# Stock Prediction FastAPI Application

This is the core FastAPI application that provides stock prediction, recommendation, and discovery services with comprehensive monitoring and observability.

## 🚀 Quick Start

### Docker Deployment (Recommended)

```bash
# Start the complete stack
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f stock-api
```

### Local Development

```bash
# Install dependencies
poetry install

# Set up environment
cp .env.example .env

# Start development server
poetry run uvicorn src.main:app --reload
```

## 📁 Project Structure

```
src/
├── api/                    # API route handlers
│   ├── discovery.py        # Stock discovery endpoints
│   └── stocks.py          # Stock data and prediction endpoints
├── models/                 # SQLAlchemy database models
│   └── daily.py           # Daily stock data model
├── schemas/                # Pydantic request/response models
│   ├── discovery.py        # Discovery API schemas
│   └── stock.py           # Stock prediction schemas
├── services/               # Business logic layer
│   ├── discovery_service.py # Stock discovery service
│   └── stock_service.py    # Stock prediction service
├── telemetry.py           # OpenTelemetry configuration
├── telemetry_decorators.py # Reusable telemetry decorators
├── config.py              # Application configuration
├── database.py            # Database connection setup
└── main.py                # FastAPI application entry point
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_DB=stock_predictions

# API Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=true
API_V1_STR=/api

# OpenTelemetry Configuration
JAEGER_ENDPOINT=http://localhost:4318/v1/traces
PROMETHEUS_PORT=8001
OTEL_CONSOLE_EXPORT=false
OTEL_SERVICE_NAME=stock-prediction-api
OTEL_SERVICE_VERSION=1.0.0

# External APIs
YFINANCE_TIMEOUT=30
```

### Database Setup

```bash
# Run migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "description"
```

## 📡 API Endpoints

### Health Check
- `GET /health` - Application health status

### Stock Data & Predictions
- `GET /api/stocks/{ticker}` - Historical stock data
- `POST /api/stocks/{ticker}/predict` - Price predictions
- `GET /api/stocks/{ticker}/recommendation` - Trading recommendations

### Stock Discovery
- `GET /api/discovery/search` - Search stocks by ticker/name
- `GET /api/discovery/search/suggestions` - Autocomplete suggestions
- `GET /api/discovery/browse/sectors` - List market sectors
- `GET /api/discovery/browse/sectors/{sector}` - Stocks by sector
- `GET /api/discovery/browse/industries` - List industries
- `GET /api/discovery/browse/industries/{industry}` - Stocks by industry
- `GET /api/discovery/browse/market-cap/{category}` - Filter by market cap
- `GET /api/discovery/browse/price-range` - Filter by price range

### Monitoring
- `GET /metrics` - Prometheus metrics (port 8001)
- OpenTelemetry traces exported to Jaeger

## 🧪 Testing

### Run Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run specific test file
poetry run pytest tests/test_stocks.py -v

# Run tests with different markers
poetry run pytest -m "not slow"
```

### Test Structure

```
tests/
├── conftest.py             # Test configuration and fixtures
├── test_stocks.py          # Stock API tests
├── test_discovery.py       # Discovery API tests (if exists)
└── alembic_tests/          # Database migration tests
```

## 🔍 Code Quality

### Formatting and Linting

```bash
# Format code
poetry run black src tests
poetry run isort src tests

# Linting
poetry run flake8 src tests
poetry run mypy src

# Run all quality checks
poetry run pre-commit run --all-files
```

### Code Style Guidelines

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing

## 📊 Monitoring & Observability

### OpenTelemetry Integration

The application uses decorator-based telemetry for clean separation of concerns:

```python
from telemetry_decorators import trace_method, measure_yfinance_call

@trace_method("operation_name")
@measure_yfinance_call("ticker")
def my_service_method(self, ticker: str):
    # Business logic only - telemetry is automatic
    pass
