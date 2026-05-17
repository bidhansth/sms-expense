import os
from pathlib import Path

from config.db import get_engine
from etl.extract import extract_from_folder
from etl.load import load_raw, load_transactions
from etl.transform import transform_records

INPUT_DIR = Path("./data/input")
ARCHIVE_DIR = Path("./data/archive")

def main() -> None:
    raw_records = extract_from_folder(INPUT_DIR, ARCHIVE_DIR)
    if not raw_records:
        print("No input files found.")
        return

    engine = get_engine()
    raw_count = load_raw(engine, raw_records)
    parsed_records = transform_records(raw_records)
    parsed_count = load_transactions(engine, parsed_records)

    print(f"Loaded raw rows: {raw_count}")
    print(f"Loaded parsed rows: {parsed_count}")


if __name__ == "__main__":
    main()
