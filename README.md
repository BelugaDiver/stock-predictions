# Stock Prediction and Discovery API

A comprehensive FastAPI-based application that provides stock price predictions, trading recommendations, and stock discovery capabilities using machine learning and real-time market data. Features include full observability with OpenTelemetry, containerized deployment, and a complete monitoring stack.

## 🚀 Features

### Core Functionality

- **Stock Data Retrieval**: Historical stock data from Yahoo Finance
- **Price Predictions**: Machine learning-based predictions using Random Forest
- **Trading Recommendations**: Technical analysis-based trading recommendations
- **Stock Discovery**: Search, browse, and discover stocks by various criteria

### API Features

- **Discovery APIs**: Search tickers, browse by sector/industry, market cap filtering
- **Prediction APIs**: Multi-day price forecasting with confidence intervals
- **Recommendation APIs**: Buy/Hold/Sell recommendations with confidence scores
- **RESTful API**: Complete OpenAPI documentation with interactive interface

### Infrastructure

- **Observability**: Full OpenTelemetry integration with distributed tracing via OTLP
- **Monitoring**: Prometheus metrics collection and Grafana dashboards
- **Containerization**: Complete Docker setup with orchestration
- **Performance**: Nginx reverse proxy with rate limiting and caching
- **Database**: PostgreSQL with Alembic migrations
- **Code Quality**: Decorator-based telemetry abstraction for clean service code

> **Note**: This application uses the modern OTLP (OpenTelemetry Protocol) exporter for Jaeger instead of the deprecated Jaeger Thrift exporter, ensuring compatibility with Linux Docker containers and future OpenTelemetry versions.

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
