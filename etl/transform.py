from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Iterable
from .extract import RawRecord


@dataclass(frozen=True)
class ParsedTransaction:
    source_file: str
    account_no: str
    amount: float
    txn_date: date
    txn_time: time
    description: str
    category: str


_NIMB_PATTERN = re.compile(
    r"AC#(?P<account>\S+)\s+"
    r"(?P<drcr>Dr|Cr)\s+by\s+NPR\s+"
    r"(?P<amount>[0-9]+(?:\.[0-9]+)?)\s+"
    r"on\s+(?P<date>\d{2}[A-Za-z]{3}\d{2})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+-\s+"
    r"(?P<desc>.+)$"
)

_PRABHU_PATTERN = re.compile(
    r"Dear\s+[^,]+,\s+NPR\s+(?P<amount>[0-9,]+(?:\.[0-9]+)?)\s+"
    r"has\s+been\s+(?P<action>withdrawn|deposited)\s+from\s+your\s+A/C\s+"
    r"(?P<account>\S+)\s+on\s+(?P<date>\d{2}/\d{2}/\d{4})\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2})\.\s+Rmk:\s+(?P<rmk>.+)$",
    re.IGNORECASE,
)


_CATEGORY_RULES: list[tuple[str, str]] = [
    ("CMPAY", "qr"),
    ("FONEPAY", "fonepay"),
    ("CASH WD", "cash_withdrawal"),
    ("ESEWA", "wallet"),
    ("PUR ", "purchase"),
]


def _normalize_line(raw_line: str) -> str:
    line = raw_line.strip()
    if line.startswith('"') and line.endswith('"'):
        line = line[1:-1]
    return line


def _parse_datetime(date_str: str, time_str: str) -> tuple[date, time]:
    dt = datetime.strptime(f"{date_str} {time_str}", "%d%b%y %H:%M:%S")
    return dt.date(), dt.time()


def _parse_datetime_slash(date_str: str, time_str: str) -> tuple[date, time]:
    dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
    return dt.date(), dt.time()


def _categorize(description: str) -> str:
    if re.match(r"^\d{9},", description.strip()):
        return "qr"

    desc_upper = description.upper()
    for token, category in _CATEGORY_RULES:
        if token in desc_upper:
            return category
    return "other"


def transform_records(records: Iterable[RawRecord]) -> list[ParsedTransaction]:
    parsed: list[ParsedTransaction] = []

    for record in records:
        line = _normalize_line(record.raw_line)
        match = _NIMB_PATTERN.match(line)
        if match:
            if match.group("drcr") != "Dr":
                continue

            account_no = match.group("account")
            amount = float(match.group("amount"))
            txn_date, txn_time = _parse_datetime(
                match.group("date"), match.group("time")
            )
            description = match.group("desc").strip()
            category = _categorize(description)
        else:
            prabhu_match = _PRABHU_PATTERN.match(line)
            if not prabhu_match:
                continue

            if prabhu_match.group("action").lower() != "withdrawn":
                continue

            account_no = prabhu_match.group("account")
            amount = float(prabhu_match.group("amount").replace(",", ""))
            txn_date, txn_time = _parse_datetime_slash(
                prabhu_match.group("date"), prabhu_match.group("time")
            )
            description = prabhu_match.group("rmk").strip()
            category = _categorize(description)

        parsed.append(
            ParsedTransaction(
                source_file=record.source_file,
                account_no=account_no,
                amount=amount,
                txn_date=txn_date,
                txn_time=txn_time,
                description=description,
                category=category,
            )
        )

    return parsed
