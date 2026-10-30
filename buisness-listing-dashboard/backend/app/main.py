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
from app.database import get_db, engine
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


# ── Startup: Auto-seed database if empty ────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Initialize database with sample data if empty."""
    from datetime import datetime
    from app.models import Base
    
    # Log database configuration
    logger.info(f"🔌 Database Configuration:")
    logger.info(f"  - DB_HOST: {settings.DB_HOST}")
    logger.info(f"  - DB_PORT: {settings.DB_PORT}")
    logger.info(f"  - DB_NAME: {settings.DB_NAME}")
    logger.info(f"  - DB_USER: {settings.DB_USER}")
    logger.info(f"  - Using DATABASE_URL: {bool(settings.DATABASE_URL)}")
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Check if database is empty
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM listing_master")).scalar()
        logger.info(f"📊 Found {result} existing listings in database")
        
        if result == 0:
            logger.info("⚠️ Database is empty. Seeding with sample data...")
            
            # Sample listings data
            sample_data = [
                ("Good Luck Restaurant", "Restaurant", "Mumbai", "M Kahn Chowk, Mumbai, 400050", "02226422250", "OpenStreetMap"),
                ("Cafe Mondegar", "Cafe", "Mumbai", "Chhatrapati Shivaji Maharaj Road, Mumbai", "22020591", "OpenStreetMap"),
                ("Villa 39", "Restaurant", "Mumbai", "60, Madame Cama Road, Mumbai, 400039", "+91 22 6657 3939", "OpenStreetMap"),
                ("Kala Ghoda Cafe", "Cafe", "Mumbai", "10, Rope Walk Street, Mumbai, 400001", "+91 22 2265 0195", "OpenStreetMap"),
                ("The Bagel Shop", "Cafe", "Mumbai", "30, Pali Mala Road, Bandra West, Mumbai, 400050", "+91 22 2605 0178", "OpenStreetMap"),
                ("Lifeline", "Pharmacy", "Mumbai", "1, Off Yari Road, Mumbai, 400061", "+912226378686", "OpenStreetMap"),
                ("Wellness Forever", "Pharmacy", "Mumbai", "7, Central Avenue, Mumbai, 400076", "022 6162 0659", "OpenStreetMap"),
                ("Starbucks", "Cafe", "Mumbai", "Boraspada Road, Mumbai, 400067", "073044 75255", "OpenStreetMap"),
                ("Blue Tokai Coffee Roasters", "Cafe", "Mumbai", "New Kantwadi Road, Bandra West, Mumbai, 400050", "+91 90825 66400", "OpenStreetMap"),
                ("Cafe Coffee Day", "Cafe", "Mumbai", "123, Ganesh Purushottam Rd, Thane, 400605", "+91 9807965789", "OpenStreetMap"),
                ("Cafe Turtle", "Cafe", "Delhi", "Khan Market, New Delhi", "+911124655641", "OpenStreetMap"),
                ("Lama Kitchen Himalayan Cook House", "Restaurant", "Delhi", "Hauz Khas Village Road, New Delhi, 110017", "+911141008883", "OpenStreetMap"),
                ("Keshav Restaurant", "Restaurant", "Delhi", "Radial Road 6, New Delhi, 110001", "+91-90154-84272", "OpenStreetMap"),
                ("Sagar Ratna", "Restaurant", "Delhi", "15, Connaught Place, New Delhi, 110001", "+91 11 4737 7300", "OpenStreetMap"),
                ("Keventers", "Cafe", "Delhi", "GF22 Unity One, Shivaji Road, Delhi, 110058", "+91 92053 45002", "OpenStreetMap"),
                ("Apollo Pharmacy", "Pharmacy", "Delhi", "8, New Delhi", "+91 88269 92200", "OpenStreetMap"),
                ("Medicine House", "Pharmacy", "Delhi", "04, D00, New Delhi, 110001", "+91-95825-34440", "OpenStreetMap"),
                ("Blue Tokai Coffee Roasters", "Cafe", "Delhi", "Khan Market, Rabindra Nagar, New Delhi, 110003", "+91 98219 84555", "OpenStreetMap"),
                ("India Coffee House", "Cafe", "Delhi", "JNU Ring Road, Delhi, 110067", "+919013828749", "OpenStreetMap"),
                ("All India Pharmacy", "Pharmacy", "Delhi", "Lajpat Nagar 4, Delhi, 110024", "011-41038494", "OpenStreetMap"),
                ("Mavalli Tiffin Rooms", "Restaurant", "Bangalore", "14, Lalbagh Road, Bangalore, 560027", "+918022220022", "OpenStreetMap"),
                ("The Only Place", "Restaurant", "Bangalore", "13, Museum Road, Bangalore", "+91-80-32718989", "OpenStreetMap"),
                ("Ebony", "Restaurant", "Bangalore", "84, Mahatma Gandhi Road, Bangalore", "+91 8025136611", "OpenStreetMap"),
                ("Adyar Ananda Bhavan", "Restaurant", "Bangalore", "80 Feet Road, Koramangala, Bangalore, 560065", "+91 77950 73031", "OpenStreetMap"),
                ("The Cash Pharmacy", "Pharmacy", "Bangalore", "St. Marks Road, Opp Bishop Cotton Boys School", "080 3361 8456", "OpenStreetMap"),
                ("Swati Deluxe", "Restaurant", "Bangalore", "5, Modi Hospital Main Road, Bangalore, 560010", "+(91)-80-23595565", "OpenStreetMap"),
                ("Gokul Vegetarian", "Restaurant", "Bangalore", "399/34, 19th Main, Bangalore, 560010", "+91 80 2342 3955", "OpenStreetMap"),
                ("Chutney Chang", "Restaurant", "Bangalore", "Museum Road, Bangalore, 560001", "080 4000 1234", "OpenStreetMap"),
            ]
            
            # Insert sample data
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for business_name, category, city, address, phone, source in sample_data:
                conn.execute(text("""
                    INSERT INTO listing_master 
                    (business_name, category, city, address, phone, source, created_at)
                    VALUES (:name, :category, :city, :address, :phone, :source, :created_at)
                """), {
                    "name": business_name,
                    "category": category,
                    "city": city,
                    "address": address,
                    "phone": phone,
                    "source": source,
                    "created_at": now
                })
            conn.commit()
            logger.info(f"✅ Seeded database with {len(sample_data)} sample listings")
        else:
            logger.info(f"Database already has {result} listings. Skipping seed.")


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
