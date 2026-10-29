"""
schemas.py
----------
Pydantic v2 schemas for request validation and response serialisation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

UNKNOWN = "Unknown"


def unknown_if_blank(value: Any) -> Any:
    """Map None / empty / whitespace-only values to "Unknown"; trim strings."""
    if value is None:
        return UNKNOWN
    if isinstance(value, str):
        return value.strip() or UNKNOWN
    return value


# ──────────────────────────────────────────────────────────────────────────────
# Listing schemas
# ──────────────────────────────────────────────────────────────────────────────

class ListingBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255, examples=["Cafe Mondegar"])
    category: str = Field(UNKNOWN, max_length=150, examples=["Cafe"])
    city: str = Field(UNKNOWN, max_length=100, examples=["Mumbai"])
    address: Optional[str] = Field(None, examples=["Chhatrapati Shivaji Maharaj Road, Mumbai"])
    phone: Optional[str] = Field(None, max_length=30, examples=["+91 22 2202 0591"])
    source: str = Field(UNKNOWN, max_length=50, examples=["OpenStreetMap"])
    image_url: Optional[str] = Field(None, max_length=500)

    _normalise = field_validator("category", "city", "source", mode="before")(unknown_if_blank)


class ListingCreate(ListingBase):
    """Used for POST /listings body. Missing/blank category, city or source become "Unknown"."""


class BulkListingRequest(BaseModel):
    """Used for POST /listings/bulk when wrapped in an object."""
    listings: list[ListingCreate]


class BulkInsertResult(BaseModel):
    """Result of a bulk insert; duplicates (same name + city + source) are skipped."""
    inserted: int
    skipped: int
    total_submitted: int


class ListingUpdate(BaseModel):
    """Used for PATCH /listings/{id} body – all fields optional."""
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=150)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=30)
    source: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)

    _normalise = field_validator("category", "city", "source", mode="before")(unknown_if_blank)


class ListingOut(ListingBase):
    """Returned by GET /listings and GET /listings/{id}."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# ──────────────────────────────────────────────────────────────────────────────
# Paginated response wrapper
# ──────────────────────────────────────────────────────────────────────────────

class PaginatedListings(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ListingOut]


# ──────────────────────────────────────────────────────────────────────────────
# Stats schemas
# ──────────────────────────────────────────────────────────────────────────────

class CountItem(BaseModel):
    label: str = Field(..., examples=["Mumbai"])
    count: int = Field(..., examples=[120])


class StatsOverview(BaseModel):
    total_listings: int
    total_cities: int
    total_categories: int
    total_sources: int


class TimelinePoint(BaseModel):
    date: str = Field(..., examples=["2026-10-28"])
    count: int = Field(..., examples=[42])


class CityCategoryMatrix(BaseModel):
    """Top cities broken down by top categories; each row has one key per category plus 'city' and 'total'."""
    categories: list[str]
    rows: list[dict[str, Any]]
