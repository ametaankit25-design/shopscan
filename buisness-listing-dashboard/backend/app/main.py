"""
main.py
-------
FastAPI application entry-point.

Start with:
    cd backend
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.routers import listings, stats

logger = logging.getLogger("listings_api")
settings = get_settings()

app = FastAPI(
    title="Business Listings Dashboard API",
    version="1.0.0",
    description=(
        "REST API for the Business Listings Dashboard. "
        "Supports paginated listing queries, full CRUD, bulk import and analytics aggregations. "
        "Returns 422 for invalid input, 404 for unknown ids and 503 when MySQL is unreachable."
    ),
    openapi_tags=[
        {"name": "listings", "description": "Create, read, update, delete and bulk-import business listings."},
        {"name": "stats", "description": "Aggregations used by the dashboard charts."},
        {"name": "health", "description": "Liveness and database connectivity check."},
    ],
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Database error handling ─────────────────────────────────────────────────
@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError) -> JSONResponse:
    logger.error("Database unavailable on %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable. Make sure the MySQL container is running."},
    )


@app.exception_handler(SQLAlchemyError)
async def database_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Database error while processing the request."})


# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(listings.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


# ── Health check ─────────────────────────────────────────────────────────────
@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Returns 200 when the API and MySQL are both reachable, 503 if the database is down.",
    responses={503: {"description": "Database unavailable"}},
)
def health(db: Session = Depends(get_db)) -> JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(status_code=503, content={"status": "degraded", "database": "unavailable"})
    return JSONResponse(content={"status": "ok", "database": "ok"})
