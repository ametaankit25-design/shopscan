"""
check_db.py
-----------
Phase-1 sanity-check script.

Connects to MySQL (via the backend .env), prints:
  • MySQL server version
  • Whether the `listing_master` table exists in `listings_db`

Run from the backend/ directory with the venv activated:
    python scripts/check_db.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import quote_plus

# ── Make sure we can import from backend/app ───────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Load backend/.env (two levels up from this file)
_env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=_env_path)


def build_url() -> str:
    """Build a SQLAlchemy URL from environment variables."""
    user = os.environ["DB_USER"]
    password = quote_plus(os.environ["DB_PASSWORD"])   # handles special chars
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "3306")
    name = os.environ["DB_NAME"]
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"


def main() -> None:
    url = build_url()
    print(f"\n[check_db] Connecting to: mysql+pymysql://***@{os.environ.get('DB_HOST','localhost')}:"
          f"{os.environ.get('DB_PORT','3306')}/{os.environ['DB_NAME']}")

    try:
        engine = create_engine(url, pool_pre_ping=True)

        with engine.connect() as conn:
            # 1. Server version
            version_row = conn.execute(text("SELECT VERSION()")).fetchone()
            version = version_row[0] if version_row else "unknown"
            print(f"[check_db] [OK] MySQL version : {version}")

            # 2. Table existence check
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if "listing_master" in tables:
                print("[check_db] [OK] Table `listing_master` EXISTS - schema applied correctly.")
            else:
                print("[check_db] [ERROR] Table `listing_master` NOT FOUND.")
                print("               -> Make sure the Docker container is healthy and")
                print("               -> schema.sql was mounted into /docker-entrypoint-initdb.d/")
                sys.exit(1)

        print("\n[check_db] [SUCCESS] Phase 1 database check PASSED. Ready for Phase 2.\n")

    except Exception as exc:  # pylint: disable=broad-except
        print(f"\n[check_db] [ERROR] Connection failed: {exc}")
        print("  Checklist:")
        print("  1. docker compose up -d   (from the project root)")
        print("  2. docker compose ps      (mysql should show 'healthy')")
        print("  3. Verify DB_* vars in backend/.env match docker-compose env")
        sys.exit(1)


if __name__ == "__main__":
    main()
