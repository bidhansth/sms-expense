from pathlib import Path
from sqlalchemy import Engine, text
from config.db import get_engine

SCHEMA_FILE = Path("./sql/create_tables.sql")

def init_db(engine: Engine, schema_file: Path) -> None:
    sql_text = schema_file.read_text(encoding="utf-8")

    with engine.begin() as conn:
        for statement in sql_text.split(";"):
            stmt = statement.strip()
            if stmt:
                conn.execute(text(stmt))


def main() -> None:
    engine = get_engine()
    init_db(engine, SCHEMA_FILE)
    print("Database schema created successfully.")


if __name__ == "__main__":
    main()
    