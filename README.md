# SMS Expense ETL

A small ETL that reads SMS transaction alerts from .txt or .csv files, loads raw lines into Postgres, parses expense transactions, and stores structured rows with a simple category.

## Features
- Extract from a folder containing .txt or .csv files
- Load raw lines into `raw_transactions`
- Parse Dr-only transactions into `transactions`
- Simple keyword-based category
- Uses SQLAlchemy with psycopg

## Project structure
- config/db.py: database connection helpers
- etl/extract.py: read files and move them to archive
- etl/transform.py: parse lines + categorize
- etl/load.py: load raw and parsed rows
- sql/create_tables.sql: table DDL
- scripts/init_db.py: run DDL
- run_etl.py: entry point

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
1. Put your input files in ./data/input
2. Run:
   python run_etl.py

Processed files are moved to ./data/archive after being read.

## Input format
The parser expects lines like:
AC#040XX0931 Dr by NPR 2000 on 06Dec25 16:08:58 - CASH WD NIMB CEDAR G

It also supports quoted lines and CSV files where the first column is the full line.

## Categorization rules
- QR pattern: descriptions like 668929706,abcde,102 are labeled as `qr`
- Keyword rules: CASH WD, ESEWA, PUR
- Otherwise: other

## Notes
- Only Dr transactions are loaded; Cr lines are ignored.
- There is no deduplication logic.
