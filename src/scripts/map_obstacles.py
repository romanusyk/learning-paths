import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from src.client.gemini import generate_gemini


def build_prompt(responses: List[Dict[str, str]], obstacles: List[Dict[str, str]]) -> str:
    header = (
        "You are assisting with a research on why people stop learning English. "
        "We have a curated list of common obstacles (reasons). You will map each respondent's answer to one or more of these obstacles. "
        "If a respondent explicitly denies ever stopping, return 'Never' for that respondent. Return answers in English.\n\n"
    )
    obs_text = "\n".join(
        f"- {o['obstacle']}: {o.get('explanation', '')}" for o in obstacles if o.get("obstacle")
    )
    obs_section = f"Obstacles list (canonical):\n{obs_text}\n\n"

    resp_text = "\n".join(
        f"- id={r['respondent_id']}: {r['text']}" for r in responses if r.get("text")
    )
    resp_section = f"Respondent free-text answers (only those who answered):\n{resp_text}\n\n"

    instruction = (
        "Task: For each respondent, infer zero or more obstacles from the canonical list that match their description. "
        "Use a strict subset of obstacles: only return obstacles present in the canonical list. "
        "If the text clearly says they never stopped, return a single label 'Never' instead of any obstacle. "
        "Return only JSON in the exact format described below. No commentary.\n\n"
        "Output format (JSON array):\n"
        "[ {\"respondent_id\": <number>, \"labels\": [<string>|'Never', ...] }, ... ]\n"
        "- 'labels' must be either ['Never'] or one/more obstacle names from the canonical list.\n\n"
    )
    return header + obs_section + resp_section + instruction


def main() -> int:
    parser = argparse.ArgumentParser(description="Map obstacles per respondent using Gemini")
    parser.add_argument("--input", type=Path, default=Path("data/form_data.csv"))
    parser.add_argument("--obstacles", type=Path, default=Path("data/obstacles.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/obstacles_map.json"))
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    # Collect only provided 'obstacles' answers with respondent_id
    if "respondent_id" not in df.columns:
        raise SystemExit("Column 'respondent_id' not found in input CSV")
    if "obstacles" not in df.columns:
        raise SystemExit("Column 'obstacles' not found in input CSV")

    resp = (
        df[["respondent_id", "obstacles"]]
        .dropna(subset=["obstacles"])  # responded
        .assign(obstacles=lambda d: d["obstacles"].astype(str).str.strip())
        .query("obstacles != ''")
    )
    responses: List[Dict[str, str]] = (
        resp.rename(columns={"obstacles": "text"})
        .to_dict(orient="records")
    )

    obs_df = pd.read_csv(args.obstacles)
    if "obstacle" not in obs_df.columns:
        raise SystemExit("CSV at --obstacles must include an 'obstacle' column")
    obstacles = obs_df.fillna("").to_dict(orient="records")

    prompt = build_prompt(responses, obstacles)

    schema: Dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "respondent_id": {"type": "integer"},
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["respondent_id", "labels"],
        },
    }

    # Call LLM with minor retry in case of transient issues
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
        except Exception:
            if attempt == 2:
                raise
            import time
            time.sleep(1 + attempt * 2)

    if not isinstance(result, list):
        raise SystemExit("LLM did not return an array as expected")

    # Basic normalization and validation
    cleaned: List[Dict[str, Any]] = []
    valid_obstacles = {o.get("obstacle", "").strip() for o in obstacles}
    for item in result:
        if not isinstance(item, dict):
            continue
        rid = item.get("respondent_id")
        labels = item.get("labels")
        if not isinstance(rid, (int, float)):
            continue
        rid = int(rid)
        if not isinstance(labels, list):
            continue
        norm_labels: List[str] = []
        for label in labels:
            s = str(label).strip()
            if not s:
                continue
            if s == "Never" or s in valid_obstacles:
                norm_labels.append(s)
        cleaned.append({"respondent_id": rid, "labels": norm_labels or ["Never"]})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


