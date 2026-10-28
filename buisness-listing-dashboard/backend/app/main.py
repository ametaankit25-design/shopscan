"""
main.py
-------
FastAPI application entry-point.

Start with:
    cd backend
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import listings, stats

settings = get_settings()

app = FastAPI(
    title="Business Listings Dashboard API",
    version="1.0.0",
    description=(
        "REST API for the Business Listings Dashboard. "
        "Supports paginated listing queries, full CRUD, and analytics aggregations."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ─────────────────────────────────────────────────────────────────
app.include_router(listings.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}
