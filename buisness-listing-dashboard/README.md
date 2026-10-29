# Business Listings Dashboard

A full-stack dashboard for business directory data. It collects real business listings from
OpenStreetMap, stores them in MySQL, serves them through a FastAPI REST API and shows them in a
React dashboard with charts by city, category and source.

```
frontend/   React 19 + Vite + Recharts dashboard (http://localhost:5173)
backend/    FastAPI + SQLAlchemy API (http://localhost:8000, docs at /docs)
database/   schema.sql (auto-applied by Docker) and dump.sql (full data export)
```

## Tech stack

| Layer     | Technology |
|-----------|------------|
| Frontend  | React 19, Vite 8, React Router 7, Recharts 3, Axios |
| Backend   | Python 3.12, FastAPI 0.111, SQLAlchemy 2, Pydantic 2, PyMySQL |
| Database  | MySQL 8.0 (Docker), utf8mb4; Adminer at http://localhost:8080 |
| Data      | OpenStreetMap via the Overpass API (`requests`), Faker for clearly-labelled mock rows |
| Tooling   | pytest, flake8, oxlint |

## Data

| `source` value  | What it is | How it got there |
|-----------------|------------|------------------|
| `OpenStreetMap` | Real businesses (name, category, city, address, phone) from OpenStreetMap, © OpenStreetMap contributors, ODbL | `scripts/scrape_directory.py` |
| `Mock`          | Synthetic listings generated with Faker for volume / demo purposes | `scripts/seed.py` |

Mock data is always labelled `source = "Mock"` so it is never mistaken for scraped data; the
dashboard's source chart shows the split. Missing or blank category / city / source values are
stored and reported as `Unknown`.

The scraper is built to be polite and compliant:

- checks `robots.txt` for every endpoint (`urllib.robotparser`) and skips any that disallow it -
  e.g. `overpass-api.de` disallows `/api/`, so the scraper uses the public mirrors instead;
- sends one honest User-Agent, waits between requests (`--delay`, default 5 s) and uses timeouts;
- backs off on HTTP 429/5xx and gives up on 403/blocked responses - no CAPTCHA or anti-bot bypass;
- skips records missing a name, phone or address instead of inventing values.

## Setup

Prerequisites: Docker Desktop, Python 3.12+, Node.js 20+.

### 1. MySQL (Docker)

```bash
cp .env.example .env              # Windows: copy .env.example .env  - then set real passwords
docker compose up -d
docker compose ps                 # listings_mysql should show "(healthy)"
```

On the first start Docker runs `database/schema.sql`, which creates `listings_db.listing_master`.
Data lives in the named volume `mysql_data`, so it survives `docker compose stop/start`
(`docker compose down -v` deletes it).

### 2. Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate             # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env  - DB_PASSWORD must match the root .env
python scripts/check_db.py        # verifies the connection and that listing_master exists
uvicorn app.main:app --reload --port 8000
```

Check http://localhost:8000/health → `{"status":"ok","database":"ok"}` and open http://localhost:8000/docs.

### 3. Load data

Pick one (run from `backend/` with the venv active, unless noted):

```bash
# a) Restore the exported dataset (run from the project root)
#    cmd:        docker exec -i listings_mysql sh -c "mysql -uroot -p\"$MYSQL_ROOT_PASSWORD\" listings_db" < database\dump.sql
#    PowerShell: Get-Content -Raw database\dump.sql | docker exec -i listings_mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" listings_db'

# b) Collect fresh real data from OpenStreetMap (takes a few minutes)
python scripts/scrape_directory.py                         # 10 cities, up to 80 listings each
python scripts/scrape_directory.py --cities Mumbai --dry-run   # preview without writing

# c) Add mock rows (labelled source = "Mock")
python scripts/seed.py --count 500
```

Both scripts use `INSERT IGNORE`, so re-running them never creates duplicates.

### 4. Frontend (React)

```bash
cd frontend
cp .env.example .env              # Windows: copy .env.example .env  (VITE_API_URL=http://localhost:8000/api)
npm install
npm run dev                       # http://localhost:5173
```

Pages: **Listings** (search, filter by city / category / source, add/edit/delete), **Dashboard**
(animated totals, top categories, source donut, cities), **Analytics** (category ranking,
city × category stacked chart, listings-added timeline, category share, city coverage, source share,
per-city breakdown table).
If the API or database is down the pages show an error message with a Retry button.

## API reference

Base URL `http://localhost:8000`. Interactive docs: `/docs` (Swagger) and `/redoc`.

