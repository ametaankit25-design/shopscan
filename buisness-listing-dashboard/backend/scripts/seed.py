"""
seed.py
-------
Generates MOCK business listings with Faker for local development / demos.
Every generated row is labelled source = "Mock" so it can never be confused
with the real OpenStreetMap data collected by scripts/scrape_directory.py.

Usage (from backend/ directory with venv active):
    python scripts/seed.py              # seeds 500 mock listings (default)
    python scripts/seed.py --count 200  # custom count
    python scripts/seed.py --clear      # wipe ONLY Mock rows first, then seed

The script uses INSERT IGNORE so it's safe to run multiple times.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from faker import Faker  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.dialects.mysql import insert as mysql_insert  # noqa: E402

from app.database import SessionLocal  # noqa: E402
from app.models import Listing  # noqa: E402

fake = Faker("en_IN")   # Indian locale for more relevant business names

MOCK_SOURCE = "Mock"

CATEGORIES = [
    "Restaurant", "Cafe", "Hotel", "Retail Store", "Grocery",
    "Pharmacy", "Hospital", "Clinic", "School", "College",
    "Bank", "ATM", "Salon", "Spa", "Gym", "Bakery",
    "Electronics", "Clothing", "Furniture", "Real Estate",
    "Automobile", "Petrol Station", "Hardware", "Bookstore", "Jewellery",
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad",
    "Chennai", "Kolkata", "Pune", "Jaipur", "Lucknow",
    "Surat", "Kanpur", "Nagpur", "Indore", "Thane",
    "Bhopal", "Visakhapatnam", "Pimpri", "Patna", "Vadodara",
]

BUSINESS_SUFFIXES = [
    "Enterprises", "Solutions", "Services", "& Co.", "Pvt Ltd",
    "Associates", "Group", "Store", "Center", "Hub",
    "Works", "Traders", "Distributors", "Agency", "Shop",
]


def _fake_business_name(category: str) -> str:
    return f"{fake.last_name()} {category} {random.choice(BUSINESS_SUFFIXES)}"


def _fake_phone() -> str:
    return f"+91-{random.randint(6, 9)}{random.randint(100000000, 999999999)}"


def generate_listings(count: int) -> list[dict]:
    """Build `count` mock listing dicts, all with source = "Mock"."""
    records = []
    for _ in range(count):
        category = random.choice(CATEGORIES)
        city = random.choice(CITIES)
        records.append(
            {
                "business_name": _fake_business_name(category),
                "category": category,
                "city": city,
                "address": f"{fake.building_number()}, {fake.street_name()}, {city}",
                "phone": _fake_phone(),
                "source": MOCK_SOURCE,
            }
        )
    return records


def seed(count: int, clear: bool) -> None:
    """Insert mock listings, optionally deleting existing Mock rows first."""
    with SessionLocal() as db:
        if clear:
            db.execute(text("DELETE FROM listing_master WHERE source = :s"), {"s": MOCK_SOURCE})
            db.commit()
            print("[seed] [INFO] Existing Mock rows cleared.")

        stmt = mysql_insert(Listing).prefix_with("IGNORE").values(generate_listings(count))
        db.execute(stmt)
        db.commit()

        total = db.scalar(text("SELECT COUNT(*) FROM listing_master")) or 0
        print(f"[seed] [OK] Inserted up to {count} mock listings. Total rows now: {total}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed MOCK business listings (source='Mock')")
    parser.add_argument("--count", type=int, default=500, help="Number of listings to insert")
    parser.add_argument("--clear", action="store_true", help="Delete existing Mock rows before inserting")
    args = parser.parse_args()

    print(f"[seed] Seeding {args.count} mock listings (clear={args.clear}) ...")
    seed(args.count, args.clear)


if __name__ == "__main__":
    main()
