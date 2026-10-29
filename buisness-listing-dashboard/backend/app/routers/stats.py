"""
routers/stats.py
----------------
Aggregation / analytics endpoints consumed by the dashboard charts.
NULL or blank category / city / source values are reported as "Unknown",
so the counts of every breakdown always add up to total_listings.

Routes:
  GET /stats/overview    – totals (listings, cities, categories, sources)
  GET /stats/category    – top-N categories by listing count
  GET /stats/city        – top-N cities by listing count
  GET /stats/source      – breakdown by source
  GET /stats/timeline    – listings added per day
  GET /stats/city-category – top cities broken down by top categories
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import CityCategoryMatrix, CountItem, StatsOverview, TimelinePoint

router = APIRouter(prefix="/stats", tags=["stats"])

LIMIT_QUERY = Query(10, ge=1, le=100, description="Maximum number of groups to return (largest first)")


@router.get(
    "/overview",
    response_model=StatsOverview,
    summary="Dashboard totals",
    description="Total listings and the number of distinct cities, categories and sources.",
)
def overview(db: Session = Depends(get_db)) -> StatsOverview:
    return crud.stats_overview(db)


@router.get(
    "/category",
    response_model=list[CountItem],
    summary="Listings per category",
    description="`[{label, count}]` sorted by count descending. NULL/blank categories appear as `Unknown`.",
)
def by_category(limit: int = LIMIT_QUERY, db: Session = Depends(get_db)) -> list[CountItem]:
    return crud.stats_by_category(db, limit=limit)


@router.get(
    "/city",
    response_model=list[CountItem],
    summary="Listings per city",
    description="`[{label, count}]` sorted by count descending. NULL/blank cities appear as `Unknown`.",
)
def by_city(limit: int = LIMIT_QUERY, db: Session = Depends(get_db)) -> list[CountItem]:
    return crud.stats_by_city(db, limit=limit)


@router.get(
    "/source",
    response_model=list[CountItem],
    summary="Listings per data source",
    description=(
        "`[{label, count}]` for every source (e.g. `OpenStreetMap` for scraped rows, "
        "`Mock` for generated rows). NULL/blank sources appear as `Unknown`."
    ),
)
def by_source(db: Session = Depends(get_db)) -> list[CountItem]:
    return crud.stats_by_source(db)


@router.get(
    "/timeline",
    response_model=list[TimelinePoint],
    summary="Listings added per day",
    description=(
        "One `{date, count}` point per day for the last `days` days (default 30), oldest first, zeros included."
    ),
)
def timeline(
    days: int = Query(30, ge=7, le=365, description="Number of days to cover, ending today"),
    db: Session = Depends(get_db),
) -> list[TimelinePoint]:
    return crud.stats_timeline(db, days=days)


@router.get(
    "/city-category",
    response_model=CityCategoryMatrix,
    summary="City × category breakdown",
    description=(
        "For the top `cities`, the listing count in each of the top `categories` (remaining categories are "
        "summed under `Other`). Used for the stacked bar chart and the per-city table."
    ),
)
def city_category(
    cities: int = Query(8, ge=1, le=50),
    categories: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
) -> CityCategoryMatrix:
    return crud.stats_city_category(db, cities=cities, categories=categories)