| Method | Path | Description |
|--------|------|-------------|
| GET    | `/health` | API + database check; 503 if MySQL is unreachable |
| GET    | `/api/listings` | Paginated list. Query: `page`, `page_size` (≤100), `search`, `category`, `city`, `source` |
| POST   | `/api/listings` | Create one listing |
| POST   | `/api/listings/bulk` | Bulk insert (array or `{"listings": [...]}`); duplicates skipped → `{"inserted", "skipped", "total_submitted"}` |
| GET    | `/api/listings/{id}` | One listing (404 if missing) |
| PATCH  | `/api/listings/{id}` | Partial update |
| DELETE | `/api/listings/{id}` | Delete (204) |
| GET    | `/api/stats/overview` | `total_listings`, `total_cities`, `total_categories`, `total_sources` |
| GET    | `/api/stats/category?limit=10` | `[{label, count}]` per category, largest first |
| GET    | `/api/stats/city?limit=10` | `[{label, count}]` per city |
| GET    | `/api/stats/source` | `[{label, count}]` per source |
| GET    | `/api/stats/timeline?days=30` | `[{date, count}]` listings added per day (zeros included) |
| GET    | `/api/stats/city-category?cities=8&categories=6` | Top cities split by top categories (`Other` = the rest), for the stacked chart and table |

Errors: 422 for invalid input (missing `business_name`, wrong types, bad JSON, bad query/path values),
404 for unknown ids, 503 `{"detail": "Database unavailable..."}` when MySQL is down.

Example:

```bash
curl -X POST http://localhost:8000/api/listings/bulk -H "Content-Type: application/json" \
  -d '[{"business_name":"Cafe Mondegar","category":"Cafe","city":"Mumbai","address":"Colaba Causeway, Mumbai","phone":"22020591","source":"OpenStreetMap"}]'
```

## Database

Table `listing_master` (utf8mb4): `id`, `business_name`, `category`, `city`, `address`, `phone`,
`source`, `image_url`, `created_at`. A unique key on `(business_name, city, source)` blocks duplicates;
`category`, `city` and `source` are `NOT NULL DEFAULT 'Unknown'` so that key also covers rows without them.

Regenerate the dump (run from the project root; writes UTF-8 inside the container, then copies it out):

```bash
docker exec listings_mysql sh -c 'mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" --no-tablespaces listings_db listing_master --result-file=/tmp/dump.sql'
docker cp listings_mysql:/tmp/dump.sql database/dump.sql
```

## Tests and linting

```bash
cd backend
pip install -r requirements-dev.txt
python -m pytest                  # needs the MySQL container running; cleans up its own rows
python -m flake8 app scripts tests
cd ../frontend && npm run lint && npm run build
```

## Challenges Faced

- **Scraping ethically.** Commercial directories (Justdial, YellowPages) block automated access and
  their terms forbid scraping. I switched to OpenStreetMap's Overpass API, which is open data, and
  built the scraper to check `robots.txt`; the main `overpass-api.de` host disallows `/api/`, so it is
  skipped automatically and public mirrors are used instead.
- **Slow / overloaded mirrors.** One big query per city timed out, so the scraper sends one smaller
  query per OSM tag group, with delays, timeouts and back-off on 429/5xx.
- **Incomplete source data.** Many OSM entries lack a phone or address. Those are skipped rather
  than filled with invented values; only complete records are stored.
- **Honest mock data.** Early versions generated Faker rows labelled like real sources. All generated
  rows are now labelled `Mock`, so the dashboard makes the real/mock split visible.
- **NULLs and duplicates.** MySQL unique keys ignore NULLs, so rows without a city/source could be
  duplicated, and NULL groups vanished from the charts. Category/city/source are now normalised to
  `Unknown` (API validation + `NOT NULL DEFAULT 'Unknown'`), so totals always add up.
- **Dump encoding on Windows.** Redirecting `mysqldump` output in PowerShell produced a UTF-16 file
  that MySQL could not import; the dump is now written inside the container and copied out as UTF-8.
- **API-down UX.** The dashboard originally failed silently when the API or database was down; the
  API now returns 503 and the pages show an error with a Retry button.
