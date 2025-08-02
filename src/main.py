from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session
import time

from .config import settings
from .database import engine, Base
from .api.stocks import router as stocks_router
from .api.discovery import router as discovery_router
from .telemetry import init_telemetry, telemetry

# Initialize OpenTelemetry before creating FastAPI app
init_telemetry()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Stock Prediction and Recommendation API"
)

# Initialize OpenTelemetry instrumentation for FastAPI
telemetry.instrument_fastapi(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stocks_router, prefix="/api")
app.include_router(discovery_router, prefix="/api")

# Add custom middleware for request timing
@app.middleware("http")
async def add_telemetry_middleware(request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record request duration
    duration = time.time() - start_time
    if telemetry.api_request_duration:
        telemetry.api_request_duration.record(
            duration,
            {
                "method": request.method,
                "endpoint": str(request.url.path),
                "status_code": str(response.status_code)
            }
        )
    
    # Add timing header
    response.headers["X-Process-Time"] = str(duration)
    
    return response

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Stock Prediction API!",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Metrics endpoint for Prometheus scraping
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)