"""
schemas.py
----------
Pydantic v2 schemas for request validation and response serialisation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ──────────────────────────────────────────────────────────────────────────────
# Listing schemas
# ──────────────────────────────────────────────────────────────────────────────

class ListingBase(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=150)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=30)
    source: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)


class ListingCreate(ListingBase):
    """Used for POST /listings body."""


class BulkListingRequest(BaseModel):
    """Used for POST /listings/bulk when wrapped in an object."""
    listings: list[ListingCreate]


class ListingUpdate(BaseModel):
    """Used for PATCH /listings/{id} body – all fields optional."""
    business_name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=150)
    city: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=30)
    source: Optional[str] = Field(None, max_length=50)
    image_url: Optional[str] = Field(None, max_length=500)


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
    label: str
    count: int


class StatsOverview(BaseModel):
    total_listings: int
    total_cities: int
    total_categories: int
    total_sources: int
