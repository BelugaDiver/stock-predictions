@echo off
REM Docker deployment script for Stock Prediction API (Windows)

echo 🚀 Deploying Stock Prediction API with monitoring...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "monitoring\grafana\dashboards" mkdir "monitoring\grafana\dashboards"
if not exist "monitoring\grafana\provisioning\dashboards" mkdir "monitoring\grafana\provisioning\dashboards"
if not exist "monitoring\grafana\provisioning\datasources" mkdir "monitoring\grafana\provisioning\datasources"
if not exist "nginx\ssl" mkdir "nginx\ssl"
if not exist "logs" mkdir "logs"

REM Copy environment file if it doesn't exist
if not exist ".env.production" (
    echo 📝 Creating production environment file...
    copy ".env.docker" ".env.production"
    echo ⚠️  Please edit .env.production with your production settings!
)

REM Build and start services
echo 🔨 Building and starting services...
docker-compose -f docker-compose.yml down
docker-compose -f docker-compose.yml build --no-cache
docker-compose -f docker-compose.yml up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...
docker-compose ps

REM Run database migrations
echo 🗄️  Running database migrations...
docker-compose exec stock-api poetry run alembic upgrade head

REM Verify endpoints are responding
echo 🔍 Verifying endpoints...
timeout /t 10 /nobreak >nul

echo Testing API health endpoint...
curl -s http://localhost:8000/health || echo ⚠️  API health check failed

echo Testing metrics endpoint...
curl -s http://localhost:8001/metrics | findstr "# HELP" >nul && echo ✅ Metrics endpoint responding || echo ⚠️  Metrics endpoint failed

echo Testing OTLP endpoint...
curl -s -X POST http://localhost:4318/v1/traces -H "Content-Type: application/json" -d "{}" >nul && echo ✅ OTLP endpoint responding || echo ⚠️  OTLP endpoint failed

echo Testing Jaeger UI...
curl -s http://localhost:16686 | findstr "Jaeger" >nul && echo ✅ Jaeger UI responding || echo ⚠️  Jaeger UI failed

echo Testing Prometheus...
curl -s http://localhost:9090/-/healthy >nul && echo ✅ Prometheus responding || echo ⚠️  Prometheus failed

echo Testing Grafana...
curl -s http://localhost:3000/api/health >nul && echo ✅ Grafana responding || echo ⚠️  Grafana failed

echo ✅ Deployment complete!
echo.
echo 🌐 Service URLs:
echo   API:        http://localhost:8000
echo   API Docs:   http://localhost:8000/docs
echo   Metrics:    http://localhost:8001/metrics
echo   Jaeger:     http://localhost:16686
echo   Prometheus: http://localhost:9090
echo   Grafana:    http://localhost:3000 (admin/admin)
echo.
echo 🔧 Useful commands:
echo   View logs:  docker-compose logs -f
echo   Stop all:   docker-compose down
echo   Restart:    docker-compose restart stock-api
echo.
echo 📊 Test the API:
echo   curl http://localhost:8000/health
echo   curl http://localhost:8000/api/stocks/AAPL
echo.
echo 📈 Monitor with Prometheus:
echo   curl http://localhost:8001/metrics
echo   # View metrics at: http://localhost:9090
echo   # Sample queries:
echo   #   rate(http_requests_total[5m])
echo   #   yfinance_requests_total
echo   #   stock_predictions_total
echo.
echo 🔍 Test OTLP endpoint (Jaeger):
echo   curl -X POST http://localhost:4318/v1/traces ^
echo        -H "Content-Type: application/json" ^
echo        -d "{}"
echo   # View traces at: http://localhost:16686

pause
