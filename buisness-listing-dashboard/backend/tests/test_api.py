"""
API tests. They run against the real MySQL database, so start it first:
    docker compose up -d          (project root)
    cd backend && python -m pytest
Every row a test creates is prefixed with a unique tag and deleted afterwards.
"""
from __future__ import annotations

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database import SessionLocal, get_db
from app.main import app

client = TestClient(app)
PREFIX = f"pytest-{uuid.uuid4().hex[:8]}"


@pytest.fixture(autouse=True)
def delete_test_rows() -> Iterator[None]:
    yield
    with SessionLocal() as db:
        db.execute(text("DELETE FROM listing_master WHERE business_name LIKE :p"), {"p": f"{PREFIX}%"})
        db.commit()


def make_rows(n: int) -> list[dict]:
    return [
        {
            "business_name": f"{PREFIX} Shop {i}",
            "category": "Cafe",
            "city": "Mumbai",
            "address": "1 Test Road, Mumbai",
            "phone": "+91-9000000000",
            "source": "pytest",
        }
        for i in range(n)
    ]


def test_health_reports_database_ok() -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "database": "ok"}


def test_bulk_insert_skips_duplicates() -> None:
    rows = make_rows(2)
    first = client.post("/api/listings/bulk", json=rows)
    assert first.status_code == 201
    assert first.json() == {"inserted": 2, "skipped": 0, "total_submitted": 2}

    again = client.post("/api/listings/bulk", json={"listings": rows})
    assert again.status_code == 201
    assert again.json() == {"inserted": 0, "skipped": 2, "total_submitted": 2}


def test_blank_fields_become_unknown_and_are_deduplicated() -> None:
    row = {"business_name": f"{PREFIX} Blank", "category": None, "city": "   "}
    created = client.post("/api/listings", json=row)
    assert created.status_code == 201
    body = created.json()
    assert (body["category"], body["city"], body["source"]) == ("Unknown", "Unknown", "Unknown")

    dup = client.post("/api/listings/bulk", json=[row])
    assert dup.json()["skipped"] == 1

    sources = {item["label"] for item in client.get("/api/stats/source").json()}
    assert "Unknown" in sources


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("post", "/api/listings/bulk", {"json": [{"category": "Cafe"}]}),
        ("post", "/api/listings/bulk", {"json": [{"business_name": ["not", "a", "string"]}]}),
        ("post", "/api/listings/bulk", {"content": "{bad json", "headers": {"Content-Type": "application/json"}}),
        ("post", "/api/listings", {"json": {"business_name": ""}}),
        ("get", "/api/listings?page=0", {}),
        ("get", "/api/listings/abc", {}),
        ("get", "/api/stats/city?limit=0", {}),
    ],
)
def test_invalid_input_returns_422(method: str, url: str, kwargs: dict) -> None:
    assert getattr(client, method)(url, **kwargs).status_code == 422


def test_missing_listing_returns_404() -> None:
    assert client.get("/api/listings/999999999").status_code == 404


@pytest.mark.parametrize("column", ["category", "city", "source"])
def test_stats_match_sql_and_add_up_to_total(column: str) -> None:
    api = {item["label"]: item["count"] for item in client.get(f"/api/stats/{column}?limit=100").json()}
    with SessionLocal() as db:
        sql = dict(
            db.execute(
                text(
                    f"SELECT COALESCE(NULLIF(TRIM({column}), ''), 'Unknown') AS label, COUNT(*) "
                    f"FROM listing_master GROUP BY label"
                )
            ).all()
        )
    assert api == sql
    total = client.get("/api/stats/overview").json()["total_listings"]
    assert sum(api.values()) == total


def test_timeline_covers_requested_days_and_counts_today() -> None:
    client.post("/api/listings", json={"business_name": f"{PREFIX} Today", "city": "Pune", "category": "Cafe"})
    points = client.get("/api/stats/timeline?days=7").json()
    assert len(points) == 7
    assert points[-1]["count"] >= 1
    assert [p["date"] for p in points] == sorted(p["date"] for p in points)


def test_city_category_rows_add_up() -> None:
    body = client.get("/api/stats/city-category?cities=3&categories=2").json()
    assert body["categories"][-1] == "Other" and len(body["categories"]) == 3
    assert len(body["rows"]) == 3
    city_totals = {item["label"]: item["count"] for item in client.get("/api/stats/city?limit=3").json()}
    for row in body["rows"]:
        assert sum(row[c] for c in body["categories"]) == row["total"] == city_totals[row["city"]]


class _BrokenSession:
    """Stands in for a Session when MySQL is unreachable."""

    def _fail(self, *args: object, **kwargs: object) -> None:
        raise OperationalError("SELECT 1", {}, ConnectionRefusedError("MySQL is down"))

    execute = scalar = scalars = get = _fail

    def close(self) -> None:
        pass


def test_database_down_returns_503() -> None:
    app.dependency_overrides[get_db] = lambda: _BrokenSession()
    try:
        stats = client.get("/api/stats/overview")
        assert stats.status_code == 503
        assert "Database unavailable" in stats.json()["detail"]
        assert client.get("/health").status_code == 503
    finally:
        app.dependency_overrides.clear()