```

### Available Decorators

- `@trace_method()` - Distributed tracing with automatic span attributes
- `@measure_yfinance_call()` - yfinance API performance tracking
- `@record_prediction_metrics()` - ML prediction metrics
- `@time_operation()` - Operation timing
- `@log_method_call()` - Structured logging

### Custom Metrics

- `yfinance_requests_total` - Total yfinance API calls
- `yfinance_request_duration_seconds` - yfinance response times
- `stock_predictions_total` - Number of predictions made
- `stock_recommendations_total` - Recommendation requests

### Monitoring Stack

- **Jaeger**: Distributed tracing at http://localhost:16686
- **Prometheus**: Metrics collection at http://localhost:9090
- **Grafana**: Dashboards at http://localhost:3000

> **Note**: This application uses the modern OTLP (OpenTelemetry Protocol) exporter to send traces to Jaeger on port 4318, replacing the deprecated Jaeger Thrift exporter. This ensures compatibility with Linux Docker containers and eliminates dependency issues.

## 🏗️ Development

### Adding New Endpoints

1. **Create Pydantic schemas** in `src/schemas/`
2. **Add business logic** in `src/services/`
3. **Create API routes** in `src/api/`
4. **Add telemetry decorators** for observability
5. **Write tests** in `tests/`

### Example Service with Telemetry

```python
from telemetry_decorators import trace_method, log_method_call

class MyService:
    @trace_method("my_operation")
    @log_method_call(include_args=True)
    def my_method(self, param: str) -> str:
        # Clean business logic
        return f"processed {param}"
```

### Database Models

Add new models in `src/models/` and create migrations:

```bash
# After adding/modifying models
poetry run alembic revision --autogenerate -m "add new model"
poetry run alembic upgrade head
```

## 🐳 Docker

### Development

```bash
# Build development image
docker build -f Dockerfile.dev -t stock-api:dev .

# Run with development overrides
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Production

```bash
# Build production image
docker build -t stock-api:latest .

# Deploy production stack
docker-compose up -d
```

### Multi-stage Build

The Dockerfile uses multi-stage builds:
- **Base stage**: Common dependencies
- **Development stage**: Dev tools and hot reload
- **Production stage**: Optimized runtime

## 🔒 Security

### Production Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Use strong database passwords
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure CORS appropriately
- [ ] Set up rate limiting
- [ ] Review log levels (no DEBUG in production)
- [ ] Validate all environment variables

### Environment Security

```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use environment-specific configs
ENVIRONMENT=production  # Changes log levels and debug settings
```

## 🚨 Troubleshooting

### Common Issues

**Import errors**
```bash
# Make sure you're in the api directory
cd api
poetry shell
poetry install
```

**Database connection issues**
```bash
# Check PostgreSQL is running
docker-compose exec postgres pg_isready -U postgres

# Check connection settings in .env
cat .env | grep POSTGRES
```

**Port conflicts**
```bash
# Check what's using port 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/macOS
```

**Poetry issues**
```bash
# Clear cache and reinstall
poetry cache clear . --all
poetry install
```

### Debug Mode

Enable detailed logging:

```bash
# In .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Or set environment variable
export DEBUG=true
poetry run uvicorn src.main:app --reload
```

### Performance Profiling

Monitor performance with OpenTelemetry:

```bash
# Check Jaeger traces
curl http://localhost:16686

# Check Prometheus metrics
curl http://localhost:8001/metrics
```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Examples

```bash
# Get Apple stock data
curl "http://localhost:8000/api/stocks/AAPL?start_date=2024-01-01&end_date=2024-12-31"

# Get predictions
curl -X POST "http://localhost:8000/api/stocks/AAPL/predict" \
  -H "Content-Type: application/json" \
  -d '{"days": 7, "lookback_days": 90}'

# Search stocks
curl "http://localhost:8000/api/discovery/search?query=apple&limit=5"
```

## 🤝 Contributing

### Development Workflow

1. **Fork and clone** the repository
2. **Create feature branch** from main
3. **Install dependencies**: `poetry install`
4. **Make changes** following code style guidelines
5. **Add tests** for new functionality
6. **Run quality checks**: `poetry run pre-commit run --all-files`
7. **Submit pull request** with clear description

### Commit Convention

Use conventional commits:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes
- `refactor:` - Code refactoring
- `test:` - Test additions/modifications
- `chore:` - Maintenance tasks

## 📄 License

This project is licensed under the MIT License - see the main [LICENSE](../LICENSE) file for details.
