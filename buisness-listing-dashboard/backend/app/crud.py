"""
crud.py
-------
Database access layer – all raw SQLAlchemy queries live here
so that routers stay thin and testable.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.models import Listing
from app.schemas import ListingCreate, ListingUpdate


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
    return db.get(Listing, listing_id)


def create_listing(db: Session, data: ListingCreate) -> Listing:
    listing = Listing(**data.model_dump())
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


def bulk_create_listings(db: Session, items: list[ListingCreate]) -> dict:
    """Bulk insert listings using MySQL INSERT IGNORE to safely handle duplicates."""
    if not items:
        return {"inserted": 0, "total_submitted": 0}

    from sqlalchemy.dialects.mysql import insert as mysql_insert

    values = [item.model_dump(exclude_unset=True) for item in items]
    stmt = mysql_insert(Listing).prefix_with("IGNORE").values(values)
    result = db.execute(stmt)
    db.commit()
    return {
        "inserted": result.rowcount if result.rowcount >= 0 else len(items),
        "total_submitted": len(items),
    }


def update_listing(db: Session, listing_id: int, data: ListingUpdate) -> Optional[Listing]:
    listing = db.get(Listing, listing_id)
    if listing is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return listing


def delete_listing(db: Session, listing_id: int) -> bool:
    listing = db.get(Listing, listing_id)
    if listing is None:
        return False
    db.delete(listing)
    db.commit()
    return True


# ──────────────────────────────────────────────────────────────────────────────
# Stats queries
# ──────────────────────────────────────────────────────────────────────────────

def stats_overview(db: Session) -> dict:
    total = db.scalar(select(func.count(Listing.id))) or 0
    cities = db.scalar(select(func.count(distinct(Listing.city)))) or 0
    categories = db.scalar(select(func.count(distinct(Listing.category)))) or 0
    sources = db.scalar(select(func.count(distinct(Listing.source)))) or 0
    return {
        "total_listings": total,
        "total_cities": cities,
        "total_categories": categories,
        "total_sources": sources,
    }


def stats_by_category(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.execute(
            select(Listing.category, func.count(Listing.id).label("count"))
            .where(Listing.category.is_not(None))
            .group_by(Listing.category)
            .order_by(func.count(Listing.id).desc())
            .limit(limit)
        )
        .all()
    )
    return [{"label": r.category, "count": r.count} for r in rows]


def stats_by_city(db: Session, limit: int = 10) -> list[dict]:
    rows = (
        db.execute(
            select(Listing.city, func.count(Listing.id).label("count"))
            .where(Listing.city.is_not(None))
            .group_by(Listing.city)
            .order_by(func.count(Listing.id).desc())
            .limit(limit)
        )
        .all()
    )
    return [{"label": r.city, "count": r.count} for r in rows]


def stats_by_source(db: Session) -> list[dict]:
    rows = (
        db.execute(
            select(Listing.source, func.count(Listing.id).label("count"))
            .where(Listing.source.is_not(None))
            .group_by(Listing.source)
            .order_by(func.count(Listing.id).desc())
        )
        .all()
    )
    return [{"label": r.source, "count": r.count} for r in rows]
