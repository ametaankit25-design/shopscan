"""
scrape_directory.py
-------------------
Data collection for Part 1 of the assignment.

Collects REAL business listings from OpenStreetMap through the public
Overpass API and stores them in `listing_master` with source = "OpenStreetMap".
Each record has: business_name, category, city, address, phone, source.

Ethics / ToS compliance:
  - robots.txt is checked for every endpoint (urllib.robotparser); an endpoint
    whose robots.txt disallows the API path is skipped, never forced.
  - One honest, identifying User-Agent (no rotation, no browser impersonation).
  - Polite delay between requests (--delay, default 5 s) and a request timeout.
  - HTTP 429/5xx get a short back-off retry; 403/CAPTCHA/blocked responses are
    NOT worked around - that endpoint is abandoned.
  - Records missing a name, phone or address are skipped (no invented values).
  - Data (c) OpenStreetMap contributors, licensed under the ODbL.

Usage (from backend/ with the venv active and MySQL running):
  python scripts/scrape_directory.py                    # all cities, 80 per city
  python scripts/scrape_directory.py --cities Mumbai Pune --per-city 50
  python scripts/scrape_directory.py --dry-run          # fetch + print, no DB writes
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional
from urllib import robotparser
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import requests  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

SOURCE_LABEL = "OpenStreetMap"
USER_AGENT = "BusinessListingsDashboard/1.0 (internship assignment; data collection for a student project)"
REQUEST_TIMEOUT = 75
MAX_RETRIES = 1

OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

# (south, west, north, east) bounding boxes of the city cores.
CITY_BBOXES: dict[str, tuple[float, float, float, float]] = {
    "Mumbai": (18.89, 72.77, 19.27, 72.99),
    "Delhi": (28.50, 77.05, 28.75, 77.35),
    "Bangalore": (12.85, 77.45, 13.10, 77.75),
    "Hyderabad": (17.30, 78.35, 17.50, 78.60),
    "Chennai": (12.95, 80.15, 13.15, 80.30),
    "Kolkata": (22.48, 88.28, 22.65, 88.43),
    "Pune": (18.45, 73.75, 18.62, 73.97),
    "Ahmedabad": (22.95, 72.48, 23.10, 72.65),
    "Jaipur": (26.82, 75.72, 26.98, 75.88),
    "Lucknow": (26.78, 80.88, 26.92, 81.02),
}

# OSM tag (key, value) -> dashboard category
TAG_CATEGORIES: dict[tuple[str, str], str] = {
    ("amenity", "restaurant"): "Restaurant",
    ("amenity", "cafe"): "Cafe",
    ("tourism", "hotel"): "Hotel",
    ("shop", "department_store"): "Retail Store",
    ("shop", "variety_store"): "Retail Store",
    ("shop", "supermarket"): "Grocery",
    ("shop", "convenience"): "Grocery",
    ("amenity", "pharmacy"): "Pharmacy",
    ("shop", "chemist"): "Pharmacy",
    ("amenity", "hospital"): "Hospital",
    ("amenity", "clinic"): "Clinic",
    ("amenity", "doctors"): "Clinic",
    ("amenity", "school"): "School",
    ("amenity", "college"): "College",
    ("amenity", "university"): "College",
    ("amenity", "bank"): "Bank",
    ("shop", "hairdresser"): "Salon",
    ("shop", "beauty"): "Salon",
    ("leisure", "fitness_centre"): "Gym",
    ("shop", "bakery"): "Bakery",
    ("shop", "electronics"): "Electronics",
    ("shop", "mobile_phone"): "Electronics",
    ("shop", "clothes"): "Clothing",
    ("shop", "furniture"): "Furniture",
    ("office", "estate_agent"): "Real Estate",
    ("shop", "car"): "Automobile",
    ("shop", "car_repair"): "Automobile",
    ("amenity", "fuel"): "Petrol Station",
    ("shop", "hardware"): "Hardware",
    ("shop", "books"): "Bookstore",
    ("shop", "jewelry"): "Jewellery",
}

_robots_cache: dict[str, Optional[robotparser.RobotFileParser]] = {}


def is_allowed_by_robots(url: str) -> bool:
    """Return True only if the host's robots.txt permits USER_AGENT to fetch `url`."""
    parts = urlsplit(url)
    host = f"{parts.scheme}://{parts.netloc}"
    if host not in _robots_cache:
        parser: Optional[robotparser.RobotFileParser] = robotparser.RobotFileParser()
        try:
            resp = requests.get(f"{host}/robots.txt", headers={"User-Agent": USER_AGENT}, timeout=20)
            if resp.status_code == 200:
                parser.parse(resp.text.splitlines())
            elif resp.status_code in (401, 403):
                parser.disallow_all = True
            else:  # 404 etc. -> no robots.txt -> allowed
                parser.allow_all = True
        except requests.RequestException as exc:
            print(f"[scraper] Could not read {host}/robots.txt ({exc}); skipping this host.")
            parser = None
        _robots_cache[host] = parser
    parser = _robots_cache[host]
    return parser is not None and parser.can_fetch(USER_AGENT, url)


def query_groups(chunk: int = 3) -> list[tuple[str, list[str]]]:
    """Split TAG_CATEGORIES into small (key, values) groups so each Overpass query stays light."""
    grouped: dict[str, list[str]] = {}
    for key, value in TAG_CATEGORIES:
        grouped.setdefault(key, []).append(value)
    return [
        (key, values[i:i + chunk])
        for key, values in grouped.items()
        for i in range(0, len(values), chunk)
    ]


