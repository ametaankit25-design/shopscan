# 📍 Business Listings Dashboard

[![React](https://img.shields.io/badge/React-19.3-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack business directory and analytics platform that collects real business listings from OpenStreetMap, stores them in MySQL/SQLite, and visualizes market data through an interactive React dashboard.

---

## 🌟 Key Features

- **🗺️ Interactive Business Directory**: Browse verified restaurants, cafes, hotels, pharmacies, and retail stores
- **🔍 Advanced Search & Filtering**: Filter by keyword, city, category, and data source in real-time
- **📊 Analytics Dashboard**: Real-time KPIs, category rankings, city distribution charts, and market insights
- **📈 Multi-dimensional Analytics**: Stacked charts, 30-day timeline trends, and cross-tabulation views
- **⚡ Resilient Database Architecture**: MySQL with automatic SQLite fallback for 100% uptime
- **🤖 Ethical Web Scraping**: OpenStreetMap Overpass API with robots.txt compliance and rate limiting
- **☁️ Cloud-Ready**: Pre-configured for Vercel (frontend), Render (backend), and TiDB Cloud (MySQL)

---

## 🗂️ Folder Structure

```
buisness-listing-dashboard/
├── frontend/                    # React 19 + Vite 8 frontend
│   ├── src/
│   │   ├── api/                # Axios HTTP client
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Main views (Listings, Dashboard, Analytics)
│   │   ├── context/            # React Context (Toast notifications)
│   │   ├── utils/              # Helper functions, animations
│   │   ├── assets/             # Brand graphics and images
│   │   ├── App.jsx             # React Router setup
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── public/                 # Static assets (favicon, icons)
│   ├── package.json            # Node dependencies
│   ├── package-lock.json       # Locked dependency versions
│   ├── vite.config.js          # Vite configuration
│   ├── index.html              # HTML template
│   ├── vercel.json             # Vercel SPA routing config
│   └── .env.example            # Frontend environment template
│
├── backend/                     # FastAPI Python backend
│   ├── app/
│   │   ├── routers/
│   │   │   ├── listings.py    # CRUD endpoints
│   │   │   └── stats.py       # Analytics endpoints
│   │   ├── main.py            # FastAPI app & middleware
│   │   ├── config.py          # Environment settings
│   │   ├── database.py        # MySQL + SQLite connection
│   │   ├── models.py          # SQLAlchemy ORM models
│   │   ├── schemas.py         # Pydantic validation schemas
│   │   └── crud.py            # Database query functions
│   ├── scripts/
│   │   ├── scrape_directory.py # OpenStreetMap scraper
│   │   ├── seed.py            # Mock data generator
│   │   └── check_db.py        # Database health check
│   ├── tests/
│   │   └── test_api.py        # API integration tests
│   ├── data/                   # Scraped data storage (gitignored)
│   ├── requirements.txt        # Python dependencies
│   ├── requirements-dev.txt    # Dev dependencies (pytest, flake8)
│   ├── pytest.ini              # Pytest configuration
│   └── .env.example            # Backend environment template
│
├── database/
│   └── listing_master.sql      # MySQL database dump with CREATE TABLE and data
│
├── docker-compose.yml           # MySQL 8.0 + Adminer containers
├── .gitignore                   # Git exclusions
├── .env.example                 # Root environment template (Docker)
└── README.md                    # This file
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 19.3 | Component-based UI framework |
| | Vite 8.3 | Fast build tool and dev server |
| | React Router 7 | Client-side routing |
| | Recharts 3.10 | SVG data visualization |
| | Axios 1.21 | HTTP client |
| | Lucide React | Icon library |
| **Backend** | Python 3.12 | Backend language |
| | FastAPI 0.111 | Async REST API framework |
| | Uvicorn 0.30 | ASGI web server |
| | SQLAlchemy 2.0 | ORM and database toolkit |
| | Pydantic 2.8 | Data validation |
| | PyMySQL 1.1 | MySQL connector |
| **Database** | MySQL 8.0 | Primary production database |
| | SQLite 3 | Local fallback database |
| | Adminer | Web-based DB management |
| **Scraping** | Overpass API | OpenStreetMap query service |
| | BeautifulSoup4 | HTML/XML parsing |
| | Faker | Mock data generation |
| **Quality** | Pytest | Backend testing |
| | Flake8 | Python linting |
| | Oxlint | JavaScript linting |

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 20+ & npm
- Docker Desktop (optional - SQLite fallback available)

### 1. Clone Repository
```bash
git clone <repository-url>
cd buisness-listing-dashboard
```

### 2. Database Setup (MySQL via Docker)

**Start MySQL container:**
```bash
docker compose up -d
```

**Verify containers are running:**
```bash
docker compose ps
```

**Import SQL dump:**
```bash
docker exec -i $(docker compose ps -q mysql) mysql -ulistings_user -plistings_pass listings_db < database/listing_master.sql
```

**Access Adminer (optional):**
- URL: http://localhost:8080
- System: MySQL
- Server: mysql
- Username: listings_user
- Password: listings_pass
- Database: listings_db

**Skip Docker?** The backend automatically falls back to SQLite if MySQL is unavailable.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
# Edit .env with your database credentials

# Run backend server
uvicorn app.main:app --reload --port 8000
```

**Backend runs at:** http://localhost:8000
**API docs:** http://localhost:8000/docs

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file from template
cp .env.example .env
# Default: VITE_API_URL=http://localhost:8000/api

# Run development server
npm run dev
```

**Frontend runs at:** http://localhost:5173

---

## 🔐 Environment Variables

### Root `.env` (Docker Compose)
```env
MYSQL_ROOT_PASSWORD=your_root_password
DB_NAME=listings_db
DB_USER=listings_user
DB_PASSWORD=your_secure_password
DB_PORT=3306
```

### Backend `.env`
```env
DB_USER=listings_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=listings_db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend `.env`
```env
VITE_API_URL=http://localhost:8000/api
```

---

## 📡 API Endpoints

**Base URL:** `http://localhost:8000/api`

### Health & Info
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |

### Listings CRUD
| Method | Endpoint | Query Params | Description |
|--------|----------|--------------|-------------|
| `GET` | `/listings` | `page`, `pageSize`, `search`, `city`, `category`, `source` | Get paginated listings with filters |
| `POST` | `/listings` | - | Create single listing |
| `POST` | `/listings/bulk` | - | Bulk insert listings |
| `GET` | `/listings/{id}` | - | Get listing by ID |
| `PATCH` | `/listings/{id}` | - | Update listing |
| `DELETE` | `/listings/{id}` | - | Delete listing |

### Analytics & Statistics
| Method | Endpoint | Query Params | Description |
|--------|----------|--------------|-------------|
| `GET` | `/stats/overview` | - | Total counts (listings, cities, categories, sources) |
| `GET` | `/stats/category` | `limit` (default: 10) | Top categories by listing count |
| `GET` | `/stats/city` | `limit` (default: 10) | Top cities by listing count |
| `GET` | `/stats/source` | - | Distribution by data source |
| `GET` | `/stats/timeline` | `days` (default: 30) | Daily listing creation timeline |
| `GET` | `/stats/city-category` | `cities`, `categories` | Cross-tabulation matrix |

### Example Request
```bash
# Get listings filtered by city
curl "http://localhost:8000/api/listings?city=Mumbai&pageSize=20"

# Get category statistics
curl "http://localhost:8000/api/stats/category?limit=5"
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE `listing_master` (
  `id` int NOT NULL AUTO_INCREMENT,
  `business_name` varchar(255) NOT NULL,
  `category` varchar(150) NOT NULL DEFAULT 'Unknown',
  `city` varchar(100) NOT NULL DEFAULT 'Unknown',
  `address` text,
  `phone` varchar(30) DEFAULT NULL,
  `source` varchar(50) NOT NULL DEFAULT 'Unknown',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `image_url` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_name_city_source` (`business_name`(150), `city`, `source`),
  KEY `idx_category` (`category`),
  KEY `idx_city` (`city`),
  KEY `idx_source` (`source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Key Features:**
- Composite unique constraint prevents duplicate entries
- Indexed columns for fast filtering and aggregation
- UTF-8 support for international business names

---

## 🤖 Data Scraping Approach

The project includes ethical web scraping scripts that collect business data from OpenStreetMap:

### Scraping Script
```bash
cd backend
python scripts/scrape_directory.py --city Mumbai --category restaurant --limit 100
```

### Ethical Guidelines
1. **Public API**: Uses OpenStreetMap's Overpass API (public domain data)
2. **robots.txt Compliance**: Checks and respects robots.txt directives
3. **Rate Limiting**: Built-in delays between requests
4. **User-Agent**: Identifies scraper with contact information
5. **Mirror Failover**: Automatically switches to compliant mirrors
6. **Data Validation**: Skips incomplete records (missing name, phone, or address)

### Data Sources
- **OpenStreetMap**: Real business data via Overpass API
- **Mock Data**: Generated via `scripts/seed.py` for testing (tagged as `source="Mock"`)

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Build Test
```bash
cd frontend
npm run build
```

### Linting
```bash
# Backend
cd backend
flake8 app/

# Frontend
cd frontend
npm run lint
```

---

## 🔄 Regenerate SQL Dump

If you need to regenerate the database dump:

```bash
# Ensure Docker is running
docker compose up -d

# Export database dump
docker exec $(docker compose ps -q mysql) mysqldump -ulistings_user -plistings_pass --databases listings_db --add-drop-table --complete-insert > database/listing_master.sql
```

---

## 🚀 Deployment

### Frontend (Vercel)
1. Push code to GitHub
2. Import project in Vercel
3. Set root directory to `frontend/`
4. Add environment variable: `VITE_API_URL=<your-backend-url>/api`
5. Deploy

### Backend (Render)
1. Create new Web Service
2. Set root directory to `backend/`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `backend/.env.example`

### Database (TiDB Cloud or PlanetScale)
1. Create MySQL 8.0 instance
2. Import `database/listing_master.sql`
3. Update backend `DATABASE_URL` environment variable

---

## 📸 Screenshots

*(Add screenshots here after deployment)*

- Homepage / Listings view
- Dashboard with KPI cards
- Analytics charts
- Modal detail view

---

## 🎬 Demo

**Live Links:**
- 🌐 Frontend: `<Your-Vercel-URL>`
- 🔌 Backend: `<Your-Render-URL>`
- 📹 Demo Video: `<Your-YouTube-Link>`

---

## 💡 Key Technical Challenges Solved

1. **Compliant Web Scraping at Scale**: Integrated OpenStreetMap's public API with robots.txt verification and multi-mirror failover
2. **Zero-Config Deployment**: Dual-engine database system auto-detects MySQL availability and falls back to SQLite
3. **SPA Routing on Static Hosts**: Configured Vercel rewrites for client-side React Router navigation
4. **Cross-Origin Security**: Implemented FastAPI CORS middleware with environment-based origin configuration

---

## 📄 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📞 Contact

For questions or support, please open an issue on GitHub.
