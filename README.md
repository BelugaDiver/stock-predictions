<div align="center">

# Stock Prediction & Discovery Platform

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-UI-000000?logo=next.js)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![OpenTelemetry](https://img.shields.io/badge/Observability-OpenTelemetry-673ab7?logo=opentelemetry)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Coverage](https://img.shields.io/badge/Tests-Covered-informational)

<sub>End‑to‑end stock data ingestion, ML predictions, technical recommendations, discovery search, rich UI dashboard, and full observability stack.</sub>

</div>

> Uses modern OTLP exporters (HTTP / gRPC) for Jaeger (no deprecated Thrift). Clean telemetry via decorator abstraction. Designed for local research & extension—NOT financial advice.

---

## 📌 Quick Glance

| Layer | Technology | Notes |
|-------|------------|-------|
| Backend API | FastAPI + Pydantic | Prediction, discovery, recommendations |
| Data Source | Yahoo Finance (`yfinance`) | On-demand historical pricing |
| ML | RandomForestRegressor | Short‑horizon price forecast |
| DB | PostgreSQL + SQLAlchemy + Alembic | Historical & metadata storage |
| UI | Next.js (App Router) + Tailwind | Market summary, sectors, stock cards |
| Observability | OpenTelemetry → Jaeger, Prometheus → Grafana | Tracing + metrics |
| Proxy / Edge | Nginx | Rate limiting, caching (optional) |
| Container Stack | Docker Compose | One command spin‑up |

---

## 🧭 Table of Contents
1. Features
2. Architecture & Flow
3. Repository Structure
4. Data & Prediction Pipeline
5. Environment & Configuration
6. Running (Docker / Local)
7. API Overview & Examples
8. UI Overview
9. Observability (Tracing / Metrics)
10. Testing & Quality
11. Database & Migrations
12. Security & Production
13. Troubleshooting / FAQ
14. Limitations & Roadmap
15. Contributing
16. License & Acknowledgments

---

## 🚀 Features

### Core
- Historical price retrieval (Yahoo Finance)
- ML‑based short‑term prediction (Random Forest)
- Technical indicator aggregation for Buy / Hold / Sell signals
- Rich discovery: sector, industry, market cap, price bands, search & suggestions

### API Layer
- RESTful OpenAPI docs (`/docs`, `/redoc`)
- Filtering, pagination limits, and consistent schema responses
- Health & metrics endpoints

### UI Layer (Next.js 14+)
- Market summary synthesis (real + synthetic fallback indices)
- Sector performance grid
- Stock cards with price & recommendation snapshot
- Headless, composable components (TailwindCSS)

### Platform / Infra
- OpenTelemetry tracing & custom metrics decorators
- Prometheus + Grafana dashboards
- Jaeger trace visualization (OTLP exporter)
- Nginx reverse proxy (rate limit & caching hooks)
- Structured logging & service provenance tags

---

## 🏗️ Architecture & Flow

```text
                              +-------------------+             +--------------------+
                              |   Next.js UI      |  HTTPS/JSON |    FastAPI API     |
                              | (SSR/ISR + CSR)   +------------>+ (/api/* endpoints) |
                              +---------+---------+             +---------+----------+
                                                       |                               |
                                                       |                               |
                                                       |                               v
                                                       |                   +-----------------------+
                                                       |                   |  Service Layer        |
                                                       |                   | (Discovery / Stocks / |
                                                       |                   |  Prediction / Signals)|
                                                       |                               |
                                                       |                               v
                                                       |                   +-----------------------+
                                                       |                   |  Data Providers       |
                                                       |                   |  (yfinance)           |
                                                       |                               |
                                                       |                               v
                                                       |                   +-----------------------+
                                                       |                   |  PostgreSQL Database  |
                                                       |                   +-----------+-----------+
                                                       |                               |
                                                       |                               v
                                                       |                   +-----------------------+
                                                       |                   |  ML Model (RF)        |
                                                       |                   +-----------------------+
                                                       |
      Observability: OpenTelemetry (spans + metrics) → Prometheus / Jaeger → Grafana
```

---

## 📂 Repository Structure (Condensed)

```text
api/               # FastAPI backend
     src/
          api/           # Routers (discovery, stocks)
          services/      # Business logic modules
          models/        # SQLAlchemy ORM models
          schemas/       # Pydantic DTOs
          telemetry*.py  # OTel setup + decorators
          database.py    # Session + engine
          config.py      # Settings & env parsing
          migrations/    # Alembic migration scripts
     monitoring/      # Prometheus & Grafana configs
     nginx/           # Reverse proxy config (optional)
ui/                # Next.js frontend (App Router)
     app/             # Pages/layout
     components/      # Reusable UI parts
     lib/             # API client utilities
tests/             # Pytest suite
```

---

## 🔄 Data & Prediction Pipeline
1. Request hits FastAPI route (e.g. `GET /api/stocks/AAPL`).
2. Service checks DB (if extended to persist) or fetches via `yfinance`.
3. Price frame enriched with derived features (returns, rolling stats).
4. RandomForest model (currently classical, non-deep) predicts short horizon.
5. Confidence heuristics (variance / ensemble dispersion) provided.
6. Technical signals aggregated → recommendation classification (Buy / Hold / Sell).
7. Telemetry decorators emit spans + timing metrics (`yfinance_request_duration_seconds`).
8. Response serialized by Pydantic schema and returned to UI / client.

> Change percent formula:  `(current_close - prev_close) / prev_close * 100`.

---

## ⚙️ Environment & Configuration

Key variables (see `api/.env.example` & `src/config.py`):

| Variable | Purpose | Example |
|----------|---------|---------|
| POSTGRES_SERVER | Hostname for DB | postgres |
| POSTGRES_USER / POSTGRES_PASSWORD | Credentials | postgres / admin |
| POSTGRES_DB | Database name | stock_predictions |
| SECRET_KEY | Security / signing key | (generate) |
| ENVIRONMENT | Runtime mode | development |
| JAEGER_ENDPOINT | OTLP traces | http://jaeger:4318/v1/traces |
| PROMETHEUS_PORT | Metrics exporter port | 8001 |
| OTEL_SERVICE_NAME | Service name | stock-prediction-api |
| YFINANCE_TIMEOUT | External call timeout | 30 |

---

## 🚀 Run (Docker Recommended)

```bash
git clone https://github.com/BelugaDiver/stock-predictions.git
cd stock-predictions
cd api
cp .env.example .env
docker-compose up -d
```

Access:
- API Docs: http://localhost:8000/docs
- Alternate Docs: http://localhost:8000/redoc
- Health: http://localhost:8000/health
- Metrics: http://localhost:8001/metrics
- Jaeger: http://localhost:16686
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / admin by default)
- (Optional) Nginx root: http://localhost

