import os
from sqlalchemy import create_engine


def _resolve_db_url() -> str:
    # Prefer .env DATABASE_URL, else config.MYSQL_CONN
    url = os.getenv("DATABASE_URL")
    if not url:
        try:
            from config import MYSQL_CONN
            url = MYSQL_CONN
        except Exception:
            url = None

    if not url:
        raise RuntimeError("Database URL not configured. Set DATABASE_URL or config.MYSQL_CONN")

    # If env uses PyMySQL but driver is not installed, swap to mysqlconnector
    if url.startswith("mysql+pymysql://"):
        url = url.replace("mysql+pymysql://", "mysql+mysqlconnector://", 1)

    return url


# Global SQLAlchemy engine
engine = create_engine(_resolve_db_url(), pool_pre_ping=True)
