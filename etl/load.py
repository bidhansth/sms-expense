from __future__ import annotations
from typing import Iterable
from sqlalchemy import text
from sqlalchemy.engine import Engine
from .extract import RawRecord
from .transform import ParsedTransaction


def load_raw(engine: Engine, records: Iterable[RawRecord]) -> int:
    records = list(records)
    if not records:
        return 0

    sql = text(
        "INSERT INTO raw_transactions (source_file, raw_line) "
        "VALUES (:source_file, :raw_line)"
    )
    payload = [
        {"source_file": r.source_file, "raw_line": r.raw_line} for r in records
    ]

    with engine.begin() as conn:
        conn.execute(sql, payload)

    return len(payload)


def load_transactions(engine: Engine, records: Iterable[ParsedTransaction]) -> int:
    records = list(records)
    if not records:
        return 0

    sql = text(
        "INSERT INTO transactions "
        "(source_file, account_no, amount, txn_date, txn_time, description, category) "
        "VALUES (:source_file, :account_no, :amount, :txn_date, :txn_time, :description, :category)"
    )
    payload = [
        {
            "source_file": r.source_file,
            "account_no": r.account_no,
            "amount": r.amount,
            "txn_date": r.txn_date,
            "txn_time": r.txn_time,
            "description": r.description,
            "category": r.category,
        }
        for r in records
    ]

    with engine.begin() as conn:
        conn.execute(sql, payload)

    return len(payload)