def build_query(bbox: tuple[float, float, float, float], key: str, values: list[str]) -> str:
    """Overpass QL: named nodes/ways with a phone number and key=value inside `bbox`."""
    s, w, n, e = bbox
    return (
        "[out:json][timeout:60];\n"
        f'nw["{key}"~"^({"|".join(values)})$"]["name"]["phone"]({s},{w},{n},{e});\n'
        "out center tags;"
    )


def fetch_overpass(query: str, delay: float) -> Optional[list[dict]]:
    """POST `query` to the first robots-permitted endpoint that answers. Returns elements or None."""
    for endpoint in OVERPASS_ENDPOINTS:
        if not is_allowed_by_robots(endpoint):
            print(f"[scraper] robots.txt disallows {endpoint}; skipping.")
            continue
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = requests.post(
                    endpoint,
                    data={"data": query},
                    headers={"User-Agent": USER_AGENT},
                    timeout=REQUEST_TIMEOUT,
                )
            except requests.RequestException as exc:
                print(f"[scraper] {endpoint} attempt {attempt} failed: {exc}")
                time.sleep(delay * attempt)
                continue
            if resp.status_code == 200:
                try:
                    return resp.json().get("elements", [])
                except ValueError:
                    print(f"[scraper] {endpoint} returned non-JSON; skipping.")
                    break
            if resp.status_code in (429, 502, 503, 504):
                print(f"[scraper] {endpoint} busy (HTTP {resp.status_code}); backing off.")
                time.sleep(delay * attempt * 2)
                continue
            print(f"[scraper] {endpoint} refused (HTTP {resp.status_code}); not retrying.")
            break
    return None


def _clean(value: Optional[str], max_len: int) -> Optional[str]:
    if not value:
        return None
    value = " ".join(value.split())
    return value[:max_len] if value else None


def element_to_listing(element: dict, city: str) -> Optional[dict]:
    """Map one OSM element to a listing dict; None if a required field is missing."""
    tags: dict = element.get("tags", {})
    name = _clean(tags.get("name:en") or tags.get("name"), 255)
    phone_raw = tags.get("phone") or tags.get("contact:phone")
    phone = _clean(phone_raw.split(";")[0] if phone_raw else None, 30)
    category = next(
        (label for (key, value), label in TAG_CATEGORIES.items() if tags.get(key) == value),
        None,
    )
    address = _clean(tags.get("addr:full"), 1000)
    if not address:
        parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb") or tags.get("addr:neighbourhood"),
            tags.get("addr:city") or city,
            tags.get("addr:postcode"),
        ]
        has_locality = any(tags.get(k) for k in ("addr:street", "addr:suburb", "addr:neighbourhood", "addr:place"))
        address = _clean(", ".join(p for p in parts if p), 1000) if has_locality else None
    if not (name and phone and category and address):
        return None
    return {
        "business_name": name,
        "category": category,
        "city": city,
        "address": address,
        "phone": phone,
        "source": SOURCE_LABEL,
    }


def collect_city(city: str, per_city: int, delay: float) -> list[dict]:
    """Fetch and clean up to `per_city` listings for one city (one polite request per OSM key)."""
    seen: set[str] = set()
    listings: list[dict] = []
    raw = skipped = 0
    for i, (key, values) in enumerate(query_groups()):
        if len(listings) >= per_city:
            break
        if i:
            time.sleep(delay)
        batch = fetch_overpass(build_query(CITY_BBOXES[city], key, values), delay)
        if batch is None:
            print(f"[scraper] {city}/{key}: no endpoint available, skipped.")
            continue
        raw += len(batch)
        for element in batch:
            listing = element_to_listing(element, city)
            if listing is None:
                skipped += 1
                continue
            name_key = listing["business_name"].lower()
            if name_key in seen:
                continue
            seen.add(name_key)
            listings.append(listing)
            if len(listings) >= per_city:
                break
    print(f"[scraper] {city}: {raw} raw, {skipped} skipped (missing fields), {len(listings)} kept.")
    return listings


def store_listings(listings: list[dict]) -> int:
    """INSERT IGNORE into listing_master; returns the number of new rows."""
    if not listings:
        return 0
    from sqlalchemy.dialects.mysql import insert as mysql_insert

    from app.database import SessionLocal
    from app.models import Listing

    with SessionLocal() as db:
        result = db.execute(mysql_insert(Listing).prefix_with("IGNORE").values(listings))
        db.commit()
        return max(result.rowcount, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect real business listings from OpenStreetMap")
    parser.add_argument("--cities", nargs="*", default=list(CITY_BBOXES), choices=list(CITY_BBOXES))
    parser.add_argument("--per-city", type=int, default=80, help="Max listings kept per city (default 80)")
    parser.add_argument("--delay", type=float, default=5.0, help="Seconds between requests (default 5)")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and print, do not write to MySQL")
    args = parser.parse_args()

    print("[scraper] Source: OpenStreetMap via Overpass API (data (c) OpenStreetMap contributors, ODbL)")
    total_kept = total_inserted = 0
    for i, city in enumerate(args.cities):
        if i:
            time.sleep(args.delay)
        listings = collect_city(city, args.per_city, args.delay)
        total_kept += len(listings)
        if args.dry_run:
            for row in listings[:3]:
                print("   ", row)
            continue
        inserted = store_listings(listings)
        total_inserted += inserted
        print(f"[scraper] {city}: inserted {inserted} new rows ({len(listings) - inserted} duplicates ignored).")

    print(f"[scraper] Done. Kept {total_kept} listings, inserted {total_inserted} new rows.")


if __name__ == "__main__":
    main()
