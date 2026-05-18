# SMS Expense ETL

A small ETL that reads SMS transaction alerts from .txt or .csv files, loads raw lines into Postgres, parses expense transactions, and stores structured rows with a simple category.

## Features
- Extract from a folder containing .txt or .csv files
- Load raw lines into `raw_transactions`
- Parse Dr-only transactions into `transactions`
- Simple keyword and pattern-based categorization (QR, wallets)
- Uses SQLAlchemy with psycopg
- Streamlit reports (monthly/weekly trends, category breakdowns, top amounts)

## Project structure
- config/db.py: database connection helpers
- etl/extract.py: read files and move them to archive
- etl/transform.py: parse lines + categorize
- etl/load.py: load raw and parsed rows
- sql/create_tables.sql: table DDL
- scripts/init_db.py: run DDL
- run_etl.py: entry point
- app.py: Streamlit dashboard

## Setup
1. Create and activate a virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Create a .env file:
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=sms_expense
   DB_USER=postgres
   DB_PASSWORD=postgres

## Initialize database
Run the DDL once:
   python -m scripts.init_db

## Run ETL
1. Put your input files in `./data/input` (supports `.txt` and `.csv`)
2. Run:
   python run_etl.py

Processed files are moved to ./data/archive after being read.

## Streamlit dashboard
A small dashboard is included for quick reporting and exploration.

Available reports
- Monthly spend (line chart)
- Weekly spend (line chart)
- Most popular category by count (bar chart)
- Most popular category by amount (bar chart)
- Top 3 months by total amount (table)
- Transactions for the top months (table)
- Top 3 amounts per category (table)
- Top 3 amounts for a selected month (selects the latest month by default)

Run the dashboard locally:
streamlit run app.py

Notes
- The dashboard reads from the `transactions` table using `config/db.py`.
- Filters: date range and category selection are available in the UI.

## Input format
The parser expects lines like:
AC#040XX0931 Dr by NPR 2000 on 06Dec25 16:08:58 - CASH WD NIMB CEDAR G

It also supports quoted lines and CSV files where the first column is the full line. CSV files are read with `utf-8-sig` to handle BOMs.

## Categorization rules
- QR pattern: descriptions like `668929706,abcde,102` are labeled as `qr`
- Keyword rules: `CASH WD`, `ESEWA`, `PUR`, etc.
- Bank-specific parsers: NMB/Prabhu message formats are supported for withdrawal parsing
- Otherwise: `other`

## Notes
- Only Dr (debit/withdrawal) transactions are loaded; Cr lines are ignored.
- There is no deduplication logic.
