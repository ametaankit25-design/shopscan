"""
database.py
-----------
SQLAlchemy engine + session factory.
Provides get_db() FastAPI dependency for route handlers.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_engine():
    # 1. Try MySQL first
    db_url = settings.final_database_url
    connect_args = {"connect_timeout": 5}
    
    # Log connection attempt (without exposing password)
    safe_url = db_url.split('@')[-1] if '@' in db_url else db_url
    logger.info(f"🔌 Attempting database connection to: {safe_url}")
    
    if "tidbcloud" in db_url.lower() or "aivencloud" in db_url.lower() or "ssl" in db_url.lower():
        connect_args["ssl"] = {"check_hostname": False}
        logger.info("🔒 SSL mode enabled for cloud database")

    try:
        mysql_engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args=connect_args,
            echo=False,
        )
        with mysql_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Connected to MySQL database successfully.")
        return mysql_engine
    except Exception as exc:
        logger.error(f"❌ MySQL connection failed: {exc}")
        sqlite_file = Path(__file__).resolve().parent.parent / "listings.db"
        if sqlite_file.exists():
            logger.warning(
                "⚠️ MySQL unreachable (%s). Using local SQLite fallback database at %s",
                exc,
                sqlite_file,
            )
            return create_engine(
                f"sqlite:///{sqlite_file}",
                connect_args={"check_same_thread": False},
                echo=False,
            )
        # If no SQLite file, return mysql_engine to let standard error handlers respond
        logger.error("❌ No SQLite fallback available. Application may fail.")
        return mysql_engine


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a DB session and always closes it."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
