from __future__ import annotations
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class RawRecord:
    source_file: str
    raw_line: str


def _iter_text_lines(file_path: Path) -> Iterable[str]:
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            yield line.strip()


def _iter_csv_lines(file_path: Path) -> Iterable[str]:
    with file_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row:
                continue
            first_cell = str(row[0]).lstrip("\ufeff").strip()
            yield first_cell


def extract_from_folder(input_dir: Path, archive_dir: Path) -> list[RawRecord]:
    input_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)

    records: list[RawRecord] = []
    files = sorted(input_dir.glob("*"))

    for file_path in files:
        if file_path.is_dir():
            continue

        ext = file_path.suffix.lower()
        if ext not in {".txt", ".csv"}:
            continue

        if ext == ".csv":
            line_iter = _iter_csv_lines(file_path)
        else:
            line_iter = _iter_text_lines(file_path)

        for line in line_iter:
            if not line:
                continue
            records.append(RawRecord(source_file=file_path.name, raw_line=line))

        archive_path = archive_dir / file_path.name
        file_path.replace(archive_path)

    return records
