#!/bin/bash

# Docker deployment script for Stock Prediction API

set -e

echo "🚀 Deploying Stock Prediction API with monitoring..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p monitoring/grafana/{dashboards,provisioning/dashboards,provisioning/datasources}
mkdir -p nginx/ssl
mkdir -p logs

# Copy environment file if it doesn't exist
if [ ! -f .env.production ]; then
    echo "📝 Creating production environment file..."
    cp .env.docker .env.production
    echo "⚠️  Please edit .env.production with your production settings!"
fi

# Build and start services
echo "🔨 Building and starting services..."
docker-compose -f docker-compose.yml -f docker-compose.override.yml down
docker-compose -f docker-compose.yml build --no-cache
docker-compose -f docker-compose.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec stock-api poetry run alembic upgrade head

echo "✅ Deployment complete!"
echo ""
echo "🌐 Service URLs:"
echo "  API:        http://localhost:8000"
echo "  API Docs:   http://localhost:8000/docs"
echo "  Metrics:    http://localhost:8001/metrics"
echo "  Jaeger:     http://localhost:16686"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "🔧 Useful commands:"
echo "  View logs:  docker-compose logs -f"
echo "  Stop all:   docker-compose down"
echo "  Restart:    docker-compose restart stock-api"
echo ""
echo "📊 Test the API:"
echo "  curl http://localhost:8000/health"
echo "  curl http://localhost:8000/api/stocks/AAPL"
