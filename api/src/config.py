from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str = "Stock Prediction API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    API_PREFIX: str = "/api"
    
    # Database Configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    
    # Security Configuration
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # OpenTelemetry Configuration
    JAEGER_ENDPOINT: str = "http://jaeger:4318/v1/traces"  # OTLP HTTP endpoint
    PROMETHEUS_PORT: int = 8001
    OTEL_CONSOLE_EXPORT: bool = False
    OTEL_SERVICE_NAME: str = "stock-prediction-api"
    OTEL_SERVICE_VERSION: str = "1.0.0"
    
    # Monitoring Configuration
    GRAFANA_PASSWORD: Optional[str] = "admin"
    
    # Cache Configuration
    REDIS_URL: Optional[str] = "redis://redis:6379/0"
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

settings = Settings()

# Legacy support - keep for backward compatibility during transition
DATABASE_URL = settings.database_url
