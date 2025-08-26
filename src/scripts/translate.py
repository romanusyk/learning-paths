import argparse
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.client.gemini import generate_gemini


def build_prompt(rows: List[Dict[str, Any]], column_name: str) -> str:
    header = (
        "You are a precise translator. Translate the following Ukrainian/Russian (or mixed) survey answers to English. "
        "Do not summarize or omit details. Preserve line breaks and punctuation. Keep neutral tone.\n\n"
    )
    task = (
        "Return strictly a JSON array of objects with fields 'respondent_id' (number) and 'translation' (string). "
        "No extra fields, no commentary. The translation should correspond exactly to each input item by id.\n\n"
    )
    intro = (
        f"Source column: '{column_name}'. Items to translate (one per line as id: text):\n"
    )
    lines = []
    for r in rows:
        rid = r.get("respondent_id")
        text = str(r.get("text", "")).strip()
        if text:
            # Guard against accidental JSON-looking constructs in the bullet list; keep it plain text
            lines.append(f"- id={rid}: {text}")
    body = "\n".join(lines) + "\n\n"
    return header + task + intro + body


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate a text column to English using Gemini")
    parser.add_argument("--input", type=Path, default=Path("data/form_data.csv"))
    parser.add_argument("--column", required=True, help="Name of the text column to translate")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output CSV path. Defaults to data/<column>_eng.csv",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    if "respondent_id" not in df.columns:
        raise SystemExit("Column 'respondent_id' not found in input CSV")
    if args.column not in df.columns:
        raise SystemExit(f"Column '{args.column}' not found in input CSV")

    series = (
        df[["respondent_id", args.column]]
        .dropna(subset=[args.column])
        .assign(**{args.column: lambda d: d[args.column].astype(str).str.strip()})
        .query(f"`{args.column}` != ''")
    )

    items: List[Dict[str, Any]] = (
        series.rename(columns={args.column: "text"}).to_dict(orient="records")
    )

    prompt = build_prompt(items, args.column)

    schema: Dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "respondent_id": {"type": "integer"},
                "translation": {"type": "string"},
            },
            "required": ["respondent_id", "translation"],
        },
    }

    # Call LLM with retries for transient issues
    result = None
    for attempt in range(3):
        try:
            result = generate_gemini(
                prompt=prompt,
                model="gemini-2.0-flash",
                structured=True,
                schema=schema,
                temperature=0.1,
            )
            break
        except Exception:
            if attempt == 2:
                raise
            import time
            time.sleep(1 + attempt * 2)

    if not isinstance(result, list):
        raise SystemExit("LLM did not return an array as expected")

    # Normalize and align results
    translations: Dict[int, str] = {}
    for item in result:
        if not isinstance(item, dict):
            continue
        rid = item.get("respondent_id")
        tr = item.get("translation")
        if isinstance(rid, (int, float)) and isinstance(tr, str):
            translations[int(rid)] = tr.strip()

    out_col = f"{args.column}_eng"
    out_rows: List[Dict[str, Any]] = []
    for r in items:
        rid = int(r["respondent_id"])  # guaranteed present from selection above
        eng = translations.get(rid, "")
        out_rows.append({"respondent_id": rid, out_col: eng})

    out_df = pd.DataFrame(out_rows, columns=["respondent_id", out_col])

    output_path = args.output or Path("data") / f"{args.column}_eng.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(output_path, index=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