### Frontend (if running separately)
```bash
cd ui
npm install
npm run dev
# Visit http://localhost:3000
```

---

## 🧪 Local Development (No Docker)

Backend:
```bash
cd api
poetry install
cp .env.example .env
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload
```

Frontend:
```bash
cd ui
npm install
npm run dev
```

Optional DB via container only:
```bash
docker run -d --name postgres \
     -e POSTGRES_USER=postgres \
     -e POSTGRES_PASSWORD=admin \
     -e POSTGRES_DB=stock_predictions \
     -p 5432:5432 postgres:15-alpine
```

---

## 📡 API Overview

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/stocks/{ticker} | Historical OHLCV data |
| POST | /api/stocks/{ticker}/predict | Multi‑day predicted prices |
| GET | /api/stocks/{ticker}/recommendation | Technical recommendation |
| GET | /api/discovery/search | Unified search (ticker/name) |
| GET | /api/discovery/search/suggestions | Autocomplete suggestions |
| GET | /api/discovery/browse/sectors | Sector list |
| GET | /api/discovery/browse/sectors/{sector} | Stocks in sector |
| GET | /api/discovery/browse/industries | Industry list |
| GET | /api/discovery/browse/industries/{industry} | Stocks in industry |
| GET | /api/discovery/browse/market-cap/{category} | Market cap filter |
| GET | /api/discovery/browse/price-range | Price range filtering |
| GET | /health | Health check |
| GET | /metrics | Prometheus metrics |

