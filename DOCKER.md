# 🐳 Docker Deployment Guide

This guide covers how to deploy the Stock Prediction API using Docker with full monitoring capabilities.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM available
- 10GB+ disk space

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <your-repo>
cd stock-predictions/api
```

### 2. Configure Environment
```bash
# Copy and edit production environment
cp .env.docker .env.production

# Edit with your settings
nano .env.production  # Linux/Mac
notepad .env.production  # Windows
```

**Important**: Change these values in `.env.production`:
- `POSTGRES_PASSWORD`: Strong database password
- `SECRET_KEY`: Cryptographically secure secret key
- `GRAFANA_PASSWORD`: Grafana admin password

### 3. Deploy

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```cmd
deploy.bat
```

### 4. Verify Deployment
```bash
# Check all services are running
docker-compose ps

# Test API health
curl http://localhost:8000/health

# Test prediction endpoint
curl -X POST "http://localhost:8000/api/stocks/AAPL/predict" \
     -H "Content-Type: application/json" \
     -d '{"days": 7}'
```

## 🌐 Service Access

| Service | URL | Credentials |
|---------|-----|-------------|
| **API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **Metrics** | http://localhost:8001/metrics | - |
| **Jaeger UI** | http://localhost:16686 | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin |
| **Database** | localhost:5432 | postgres/[your-password] |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   Stock API     │    │   PostgreSQL    │
│  (Port 80/443)  │───▶│  (Port 8000)    │───▶│  (Port 5432)    │
│   Load Balancer │    │   FastAPI App   │    │    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │    Metrics      │
         │              │  (Port 8001)    │
         │              │   Prometheus    │
         │              └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Grafana     │    │   Prometheus    │    │     Jaeger      │
│  (Port 3000)    │◀───│  (Port 9090)    │    │  (Port 16686)   │
│  Visualization  │    │ Metrics Storage │    │  Tracing UI     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration Options

### Environment Variables

**Database:**
- `POSTGRES_SERVER`: Database host (default: postgres)
- `POSTGRES_USER`: Database username (default: postgres)
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name (default: stock_predictions)

**API Security:**
- `SECRET_KEY`: JWT signing key (required)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 1440)

**Monitoring:**
- `JAEGER_ENDPOINT`: Jaeger collector endpoint
- `PROMETHEUS_PORT`: Metrics server port (default: 8001)
- `OTEL_CONSOLE_EXPORT`: Enable console logging (default: false)

### Docker Compose Profiles

**Development:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```
- Hot reload enabled
- Console logging enabled
- Development dependencies included

**Production:**
```bash
docker-compose -f docker-compose.yml up
```
- Optimized builds
- No hot reload
- Production security settings

## 📊 Monitoring & Observability

### Distributed Tracing (Jaeger)
- **URL**: http://localhost:16686
- **Features**: Request tracing, yfinance API monitoring, ML pipeline analysis
- **Usage**: Search by service "stock-prediction-api"

### Metrics (Prometheus)
- **URL**: http://localhost:9090
- **Custom Metrics**:
  - `api_request_duration_seconds`: API response times
  - `yfinance_request_duration_seconds`: External API performance
  - `prediction_requests_total`: Prediction volume
  - `yfinance_errors_total`: External API failures

### Visualization (Grafana)
- **URL**: http://localhost:3000
- **Login**: admin/admin (change in production)
- **Dashboards**: Pre-configured dashboards for API and ML metrics

## 🛠️ Common Operations

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f stock-api

# Last 100 lines
docker-compose logs --tail=100 stock-api
```

### Database Operations
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d stock_predictions

# Run migrations
docker-compose exec stock-api poetry run alembic upgrade head

# Create new migration
docker-compose exec stock-api poetry run alembic revision --autogenerate -m "description"
```

### Scaling
```bash
# Scale API instances
docker-compose up -d --scale stock-api=3

# Scale with load balancer
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Backup & Restore
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres stock_predictions > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres stock_predictions < backup.sql
```

## 🔒 Security Considerations

### Production Checklist
- [ ] Change default passwords in `.env.production`
- [ ] Use strong `SECRET_KEY` (32+ random characters)
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring alerts
- [ ] Enable log aggregation
- [ ] Regular security updates

### SSL/HTTPS Setup
1. Obtain SSL certificates (Let's Encrypt recommended)
2. Place certificates in `nginx/ssl/`
3. Update `nginx/nginx.conf` with SSL configuration
4. Restart nginx service

## 🚨 Troubleshooting

### Common Issues

**API not responding:**
```bash
# Check service status
docker-compose ps

# Check API logs
docker-compose logs stock-api

# Restart API
docker-compose restart stock-api
```

**Database connection errors:**
```bash
# Check database status
docker-compose exec postgres pg_isready -U postgres

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**Memory issues:**
```bash
# Check resource usage
docker stats

# Increase Docker memory limit
# Docker Desktop: Settings > Resources > Memory
```

**Port conflicts:**
```bash
# Check port usage
netstat -tulpn | grep :8000

# Use different ports
# Edit docker-compose.yml port mappings
```

### Performance Tuning

**API Performance:**
- Increase `uvicorn` workers: `--workers 4`
- Enable connection pooling
- Add Redis caching layer
- Scale horizontally with load balancer

**Database Performance:**
- Tune PostgreSQL settings
- Add database indices
- Monitor query performance
- Consider read replicas

**Monitoring Overhead:**
- Adjust tracing sample rates
- Configure metric retention
- Optimize dashboard queries

## 📈 Scaling for Production

### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  stock-api:
    deploy:
      replicas: 3
  
  nginx:
    depends_on:
      - stock-api
    environment:
      - NGINX_WORKERS=4
```

### Load Testing
```bash
# Install hey
go install github.com/rakyll/hey@latest

# Load test API
hey -n 1000 -c 10 http://localhost:8000/api/stocks/AAPL

# Load test predictions
hey -n 100 -c 5 -m POST -H "Content-Type: application/json" \
    -d '{"days": 7}' http://localhost:8000/api/stocks/AAPL/predict
```

## 📞 Support

For issues and questions:
1. Check logs: `docker-compose logs`
2. Review configuration files
3. Consult monitoring dashboards
4. Check GitHub issues
5. Contact support team
