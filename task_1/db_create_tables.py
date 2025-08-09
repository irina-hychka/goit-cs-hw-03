"""
Create core database tables for the task manager service.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Sequence

from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection as PGConnection

# Load .env from current working directory (if present)
load_dotenv()

# SQL DDL statements kept separate for readability and reuse
DDL_STATEMENTS: Sequence[str] = (
    """
    CREATE TABLE IF NOT EXISTS users (
        id        SERIAL PRIMARY KEY,
        fullname  VARCHAR(100) NOT NULL,
        email     VARCHAR(100) UNIQUE NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS status (
        id   SERIAL PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS tasks (
        id          SERIAL PRIMARY KEY,
        title       VARCHAR(100) NOT NULL,
        description TEXT,
        status_id   INTEGER REFERENCES status (id),
        user_id     INTEGER REFERENCES users (id) ON DELETE CASCADE
    );
    """,
)


def get_db_connection() -> PGConnection:
    """
    Create a PostgreSQL connection using environment variables.
    Requires DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT to be set.
    """
    return psycopg2.connect(
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
    )


def create_tables(
    conn: PGConnection, statements: Sequence[str] = DDL_STATEMENTS
) -> None:
    """
    Create required tables if they do not already exist.

    :param conn: An open psycopg2 connection.
    :param statements: A sequence of DDL statements to execute.
    """
    # Use a cursor context manager to ensure it is closed automatically
    with conn.cursor() as cur:
        for ddl in statements:
            cur.execute(ddl)
    # Explicit commit so changes are persisted
    conn.commit()


def main() -> int:
    """
    Entry point for running the table creation script.
    Returns process exit code (0 on success).
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    try:
        with get_db_connection() as conn:
            create_tables(conn)
            logging.info("Tables created successfully (or already existed).")
        return 0
    except (Exception, psycopg2.DatabaseError) as exc:
        logging.error("Failed to create tables: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