### Example Requests
```bash
curl "http://localhost:8000/api/discovery/search?query=apple&limit=5"
curl "http://localhost:8000/api/stocks/AAPL?start_date=2024-01-01&end_date=2024-06-30"
curl -X POST "http://localhost:8000/api/stocks/AAPL/predict" -H "Content-Type: application/json" -d '{"days":7,"lookback_days":90}'
curl "http://localhost:8000/api/stocks/AAPL/recommendation"
```

---

## 🖥️ UI Overview

Component | Purpose | File
----------|---------|------
Header | Branding & global nav | `ui/components/Header.tsx`
MarketSummary | Aggregates indices + synthetic fallback | `ui/components/MarketSummary.tsx`
SectorOverview | Sector performance matrix | `ui/components/SectorOverview.tsx`
StockCards | Card list for tickers | `ui/components/StockCards.tsx`
API Client | Fetch helpers (SSR/CSR) | `ui/lib/api.ts`

Synthetic fallback triggers when fewer than 2 real indices load; logs a warning and constructs composite sector averages.

---

## 🔭 Observability & Telemetry

File | Role
-----|-----
`src/telemetry.py` | Provider setup (Tracer / Meter) + exporters
`src/telemetry_decorators.py` | `@trace_method`, custom metric wrappers
`services/*` | Decorated methods for spans & metrics

Custom Metrics (illustrative):
- `yfinance_requests_total`
- `yfinance_request_duration_seconds`
- `stock_predictions_total`
- `stock_recommendations_total`

Tracing Path Example:
`HTTP GET /api/stocks/AAPL` → `service.get_stock_history` → `yfinance.fetch` span.

Test OTLP endpoint:
```bash
curl -X POST http://localhost:4318/v1/traces -H "Content-Type: application/json" -d "{}"
```

---

## 🧪 Testing & Quality
```bash
poetry run pytest --cov=src --cov-report=term-missing --cov-report=html
poetry run black .
poetry run isort .
poetry run flake8
poetry run mypy src
poetry run pre-commit run --all-files
```

Open coverage HTML (after run): `api/htmlcov/index.html`.

---

## 🗄️ Database & Migrations
```bash
poetry run alembic revision --autogenerate -m "add_new_feature"
poetry run alembic upgrade head
poetry run alembic downgrade -1
```

Data model seeds can be extended: currently driven via runtime fetch; future improvement: persist symbol metadata & daily candles incrementally.

---

## 🔒 Security & Production Notes
Checklist:
- Rotate `SECRET_KEY` & DB credentials
- Enforce HTTPS (Nginx + certs in `nginx/ssl/` → `cert.pem`, `key.pem`)
- Restrict CORS origins if publicly exposed
- Add Web Application Firewall / rate limiting rules
- Configure backups & retention for PostgreSQL
- Enable alerting (Prometheus rules → Grafana alerts)
- Separate monitoring network segment (optional)

### Production Environment Variables
```bash
POSTGRES_PASSWORD=change-me
SECRET_KEY=generate-a-256-bit-secret
GRAFANA_PASSWORD=change-me
OTEL_SERVICE_NAME=stock-prediction-api
ENVIRONMENT=production
```

---

## 🚨 Troubleshooting (Highlights)
Issue | Action
------|-------
No traces | Verify `JAEGER_ENDPOINT`; check container logs for exporter errors
High latency | Inspect `yfinance_request_duration_seconds` in Prometheus
Port in use | `netstat -ano | findstr :8000` (Windows) / `lsof -i :8000` (Unix)
DB fails migrations | Ensure container healthy: `docker-compose exec postgres pg_isready -U postgres`
Empty predictions | Ensure enough historical bars returned (check logs)

Reset stack completely:
```bash
docker-compose down -v
docker volume prune -f
docker-compose up -d
```

---

## ❗ Limitations
- Classical ML (RandomForest) only; no deep temporal modeling
- No authentication / RBAC
- No persistent caching layer (Redis optional but not configured)
- Rate limits depend on external `yfinance` stability
- No portfolio / order simulation endpoints yet

---

## 🧭 Roadmap (Suggested Enhancements)
- Add Redis caching for hot ticker windows
- Introduce LSTM / Transformer comparative models
- WebSocket streaming for live quote deltas
- Portfolio backtesting & risk metrics
- Persist symbol master + nightly ETL
- Feature store abstraction for ML pipeline
- Add authentication & API keys
- Canary deployment / blue‑green compose overlay

