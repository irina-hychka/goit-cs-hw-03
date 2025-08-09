"""
Seed script for PostgreSQL task manager schema.

- Inserts default statuses (idempotent).
- Generates fake users (unique emails; idempotent).
- Generates fake tasks linked to random users and statuses.

Configuration (via .env or environment):
  Either:
    DATABASE_URL = postgresql://USER:PASSWORD@HOST:PORT/DBNAME
  Or all of:
    PG_DB, PG_USER, PG_PASSWORD, PG_HOST, [PG_PORT=5432]

Optional:
  SEED_USERS  (default 10)
  SEED_TASKS  (default 30)
"""

import logging
import os
import random
import time
from typing import Optional, Sequence
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv
from faker import Faker
from psycopg2.extensions import connection as PGConnection
from psycopg2.extras import execute_batch

# ----- Load config & logging -----
load_dotenv()  # read .env from CWD if present

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

fake = Faker()

SEED_USERS = int(os.getenv("SEED_USERS", "10"))
SEED_TASKS = int(os.getenv("SEED_TASKS", "30"))

# ----- Helpers -----
def _parse_db_env() -> dict:
    """Return connection kwargs from env. Prefer DATABASE_URL if provided."""
    if url := os.getenv("DATABASE_URL"):
        parsed = urlparse(url)
        if parsed.scheme not in ("postgres", "postgresql", "postgresql+psycopg2"):
            raise ValueError(f"Unsupported scheme in DATABASE_URL: {parsed.scheme}")
        return dict(
            dbname=parsed.path.lstrip("/"),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
        )

    # No defaults here on purpose: misconfig should be visible.
    required = ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST")
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(
            f"Missing required env vars: {', '.join(missing)} "
            "(or provide DATABASE_URL)"
        )

    return dict(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
    )


def get_connection(max_wait_seconds: int = 30) -> PGConnection:
    """
    Connect to PostgreSQL with small retry loop (useful when DB is booting).
    """
    cfg = _parse_db_env()
    deadline = time.time() + max_wait_seconds
    attempt = 0
    last_err: Optional[Exception] = None

    while time.time() < deadline:
        attempt += 1
        try:
            conn = psycopg2.connect(**cfg)
            conn.autocommit = False
            logging.info("Connected to DB on attempt %d.", attempt)
            return conn
        except Exception as exc:
            last_err = exc
            logging.warning("DB not ready (attempt %d): %s", attempt, exc)
            time.sleep(1.5)

    # If we’re here — all attempts failed.
    raise ConnectionError(f"Could not connect to DB within timeout: {last_err}")


# ----- SQL -----
SQL_INSERT_STATUSES = """
INSERT INTO status (name)
VALUES (%s)
ON CONFLICT (name) DO NOTHING;
"""

SQL_INSERT_USER = """
INSERT INTO users (fullname, email)
VALUES (%s, %s)
ON CONFLICT (email) DO NOTHING;
"""

SQL_SELECT_USER_IDS = "SELECT id FROM users;"
SQL_SELECT_STATUS_IDS = "SELECT id FROM status;"

SQL_INSERT_TASK = """
INSERT INTO tasks (title, description, status_id, user_id)
VALUES (%s, %s, %s, %s);
"""

# ----- Seeding routines -----
def seed_statuses(conn: PGConnection) -> None:
    """Insert default statuses (idempotent)."""
    statuses: Sequence[tuple[str]] = [("new",), ("in progress",), ("completed",)]
    with conn.cursor() as cur:
        execute_batch(cur, SQL_INSERT_STATUSES, statuses, page_size=50)
    logging.info("Statuses upserted.")


def seed_users(conn: PGConnection, count: int) -> None:
    """Insert fake users (emails unique; idempotent on conflict)."""
    users = [(fake.name(), fake.unique.email()) for _ in range(count)]
    fake.unique.clear()  # reset Faker uniqueness cache
    with conn.cursor() as cur:
        execute_batch(cur, SQL_INSERT_USER, users, page_size=200)
    logging.info("Users inserted/skipped: %d", count)


def seed_tasks(conn: PGConnection, count: int) -> None:
    """Insert fake tasks mapped to random existing users & statuses."""
    with conn.cursor() as cur:
        cur.execute(SQL_SELECT_USER_IDS)
        user_ids = [r[0] for r in cur.fetchall()]
        cur.execute(SQL_SELECT_STATUS_IDS)
        status_ids = [r[0] for r in cur.fetchall()]

    if not user_ids or not status_ids:
        logging.warning("Skip tasks seeding: missing users or statuses.")
        return

    tasks = [
        (
            fake.sentence(nb_words=4),
            fake.text(),
            random.choice(status_ids),
            random.choice(user_ids),
        )
        for _ in range(count)
    ]
    with conn.cursor() as cur:
        execute_batch(cur, SQL_INSERT_TASK, tasks, page_size=500)
    logging.info("Tasks inserted: %d", count)


# ----- Entry point -----
def main() -> None:
    """Run all seeding steps in a single transaction."""
    conn: Optional[PGConnection] = None
    try:
        conn = get_connection()
        with conn:
            seed_statuses(conn)
            seed_users(conn, SEED_USERS)
            seed_tasks(conn, SEED_TASKS)
        logging.info("Seeding completed successfully.")
    except Exception as exc:
        logging.exception("Seeding failed: %s", exc)
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
        logging.info("DB connection closed.")


if __name__ == "__main__":
    main()
