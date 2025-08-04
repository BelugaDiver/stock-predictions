# OpenTelemetry Monitoring Setup

This setup provides comprehensive observability for the Stock Prediction API using OpenTelemetry, Jaeger, and Prometheus.

## What's Monitored

### 🔍 **Distributed Tracing (Jaeger)**

- **API Request Tracing**: Every API call is traced from start to finish
- **yfinance API Calls**: Detailed tracing of external Yahoo Finance API calls
- **ML Model Training**: Performance tracking of RandomForest model training
- **Database Operations**: SQLAlchemy query performance
- **Feature Engineering**: Time spent on data preparation

### 📊 **Metrics (Prometheus)**

- **API Performance**: Request duration, success/error rates
- **yfinance Performance**: External API call duration and error rates
- **Prediction Metrics**: Number of predictions, model accuracy
- **System Metrics**: Memory, CPU usage (via auto-instrumentation)

## Quick Start

### 1. Start Monitoring Infrastructure

```bash
# Start Jaeger, Prometheus, and Grafana
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. Install Dependencies

```bash
cd api
poetry install
```

### 3. Start the API

```bash
poetry run uvicorn src.main:app --reload --port 8000
```

### 4. Access Monitoring Dashboards

**Jaeger UI (Tracing)**: <http://localhost:16686>

- View distributed traces
- Analyze yfinance API performance
- Debug slow requests

**Prometheus (Metrics)**: <http://localhost:9090>

- Query custom metrics
- Monitor API performance
- Track yfinance call rates

**Grafana (Visualization)**: <http://localhost:3000>

- Username: admin
- Password: admin
- Pre-configured dashboards (coming soon)

**API Metrics Endpoint**: <http://localhost:8001/metrics>

- Prometheus-format metrics
- Direct metrics access

## Key Metrics to Monitor

### 🚀 **Performance Metrics**

```
# API request duration by endpoint
api_request_duration_seconds

# yfinance API call performance
yfinance_request_duration_seconds

# ML model training time
api_request_duration_seconds{endpoint="/api/stocks/{ticker}/predict"}
```

### 📈 **Business Metrics**

```
# Total predictions made
prediction_requests_total

# yfinance API usage
yfinance_requests_total

# API errors
yfinance_errors_total
```

### 🔍 **What to Look For**

**Slow yfinance Calls**:

- Look for `yfinance_request_duration_seconds` > 5 seconds
- Check Jaeger traces for specific slow calls

**Prediction Performance**:

- Monitor training time in prediction traces
- Track prediction accuracy over time

**API Bottlenecks**:

- Identify slowest endpoints
- Find database query performance issues

## Example Queries

### Prometheus Queries

```promql
# Average API response time by endpoint
rate(api_request_duration_seconds_sum[5m]) / rate(api_request_duration_seconds_count[5m])

# yfinance error rate
rate(yfinance_errors_total[5m]) / rate(yfinance_requests_total[5m])

# Prediction requests per minute
rate(prediction_requests_total[1m]) * 60
```

### Jaeger Traces

- Search by service: `stock-prediction-api`
- Filter by operation: `predict_stock_price`
- Look for spans: `fetch_historical_data`, `train_model`

## Troubleshooting

### No Traces in Jaeger

1. Check Jaeger is running: `docker ps`
2. Verify JAEGER_ENDPOINT in .env
3. Check API logs for OpenTelemetry errors

### No Metrics in Prometheus

1. Verify Prometheus can reach API: <http://localhost:8001/metrics>
2. Check Prometheus targets: <http://localhost:9090/targets>
3. Ensure PROMETHEUS_PORT=8001 in .env

### Performance Issues

1. Check yfinance call duration in traces
2. Monitor database query performance
3. Look for high prediction request volume

## Custom Instrumentation

The API includes custom spans for:

- `get_stock_data`: yfinance API calls
- `predict_stock_price`: ML prediction pipeline
- `train_model`: RandomForest training
- `calculate_rsi`: Technical indicator calculation

Each span includes relevant attributes like ticker symbol, duration, and success/failure status.
