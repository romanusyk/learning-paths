import argparse
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.client.gemini import generate_gemini


def build_prompt(responses: List[str], min_mentions: int) -> str:
    header = (
        "You are assisting with a small research about why people stop learning English. "
        "We collected survey responses from IT professionals. "
        "Below are ONLY the answers from respondents who answered the 'obstacles' question: "
        "'Have you ever stopped learning English at least once? If yes, describe the main reasons.'\n\n"
    )
    instruction = (
        f"Task: Extract a consolidated list of obstacles (reasons to stop learning English) that are mentioned by at least {min_mentions} different people. "
        "Cluster or deduplicate similar phrasings into a single obstacle. Each obstacle should be concise (one to a few words). "
        "For each obstacle, provide a short explanation (one sentence) that clarifies what the obstacle means. "
        "Return your answer in English."
    )
    formatting = (
        "\nReturn only a JSON array of objects with the following fields: "
        "'obstacle' (string) and 'explanation' (string). No extra fields. No preface or commentary.\n\n"
        "Example (schema only, not actual content):\n"
        "[ {\"obstacle\": \"Lack of time\", \"explanation\": \"The person cannot allocate time to study.\"} ]\n\n"
    )
    bullets = "\n".join(f"- {text.strip()}" for text in responses if text and text.strip())
    body = f"Responses (one per line):\n{bullets}\n\n"
    return header + instruction + formatting + body


def main() -> int:
    parser = argparse.ArgumentParser(description="List obstacles using Gemini")
    parser.add_argument("--input", type=Path, default=Path("data/form_data.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/obstacles.csv"))
    parser.add_argument("--min-mentions", type=int, default=2)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    series = df.get("obstacles")
    if series is None:
        raise SystemExit("Column 'obstacles' not found in input CSV")

    responses = (
        series.dropna().astype(str).map(lambda s: s.strip()).loc[lambda s: s.ne("")].tolist()
    )

    prompt = build_prompt(responses, args.min_mentions)

    schema: Dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "obstacle": {"type": "string"},
                "explanation": {"type": "string"},
            },
            "required": ["obstacle", "explanation"],
        },
    }

    # Call LLM with simple retries for transient errors
    result = None
    for attempt in range(3):
        try:
            result = generate_gemini(
                prompt=prompt,
                model="gemini-2.5-pro",
                structured=True,
                schema=schema,
                temperature=0.2,
            )
            break
        except Exception as e:
            if attempt == 2:
                raise
            import time
            time.sleep(1 + attempt * 2)

    if not isinstance(result, list):
        raise SystemExit("LLM did not return an array as expected")

    # Normalize and persist
    rows: List[Dict[str, str]] = []
    for item in result:
        if not isinstance(item, dict):
            continue
        obstacle = str(item.get("obstacle", "")).strip()
        explanation = str(item.get("explanation", "")).strip()
        if obstacle:
            rows.append({"obstacle": obstacle, "explanation": explanation})

    out_df = pd.DataFrame(rows, columns=["obstacle", "explanation"])  # preserve order
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.output, index=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


