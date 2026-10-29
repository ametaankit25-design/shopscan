"""
routers/listings.py
-------------------
CRUD endpoints for the listing_master table.

Routes:
  GET    /listings          – paginated list with optional filters & search
  POST   /listings          – create one listing
  POST   /listings/bulk     – bulk insert, duplicates skipped
  GET    /listings/{id}     – fetch one listing
  PATCH  /listings/{id}     – partial update
  DELETE /listings/{id}     – delete
"""
from __future__ import annotations

from typing import Optional, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import (
    BulkInsertResult,
    BulkListingRequest,
    ListingCreate,
    ListingOut,
    ListingUpdate,
    PaginatedListings,
)

router = APIRouter(prefix="/listings", tags=["listings"])

NOT_FOUND = {404: {"description": "Listing not found"}}

BULK_EXAMPLE = [
    {
        "business_name": "Cafe Mondegar",
        "category": "Cafe",
        "city": "Mumbai",
        "address": "Chhatrapati Shivaji Maharaj Road, Mumbai",
        "phone": "22020591",
        "source": "OpenStreetMap",
    },
    {
        "business_name": "Good Luck Restaurant",
        "category": "Restaurant",
        "city": "Mumbai",
        "address": "M Kahn Chowk, Mumbai, 400050",
        "phone": "02226422250",
        "source": "OpenStreetMap",
    },
]


@router.get(
    "",
    response_model=PaginatedListings,
    summary="List listings",
    description="Paginated listings, newest first. Filter by exact category/city/source or search name and address.",
)
def list_listings(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Case-insensitive search on name/address"),
    category: Optional[str] = Query(None, description="Exact category, e.g. Cafe"),
    city: Optional[str] = Query(None, description="Exact city, e.g. Mumbai"),
    source: Optional[str] = Query(None, description="Exact source, e.g. OpenStreetMap or Mock"),
    db: Session = Depends(get_db),
) -> PaginatedListings:
    total, items = crud.get_listings(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        city=city,
        source=source,
    )
    return PaginatedListings(total=total, page=page, page_size=page_size, items=items)


@router.post(
    "",
    response_model=ListingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a listing",
    description="Create one listing. Missing or blank category, city or source are stored as `Unknown`.",
)
def create_listing(data: ListingCreate, db: Session = Depends(get_db)) -> ListingOut:
    return crud.create_listing(db, data)


@router.post(
    "/bulk",
    response_model=BulkInsertResult,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk insert listings",
    description=(
        "Accepts a JSON array of listings or `{\"listings\": [...]}`. Uses MySQL `INSERT IGNORE`, so rows that "
        "duplicate an existing (business_name, city, source) are skipped and reported in `skipped`; re-sending "
        "the same payload is safe."
    ),
)
def bulk_create_listings(
    payload: Union[list[ListingCreate], BulkListingRequest] = Body(..., examples=[BULK_EXAMPLE]),
    db: Session = Depends(get_db),
) -> BulkInsertResult:
    items = payload if isinstance(payload, list) else payload.listings
    return crud.bulk_create_listings(db, items)


@router.get("/{listing_id}", response_model=ListingOut, summary="Get a listing", responses=NOT_FOUND)
def get_listing(listing_id: int, db: Session = Depends(get_db)) -> ListingOut:
    listing = crud.get_listing(db, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.patch(
    "/{listing_id}",
    response_model=ListingOut,
    summary="Update a listing",
    description="Partial update: only the fields sent are changed.",
    responses=NOT_FOUND,
)
def update_listing(
    listing_id: int, data: ListingUpdate, db: Session = Depends(get_db)
) -> ListingOut:
    listing = crud.update_listing(db, listing_id, data)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.delete(
    "/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a listing",
    responses=NOT_FOUND,
)
def delete_listing(listing_id: int, db: Session = Depends(get_db)) -> Response:
    deleted = crud.delete_listing(db, listing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Listing not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