---

## 🤝 Contributing
1. Fork repository
2. Create feature branch: `git checkout -b feat/awesome`
3. Commit (conventional): `feat: add awesome thing`
4. Push & open PR (ensure tests + lint pass)

Commit Types: `feat`, `fix`, `docs`, `refactor`, `test`, `perf`, `chore`, `ci`.

---

## 📄 License
MIT – see [LICENSE](LICENSE).

---

## 🙏 Acknowledgments
- Yahoo Finance (data access via `yfinance`)
- FastAPI / Pydantic ecosystem
- OpenTelemetry, Prometheus, Grafana
- Community open‑source tooling

---

## ⚠️ Disclaimer
This project is for educational & experimental exploration only. Not investment advice. No guarantees on data freshness, completeness, or accuracy.

---

Happy hacking & experimenting! 🚀

## 📋 Prerequisites

### Required Software

**Option 1: Docker (Recommended)**

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) - Includes Docker and Docker Compose
- **Windows**: Download Docker Desktop for Windows
- **macOS**: Download Docker Desktop for Mac  
- **Linux**: Install Docker Engine and Docker Compose separately

**Option 2: Local Development**

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Poetry** - Python package manager [Installation Guide](https://python-poetry.org/docs/#installation)
- **PostgreSQL** - Database server [Download PostgreSQL](https://www.postgresql.org/download/)

### Installing Prerequisites

#### Install Poetry (Local Development)

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

#### Install Docker (Recommended)

1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop/)
2. Install and start Docker Desktop
3. Verify installation:

```bash
docker --version
docker-compose --version
```

## 🏗️ Project Structure

```
.
├── api/                           # Main API application
│   ├── src/
│   │   ├── api/                   # API endpoints
│   │   │   ├── discovery.py       # Stock discovery endpoints
│   │   │   └── stocks.py          # Stock data and prediction endpoints
│   │   ├── models/                # Database models
│   │   ├── schemas/               # Pydantic models
│   │   ├── services/              # Business logic services
│   │   ├── telemetry.py           # OpenTelemetry configuration
│   │   ├── telemetry_decorators.py # Telemetry decorators
│   │   ├── config.py              # Application configuration
│   │   ├── database.py            # Database connection
│   │   └── main.py                # FastAPI application
│   ├── docker-compose.yml         # Complete Docker stack
│   ├── Dockerfile                 # Production Docker image
│   ├── Dockerfile.dev             # Development Docker image
│   ├── DOCKER.md                  # Docker documentation
│   ├── monitoring/                # Monitoring configuration
│   └── nginx/                     # Nginx configuration
├── tests/                         # Test suite
├── pyproject.toml                 # Poetry dependencies
└── README.md                      # This file
```

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/BelugaDiver/stock-predictions.git
cd stock-predictions
```

### 2. Deploy with Docker

```bash
cd api

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings (optional for development)

# Start the complete stack
docker-compose up -d

# Or use the deployment script
./deploy.sh  # Linux/macOS
# OR
deploy.bat   # Windows
```

### 3. Access Services

- **API Documentation**: <http://localhost:8000/docs>
- **API Alternative Docs**: <http://localhost:8000/redoc>
- **Metrics Endpoint**: <http://localhost:8001/metrics>
- **Grafana Dashboard**: <http://localhost:3000> (admin/admin)
- **Prometheus Metrics**: <http://localhost:9090>
- **Jaeger Tracing**: <http://localhost:16686>
- **Nginx (Load Balancer)**: <http://localhost>

### 4. Verify Deployment

```bash
# Check all services are running
docker-compose ps

# Run endpoint tests
cd api
./test-endpoints.sh      # Linux/macOS
# OR
test-endpoints.ps1       # Windows PowerShell

# View logs
docker-compose logs -f stock-api

# Test API manually
curl http://localhost:8000/health
```

## 🛠️ Local Development Setup

### 1. Install Dependencies

```bash
# Install Poetry (if not installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
cd api
poetry install
```

### 2. Setup Database

```bash
# Start PostgreSQL (Docker)
docker run -d --name postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=stock_predictions \
  -p 5432:5432 \
  postgres:15-alpine

# Run migrations
poetry run alembic upgrade head
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your database settings
```

### 4. Start Development Server

```bash
# Start with auto-reload
poetry run uvicorn src.main:app --reload

# Or using Poetry script
poetry run start
```

## 📡 API Endpoints

### Stock Data & Predictions

- `GET /api/stocks/{ticker}` - Get historical stock data
- `POST /api/stocks/{ticker}/predict` - Get price predictions
- `GET /api/stocks/{ticker}/recommendation` - Get trading recommendation

### Stock Discovery

- `GET /api/discovery/search` - Universal ticker search
- `GET /api/discovery/search/suggestions` - Search autocomplete
- `GET /api/discovery/browse/sectors` - List all sectors
- `GET /api/discovery/browse/sectors/{sector}` - Get stocks by sector
- `GET /api/discovery/browse/industries` - List all industries
- `GET /api/discovery/browse/industries/{industry}` - Get stocks by industry
- `GET /api/discovery/browse/market-cap/{category}` - Filter by market cap
- `GET /api/discovery/browse/price-range` - Filter by price range

### System

- `GET /health` - Health check endpoint
- `GET /metrics` - Prometheus metrics (port 8001)

## 🔧 Example Usage

### Stock Discovery

```bash
# Search for Apple stock
curl "http://localhost:8000/api/discovery/search?query=apple&limit=5"

# Get technology sector stocks
curl "http://localhost:8000/api/discovery/browse/sectors/Technology?limit=20"

# Find large-cap stocks
curl "http://localhost:8000/api/discovery/browse/market-cap/large-cap?limit=50"

# Search autocomplete
curl "http://localhost:8000/api/discovery/search/suggestions?query=app&limit=10"
```

### Stock Data & Predictions

```bash
# Get historical data
curl "http://localhost:8000/api/stocks/AAPL?start_date=2024-01-01&end_date=2024-12-31"

# Get 7-day price predictions
curl -X POST "http://localhost:8000/api/stocks/AAPL/predict" \
     -H "Content-Type: application/json" \
     -d '{"days": 7, "lookback_days": 90}'

# Get trading recommendation
curl "http://localhost:8000/api/stocks/AAPL/recommendation"
```

## 📊 Monitoring & Observability

### OpenTelemetry Integration

- **Distributed Tracing**: Track requests across services
- **Custom Metrics**: Monitor yfinance API performance, ML predictions
- **Automatic Instrumentation**: FastAPI, SQLAlchemy, HTTP requests

### Grafana Dashboards

- **API Performance**: Request rates, response times, error rates
- **Business Metrics**: Prediction accuracy, popular stocks
- **Infrastructure**: Database performance, memory usage, CPU utilization
- **Custom Dashboards**: yfinance API monitoring, ML model performance

### Metrics Available

- `yfinance_requests_total` - Total yfinance API calls
- `yfinance_request_duration_seconds` - yfinance response times
- `stock_predictions_total` - Number of predictions made
- `stock_recommendations_total` - Number of recommendations generated

## 🔧 Development

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest --cov=src --cov-report=term-missing --cov-report=html

# Run specific test file
poetry run pytest tests/test_stocks.py -v

# Run with different environments
poetry run pytest --env=test
```

### Code Quality

```bash
# Format code
poetry run black .
poetry run isort .

# Linting
poetry run flake8
poetry run mypy src

# Pre-commit hooks
poetry run pre-commit run --all-files
```

### Database Operations

```bash
# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Upgrade database
poetry run alembic upgrade head

# Downgrade database
poetry run alembic downgrade -1
```

## 🐳 Docker Operations

### Development Environment

```bash
# Build development image
docker-compose -f docker-compose.dev.yml build

# Start development stack
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Production Deployment

```bash
# Production build
docker-compose build --no-cache

# Deploy to production
docker-compose up -d

# Scale API instances
docker-compose up -d --scale stock-api=3

# Update specific service
docker-compose up -d --no-deps stock-api
```

### Monitoring Stack

```bash
# Start only monitoring services
docker-compose up -d prometheus grafana jaeger

# Restart monitoring
docker-compose restart prometheus grafana

# View monitoring logs
docker-compose logs -f grafana prometheus jaeger
```

## 🔒 Security & Production

### Environment Variables

```bash
# Required for production
POSTGRES_PASSWORD=your-secure-password
SECRET_KEY=your-super-secret-key-256-bits
GRAFANA_PASSWORD=secure-grafana-password

# Optional
OTEL_SERVICE_NAME=stock-prediction-api
ENVIRONMENT=production
```

### SSL/HTTPS Setup

```bash
# Generate SSL certificates (included in nginx config)
# Place certificates in nginx/ssl/
# - cert.pem
# - key.pem
```

### Production Checklist

- [ ] Change default passwords in `.env`
- [ ] Configure SSL certificates
- [ ] Set up external database (if not using Docker)
- [ ] Configure backup strategy
- [ ] Set up log aggregation
- [ ] Configure alerting rules
- [ ] Review rate limiting settings

## 🚨 Troubleshooting

### Common Setup Issues

**Docker not found / docker-compose not recognized**

```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop/
# Restart your terminal after installation
# For older systems, use: docker compose instead of docker-compose
```

**Poetry not found**

```bash
# Install Poetry first
curl -sSL https://install.python-poetry.org | python3 -

# On Windows PowerShell:
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -

# Add Poetry to PATH (may require terminal restart)
```

**Python version issues**

```bash
# Check Python version
python --version

# If Python < 3.11, install newer version:
# - Download from https://www.python.org/downloads/
# - Use pyenv for version management: https://github.com/pyenv/pyenv
```

**Port conflicts**

```bash
# If ports are in use, modify docker-compose.yml or stop conflicting services:
# - PostgreSQL: port 5432
# - API: port 8000  
# - Metrics: port 8001
# - Grafana: port 3000
# - Prometheus: port 9090
# - Jaeger UI: port 16686
# - Jaeger OTLP HTTP: port 4318
# - Jaeger OTLP gRPC: port 4317
# - Redis: port 6379
# - Nginx: ports 80, 443

# Check what's using a port (example for port 8000):
# Windows: netstat -ano | findstr :8000
# Linux/macOS: lsof -i :8000
```

**Database connection issues**

```bash
# Check database status
docker-compose exec postgres pg_isready -U postgres

# Reset database
docker-compose down -v
docker volume rm api_postgres_data
docker-compose up -d postgres
```

**Missing environment files**

```bash
# Create .env file in api/ directory
cd api
cp .env.example .env

# Edit .env with your settings (database passwords, etc.)
```

**Permission issues (Linux/macOS)**

```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Fix file permissions
sudo chown -R $USER:$USER .
```

### Alternative Installation Methods

**If Docker Desktop is too heavy, use Docker Engine + Docker Compose:**

**Ubuntu/Debian:**

```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Windows without Docker Desktop:**

- Use WSL2 with Docker Engine
- Or run local development only (see Local Development Setup)

**macOS without Docker Desktop:**

```bash
# Use Homebrew
brew install docker docker-compose
# Note: You'll need Docker Machine or similar for daemon
```

### Local Development without Docker

If you can't use Docker, you can run everything locally:

1. **Install PostgreSQL locally**
2. **Install Redis locally** (optional)
3. **Follow Local Development Setup** section
4. **Skip monitoring components** (or install Prometheus/Grafana separately)

### Getting Help

- Check the [Issues](https://github.com/BelugaDiver/stock-predictions/issues) page
- Review Docker logs: `docker-compose logs`
- Enable verbose logging in `.env`: `LOG_LEVEL=DEBUG`
- Ensure all services are healthy: `docker-compose ps`

### Testing OTLP Endpoint

To verify the OTLP endpoint is working correctly:

```bash
# Test OTLP HTTP endpoint (should return empty response with 200 status)
curl -X POST http://localhost:4318/v1/traces \
     -H "Content-Type: application/json" \
     -d "{}"

# Check Jaeger UI for traces
open http://localhost:16686

# Check OpenTelemetry logs in application
docker-compose logs stock-api | grep -i otlp
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation
- Use conventional commit messages
- Ensure all CI checks pass

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing market data
- **OpenTelemetry** for observability framework
- **FastAPI** for the excellent web framework
- **Prometheus & Grafana** for monitoring capabilities
