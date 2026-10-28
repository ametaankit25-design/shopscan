"""
seed.py
-------
Generates realistic fake business listings using Faker and inserts them
into the database via SQLAlchemy.

Usage (from backend/ directory with venv active):
    python scripts/seed.py              # seeds 500 listings (default)
    python scripts/seed.py --count 200  # custom count
    python scripts/seed.py --clear      # wipe table first, then seed

The script uses INSERT IGNORE so it's safe to run multiple times.
"""
from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

# ── Bootstrap Python path & load env ─────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Listing

fake = Faker("en_IN")   # Indian locale for more relevant business names

# ── Domain data ───────────────────────────────────────────────────────────────
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

SOURCES = ["web_scraper", "manual_entry", "google_places", "justdial_import", "csv_upload"]

BUSINESS_SUFFIXES = [
    "Enterprises", "Solutions", "Services", "& Co.", "Pvt Ltd",
    "Associates", "Group", "Store", "Center", "Hub",
    "Works", "Traders", "Distributors", "Agency", "Shop",
]


def _fake_business_name(category: str) -> str:
    word = fake.last_name()
    suffix = random.choice(BUSINESS_SUFFIXES)
    return f"{word} {category} {suffix}"


def _fake_phone() -> str:
    return f"+91-{random.randint(6,9)}{random.randint(100000000, 999999999)}"


def generate_listings(count: int) -> list[dict]:
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
                "source": random.choice(SOURCES),
            }
        )
    return records


def seed(count: int, clear: bool) -> None:
    from sqlalchemy.dialects.mysql import insert as mysql_insert

    with SessionLocal() as db:
        if clear:
            db.execute(text("DELETE FROM listing_master"))
            db.commit()
            print("[seed] [INFO] Table cleared.")

        records = generate_listings(count)
        # Use INSERT IGNORE to safely skip duplicates (matches the UNIQUE key in schema)
        stmt = mysql_insert(Listing).prefix_with("IGNORE").values(records)
        db.execute(stmt)
        db.commit()

        total = db.scalar(text("SELECT COUNT(*) FROM listing_master")) or 0
        print(f"[seed] [OK] Inserted up to {count} listings. Total rows now: {total}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed fake business listings")
    parser.add_argument("--count", type=int, default=500, help="Number of listings to insert")
    parser.add_argument("--clear", action="store_true", help="Wipe the table before inserting")
    args = parser.parse_args()

    print(f"[seed] Seeding {args.count} listings (clear={args.clear}) ...")
    seed(args.count, args.clear)


if __name__ == "__main__":
    main()
