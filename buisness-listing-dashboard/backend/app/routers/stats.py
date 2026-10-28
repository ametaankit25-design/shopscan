"""
routers/stats.py
----------------
Aggregation / analytics endpoints consumed by the dashboard charts.

Routes:
  GET /stats/overview    – totals (listings, cities, categories, sources)
  GET /stats/category    – top-N categories by listing count
  GET /stats/city        – top-N cities by listing count
  GET /stats/source      – breakdown by source
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import CountItem, StatsOverview

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverview)
def overview(db: Session = Depends(get_db)) -> StatsOverview:
    return crud.stats_overview(db)


@router.get("/category", response_model=list[CountItem])
def by_category(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[CountItem]:
    return crud.stats_by_category(db, limit=limit)


@router.get("/city", response_model=list[CountItem])
def by_city(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[CountItem]:
    return crud.stats_by_city(db, limit=limit)


@router.get("/source", response_model=list[CountItem])
def by_source(db: Session = Depends(get_db)) -> list[CountItem]:
    return crud.stats_by_source(db)
