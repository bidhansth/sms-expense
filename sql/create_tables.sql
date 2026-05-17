CREATE TABLE IF NOT EXISTS raw_transactions (
    id BIGSERIAL PRIMARY KEY,
    source_file TEXT NOT NULL,
    raw_line TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id BIGSERIAL PRIMARY KEY,
    source_file TEXT NOT NULL,
    account_no TEXT,
    amount NUMERIC(12, 2),
    txn_date DATE,
    txn_time TIME,
    description TEXT,
    category TEXT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
