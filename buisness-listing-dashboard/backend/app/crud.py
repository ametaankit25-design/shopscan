"""
crud.py
-------
Database access layer – all raw SQLAlchemy queries live here
so that routers stay thin and testable.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from sqlalchemy import distinct, func, select
from sqlalchemy.dialects.mysql import insert as mysql_insert
from sqlalchemy.orm import InstrumentedAttribute, Session
from sqlalchemy.sql.elements import ColumnElement

from app.models import Listing
from app.schemas import UNKNOWN, ListingCreate, ListingUpdate


# ──────────────────────────────────────────────────────────────────────────────
# Listing CRUD
# ──────────────────────────────────────────────────────────────────────────────

def get_listings(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    city: Optional[str] = None,
    source: Optional[str] = None,
) -> tuple[int, list[Listing]]:
    """Return (total_count, page_of_listings)."""
    stmt = select(Listing)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            Listing.business_name.ilike(pattern)
            | Listing.address.ilike(pattern)
        )
    if category:
        stmt = stmt.where(Listing.category == category)
    if city:
        stmt = stmt.where(Listing.city == city)
    if source:
        stmt = stmt.where(Listing.source == source)

    total: int = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    items = (
        db.scalars(
            stmt.order_by(Listing.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .all()
    )
    return total, list(items)


def get_listing(db: Session, listing_id: int) -> Optional[Listing]:
    """Return one listing by primary key, or None."""
    return db.get(Listing, listing_id)


def create_listing(db: Session, data: ListingCreate) -> Listing:
    """Insert one listing and return the stored row."""
    listing = Listing(**data.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def bulk_create_listings(db: Session, items: list[ListingCreate]) -> dict:
    """Bulk insert listings using MySQL INSERT IGNORE to safely skip duplicates."""
    if not items:
        return {"inserted": 0, "skipped": 0, "total_submitted": 0}

    values = [item.model_dump() for item in items]
    bind = db.get_bind()
    if bind and bind.dialect.name == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert
        result = db.execute(sqlite_insert(Listing).prefix_with("OR IGNORE").values(values))
    else:
        result = db.execute(mysql_insert(Listing).prefix_with("IGNORE").values(values))
    db.commit()
    inserted = result.rowcount if result.rowcount >= 0 else len(items)
    return {"inserted": inserted, "skipped": len(items) - inserted, "total_submitted": len(items)}


def update_listing(db: Session, listing_id: int, data: ListingUpdate) -> Optional[Listing]:
    """Apply a partial update; returns None if the listing does not exist."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


def delete_listing(db: Session, listing_id: int) -> bool:
    """Delete a listing; returns False if it did not exist."""
    listing = db.get(Listing, listing_id)
    if listing is None:
        return False
    db.delete(listing)
    db.commit()
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Stats queries
# ──────────────────────────────────────────────────────────────────────────────

def _label_or_unknown(column: InstrumentedAttribute) -> ColumnElement:
    """SQL expression: the trimmed column value, or 'Unknown' when NULL/blank."""
    return func.coalesce(func.nullif(func.trim(column), ""), UNKNOWN)


def _count_by(db: Session, column: InstrumentedAttribute, limit: Optional[int] = None) -> list[dict]:
    label = _label_or_unknown(column).label("label")
    count = func.count(Listing.id)
    stmt = select(label, count.label("count")).group_by(label).order_by(count.desc(), label)
    if limit is not None:
        stmt = stmt.limit(limit)
    return [{"label": r.label, "count": r.count} for r in db.execute(stmt).all()]


def stats_overview(db: Session) -> dict:
    """Totals: listings plus distinct cities, categories and sources ("Unknown" counts as one)."""
    total = db.scalar(select(func.count(Listing.id))) or 0
    cities = db.scalar(select(func.count(distinct(_label_or_unknown(Listing.city))))) or 0
    categories = db.scalar(select(func.count(distinct(_label_or_unknown(Listing.category))))) or 0
    sources = db.scalar(select(func.count(distinct(_label_or_unknown(Listing.source))))) or 0
    return {
        "total_listings": total,
        "total_cities": cities,
        "total_categories": categories,
        "total_sources": sources,
    }


def stats_by_category(db: Session, limit: Optional[int] = 10) -> list[dict]:
    """Listing count per category, largest first."""
    return _count_by(db, Listing.category, limit)


def stats_by_city(db: Session, limit: Optional[int] = 10) -> list[dict]:
    """Listing count per city, largest first."""
    return _count_by(db, Listing.city, limit)


def stats_by_source(db: Session) -> list[dict]:
    """Listing count per source (all sources)."""
    return _count_by(db, Listing.source)


def stats_timeline(db: Session, days: int = 30) -> list[dict]:
    """Listings added per day for the last `days` days (days with no additions are included as 0)."""
    start = date.today() - timedelta(days=days - 1)
    day = func.date(Listing.created_at).label("day")
    rows = db.execute(
        select(day, func.count(Listing.id).label("count"))
        .where(Listing.created_at >= start)
        .group_by(day)
        .order_by(day)
    ).all()
    counts = {str(r.day): r.count for r in rows}
    return [
        {"date": str(start + timedelta(days=i)), "count": counts.get(str(start + timedelta(days=i)), 0)}
        for i in range(days)
    ]


def stats_city_category(db: Session, cities: int = 8, categories: int = 6) -> dict:
    """Listing counts for the top cities broken down by the top categories (others grouped as 'Other')."""
    top_cities = [r["label"] for r in stats_by_city(db, cities)]
    top_categories = [r["label"] for r in stats_by_category(db, categories)]
    city_label = _label_or_unknown(Listing.city).label("city")
    category_label = _label_or_unknown(Listing.category).label("category")
    rows = db.execute(
        select(city_label, category_label, func.count(Listing.id).label("count"))
        .where(_label_or_unknown(Listing.city).in_(top_cities))
        .group_by(city_label, category_label)
    ).all()
    matrix: dict[str, dict[str, int]] = {c: {k: 0 for k in top_categories + ["Other"]} for c in top_cities}
    for r in rows:
        key = r.category if r.category in top_categories else "Other"
        matrix[r.city][key] += r.count
    return {
        "categories": top_categories + ["Other"],
        "rows": [{"city": c, **matrix[c], "total": sum(matrix[c].values())} for c in top_cities],
    }
