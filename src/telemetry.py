import os
import logging
from typing import Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from prometheus_client import start_http_server
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelemetryConfig:
    """OpenTelemetry configuration for the Stock Prediction API"""
    
    def __init__(self):
        self.service_name = "stock-prediction-api"
        self.service_version = "1.0.0"
        self.jaeger_endpoint = os.getenv("JAEGER_ENDPOINT", "http://localhost:14268/api/traces")
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "8001"))
        self.enable_console_export = os.getenv("OTEL_CONSOLE_EXPORT", "false").lower() == "true"
        
        # Custom metrics
        self.meter = None
        self.tracer = None
        
        # Metrics for monitoring
        self.api_request_duration = None
        self.yfinance_request_duration = None
        self.prediction_accuracy = None
        self.prediction_requests_total = None
        self.yfinance_requests_total = None
        self.yfinance_errors_total = None
        
    def setup_tracing(self):
        """Configure distributed tracing"""
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": self.service_version,
        })
        
        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Add Jaeger exporter
        try:
            jaeger_exporter = JaegerExporter(
                endpoint=self.jaeger_endpoint,
            )
            span_processor = BatchSpanProcessor(jaeger_exporter)
            tracer_provider.add_span_processor(span_processor)
            logger.info(f"Jaeger tracing configured: {self.jaeger_endpoint}")
        except Exception as e:
            logger.warning(f"Failed to configure Jaeger: {e}")
        
        # Add console exporter for development
        if self.enable_console_export:
            console_exporter = ConsoleSpanExporter()
            console_processor = BatchSpanProcessor(console_exporter)
            tracer_provider.add_span_processor(console_processor)
            logger.info("Console tracing enabled")
        
        self.tracer = trace.get_tracer(__name__)
        return self.tracer
    
    def setup_metrics(self):
        """Configure metrics collection"""
        resource = Resource.create({
            "service.name": self.service_name,
            "service.version": self.service_version,
        })
        
        readers = []
        
        # Add Prometheus exporter
        try:
            prometheus_reader = PrometheusMetricReader()
            readers.append(prometheus_reader)
            
            # Start Prometheus metrics server
            start_http_server(self.prometheus_port)
            logger.info(f"Prometheus metrics server started on port {self.prometheus_port}")
        except Exception as e:
            logger.warning(f"Failed to configure Prometheus: {e}")
        
        # Add console exporter for development
        if self.enable_console_export:
            console_reader = PeriodicExportingMetricReader(
                ConsoleMetricExporter(), export_interval_millis=10000
            )
            readers.append(console_reader)
            logger.info("Console metrics enabled")
        
        # Create meter provider
        if readers:
            meter_provider = MeterProvider(resource=resource, metric_readers=readers)
            metrics.set_meter_provider(meter_provider)
        
        self.meter = metrics.get_meter(__name__)
        self._create_custom_metrics()
        return self.meter
    
    def _create_custom_metrics(self):
        """Create custom metrics for the application"""
        if not self.meter:
            return
            
        # API request duration histogram
        self.api_request_duration = self.meter.create_histogram(
            name="api_request_duration_seconds",
            description="Duration of API requests in seconds",
            unit="s"
        )
        
        # yfinance request duration histogram
        self.yfinance_request_duration = self.meter.create_histogram(
            name="yfinance_request_duration_seconds",
            description="Duration of yfinance API calls in seconds",
            unit="s"
        )
        
        # Prediction accuracy gauge
        self.prediction_accuracy = self.meter.create_histogram(
            name="prediction_accuracy",
            description="Accuracy of stock price predictions",
            unit="1"
        )
        
        # Request counters
        self.prediction_requests_total = self.meter.create_counter(
            name="prediction_requests_total",
            description="Total number of prediction requests"
        )
        
        self.yfinance_requests_total = self.meter.create_counter(
            name="yfinance_requests_total",
            description="Total number of yfinance API calls"
        )
        
        self.yfinance_errors_total = self.meter.create_counter(
            name="yfinance_errors_total",
            description="Total number of yfinance API errors"
        )
    
    def setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries"""
        # Instrument HTTP requests (yfinance uses requests internally)
        RequestsInstrumentor().instrument()
        URLLib3Instrumentor().instrument()
        
        # Instrument SQLAlchemy
        SQLAlchemyInstrumentor().instrument()
        
        logger.info("Auto-instrumentation configured")
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application"""
        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=trace.get_tracer_provider(),
            excluded_urls="/metrics,/health"  # Exclude health checks from tracing
        )
        logger.info("FastAPI instrumentation configured")
    
    def record_yfinance_request(self, duration: float, ticker: str, success: bool = True):
        """Record metrics for yfinance API calls"""
        if self.yfinance_request_duration:
            self.yfinance_request_duration.record(
                duration, 
                {"ticker": ticker, "success": str(success)}
            )
        
        if self.yfinance_requests_total:
            self.yfinance_requests_total.add(
                1, 
                {"ticker": ticker, "success": str(success)}
            )
            
        if not success and self.yfinance_errors_total:
            self.yfinance_errors_total.add(
                1, 
                {"ticker": ticker}
            )
    
    def record_prediction_request(self, ticker: str, days: int, model_type: str = "random_forest"):
        """Record metrics for prediction requests"""
        if self.prediction_requests_total:
            self.prediction_requests_total.add(
                1, 
                {"ticker": ticker, "days": str(days), "model": model_type}
            )
    
    def record_prediction_accuracy(self, accuracy: float, ticker: str, model_type: str = "random_forest"):
        """Record prediction accuracy metrics"""
        if self.prediction_accuracy:
            self.prediction_accuracy.record(
                accuracy, 
                {"ticker": ticker, "model": model_type}
            )

# Global telemetry instance
telemetry = TelemetryConfig()

def init_telemetry(app=None):
    """Initialize OpenTelemetry for the application"""
    logger.info("Initializing OpenTelemetry...")
    
    # Setup tracing and metrics
    telemetry.setup_tracing()
    telemetry.setup_metrics()
    telemetry.setup_auto_instrumentation()
    
    # Instrument FastAPI if app is provided
    if app:
        telemetry.instrument_fastapi(app)
    
    logger.info("OpenTelemetry initialization complete")
    return telemetry

def get_tracer():
    """Get the application tracer"""
    return telemetry.tracer or trace.get_tracer(__name__)

def get_meter():
    """Get the application meter"""
    return telemetry.meter or metrics.get_meter(__name__)
