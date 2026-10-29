# Demo Script (about 5 minutes)

Before recording: `docker compose up -d`, start the backend (`uvicorn app.main:app --port 8000`
from `backend/`) and the frontend (`npm run dev` from `frontend/`).

## 1. Project overview (30 s)
- Show the repo layout: `frontend/`, `backend/`, `database/`.
- One sentence: real business listings from OpenStreetMap → MySQL → FastAPI → React dashboard.

## 2. Scraping approach (1 min 30 s)
- Open `backend/scripts/scrape_directory.py` and point out:
  - the Overpass API endpoints and the `is_allowed_by_robots()` check;
  - the single honest User-Agent, `--delay` between requests, timeouts, back-off on 429/5xx, no CAPTCHA bypass;
  - `element_to_listing()` skipping records with no name/phone/address.
- Run a short live collection:
  `python scripts/scrape_directory.py --cities Pune --per-city 10`
  - Show the "robots.txt disallows https://overpass-api.de/..." line: the scraper respects it and uses a mirror.
  - Show the "inserted N new rows" output; run it again to show "duplicates ignored".
- Mention `scripts/seed.py` generates extra rows labelled `source = "Mock"`.
- In Adminer (http://localhost:8080) or the MySQL CLI run:
  `SELECT source, COUNT(*) FROM listing_master GROUP BY source;`

## 3. API operation (1 min 30 s)
- Open http://localhost:8000/docs and walk through the `listings`, `stats` and `health` groups.
- `POST /api/listings/bulk` with the example body → `inserted: 2`; execute again → `inserted: 0, skipped: 2`.
- `GET /api/stats/city`, `/api/stats/category`, `/api/stats/source` → `[{label, count}]`.
- Send an invalid body (e.g. no `business_name`) → 422 with a validation message.
- Optional: `docker compose stop mysql`, call `/api/stats/overview` → 503 "Database unavailable", then `docker compose start mysql`.

## 4. Dashboard functionality (1 min 30 s)
- **Dashboard** (http://localhost:5173/dashboard): stat cards (total listings, cities, categories,
  sources), Top Categories bar chart, Data Origin donut (OpenStreetMap vs Mock), cities bar chart.
  Hover a bar to show the tooltip, and compare one number with the `/api/stats/...` response.
- **Analytics**: category ranking, city coverage, source share pie.
- **Listings**: search, filter by city/category, open a listing, add a new listing, then reload the
  Dashboard to show the totals updated.
- Resize the browser to phone width to show the responsive layout.
- Stop the backend and reload the Dashboard to show the error message and Retry button.

## 5. Wrap-up (15 s)
- Data persists in the Docker volume; `database/dump.sql` restores the full dataset.
- Tests: `python -m pytest` (backend) and `npm run lint && npm run build` (frontend).
