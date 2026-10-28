"""
routers/listings.py
-------------------
CRUD endpoints for the listing_master table.

Routes:
  GET    /listings          – paginated list with optional filters & search
  POST   /listings          – create one listing
  GET    /listings/{id}     – fetch one listing
  PATCH  /listings/{id}     – partial update
  DELETE /listings/{id}     – delete
"""
from __future__ import annotations

from typing import Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import BulkListingRequest, ListingCreate, ListingOut, ListingUpdate, PaginatedListings

router = APIRouter(prefix="/listings", tags=["listings"])


@router.get("", response_model=PaginatedListings)
def list_listings(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Full-text search on name/address"),
    category: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
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


@router.post("", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
def create_listing(data: ListingCreate, db: Session = Depends(get_db)) -> ListingOut:
    return crud.create_listing(db, data)


@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def bulk_create_listings(
    payload: Union[list[ListingCreate], BulkListingRequest],
    db: Session = Depends(get_db),
) -> dict:
    """Bulk insert listings into MySQL (accepts array or object with 'listings' key)."""
    items = payload if isinstance(payload, list) else payload.listings
    return crud.bulk_create_listings(db, items)


@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)) -> ListingOut:
    listing = crud.get_listing(db, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: int, data: ListingUpdate, db: Session = Depends(get_db)
) -> ListingOut:
    listing = crud.update_listing(db, listing_id, data)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_listing(listing_id: int, db: Session = Depends(get_db)) -> Response:
    deleted = crud.delete_listing(db, listing_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Listing not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
