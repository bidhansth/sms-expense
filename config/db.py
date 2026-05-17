from os import getenv
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

load_dotenv()

def get_database_url() -> str:
    host = getenv("DB_HOST", "localhost")
    port = getenv("DB_PORT", "5432")
    name = getenv("DB_NAME")
    user = getenv("DB_USER")
    password = getenv("DB_PASSWORD")

    if not all([name, user, password]):
        raise ValueError("Database credentials are not fully configured in .env")

    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"


def get_engine() -> Engine:
    return create_engine(get_database_url(), future=True, pool_pre_ping=True)
