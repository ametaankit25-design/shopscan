"""
models.py
---------
SQLAlchemy ORM model that mirrors the `listing_master` table defined in
database/schema.sql.  No auto-migration is used; the table is created by
Docker's init script on first start.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Listing(Base):
    __tablename__ = "listing_master"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    business_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(150), nullable=False, server_default="Unknown")
    city: Mapped[str] = mapped_column(String(100), nullable=False, server_default="Unknown")
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, server_default="Unknown")
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    __table_args__ = (
        Index("idx_category", "category"),
        Index("idx_city", "city"),
        Index("idx_source", "source"),
    )

    def __repr__(self) -> str:
        return f"<Listing id={self.id} name={self.business_name!r} city={self.city!r}>"
