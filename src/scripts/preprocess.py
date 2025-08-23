import argparse
from pathlib import Path
import sys

import pandas as pd

from src.common.column import (
    columns,
    col_mapping,
    motives_col_names,
    method_effectiveness_col_names,
    MOTIVES_MAPPING,
    METHOD_EFFECTIVENESS_MAPPING,
    all_col_names,
)


def preprocess(input_csv: Path, output_csv: Path) -> None:
    # Read raw CSV
    df_raw = pd.read_csv(input_csv)

    # Drop PII and administrative columns early if present
    drop_candidates = [
        "Позначка часу",  # timestamp
        "Електронна адреса",  # email
        "Імʼя",  # first name
        "Прізвище",  # last name
    ]
    existing_drops = [c for c in drop_candidates if c in df_raw.columns]
    if existing_drops:
        df_raw = df_raw.drop(columns=existing_drops)

    # Add respondent_id as sequential index starting from 1
    df_raw.insert(0, "respondent_id", range(1, len(df_raw) + 1))

    # Rename columns from raw Ukrainian names to canonical names
    df = df_raw.rename(columns=col_mapping)

    # Keep only defined columns plus respondent_id
    keep_cols = ["respondent_id"] + all_col_names
    existing_keep_cols = [c for c in keep_cols if c in df.columns]
    df = df[existing_keep_cols]

    # Likert mappings
    for col_name in motives_col_names:
        if col_name in df.columns:
            df[col_name] = df[col_name].replace(MOTIVES_MAPPING)

    for col_name in method_effectiveness_col_names:
        if col_name in df.columns:
            df[col_name] = df[col_name].replace(METHOD_EFFECTIVENESS_MAPPING)

    # Persist
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Preprocess raw form data CSV")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/form_data_raw.csv"),
        help="Path to raw CSV (default: data/form_data_raw.csv)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/form_data.csv"),
        help="Path to output CSV (default: data/form_data.csv)",
    )

    args = parser.parse_args(argv)
    preprocess(args.input, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))


