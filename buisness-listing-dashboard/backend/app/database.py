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
    try:
        mysql_engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args={"connect_timeout": 2},
            echo=False,
        )
        with mysql_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Connected to MySQL database successfully.")
        return mysql_engine
    except Exception as exc:
        sqlite_file = Path(__file__).resolve().parent.parent / "listings.db"
        if sqlite_file.exists():
            logger.warning(
                "MySQL unreachable (%s). Using local SQLite fallback database at %s",
                exc,
                sqlite_file,
            )
            return create_engine(
                f"sqlite:///{sqlite_file}",
                connect_args={"check_same_thread": False},
                echo=False,
            )
        # If no SQLite file, return mysql_engine to let standard error handlers respond
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
