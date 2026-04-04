"""
GigShield Settings — Pydantic BaseSettings reads from .env file.
All configuration is environment-driven. DEMO_MODE is toggled by env var only (RULE-25).
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_ENV: str = Field(default="development", description="development | production")
    DEMO_MODE: bool = Field(default=True, description="Enable demo mode (RULE-09, RULE-25)")
    SECRET_KEY: str = Field(default="gigshield-dev-secret-key-change-in-production", min_length=16)
    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3200,http://localhost:3201,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:3200,http://127.0.0.1:3201")

    # Database — uses SQLite by default for local dev.
    # Set DATABASE_URL in .env to use PostgreSQL/Supabase in production.
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///gigshield.db"
    )
    POSTGRES_PASSWORD: str = Field(default="changeme")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: Optional[str] = Field(
        default=None, description="Path to Firebase service account JSON"
    )
    FIREBASE_PROJECT_ID: str = Field(default="gigshield-dev")

    # Razorpay (TEST MODE ONLY — RULE-23)
    RAZORPAY_KEY_ID: str = Field(default="rzp_test_XXXX")
    RAZORPAY_KEY_SECRET: str = Field(default="XXXX")
    RAZORPAY_ACCOUNT_NUMBER: str = Field(default="XXXXXXXXXXX")

    # ML Services
    ML_PREMIUM_URL: str = Field(default="http://localhost:8001")
    ML_FORECAST_URL: str = Field(default="http://localhost:8002")
    ML_CNN_URL: str = Field(default="http://localhost:8003")
    ML_TIMEOUT_SECONDS: int = Field(default=10)

    # Scheduler
    MSC_POLL_INTERVAL_MINUTES: int = Field(default=30)
    FORECAST_UPDATE_CRON: str = Field(default="0 20 * * 0")
    PREMIUM_DEDUCTION_CRON: str = Field(default="30 0 * * 1")

    # Logging
    LOG_LEVEL: str = Field(default="INFO")

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Demo rider configuration (RULE-24)
    DEMO_RIDER_PHONE: str = "+919999999999"
    DEMO_RIDER_NAME: str = "Ravi Kumar (Demo)"
    DEMO_RIDER_ZONE: str = "BTM_LAYOUT"
    DEMO_RIDER_PLATFORM: str = "swiggy"
    DEMO_RIDER_WORK_START: int = 10
    DEMO_RIDER_WORK_END: int = 22
    DEMO_RIDER_WORK_DAYS: int = 6
    DEMO_RIDER_DAILY_EARNING_PAISE: int = 110000  # ₹1,100

    # Demo events (RULE-22)
    DEMO_EVENTS: dict = {
        "rain_order_drop": {
            "zone_id": "BTM_LAYOUT",
            "rainfall_mm_hr": 14.2,
            "aqi_value": 85,
            "order_drop_pct": 0.41,
            "signals_confirmed": 2,
            "msc_status": "standard",
        },
        "aqi_order": {
            "zone_id": "BTM_LAYOUT",
            "rainfall_mm_hr": 2.1,
            "aqi_value": 218,
            "order_drop_pct": 0.38,
            "signals_confirmed": 2,
            "msc_status": "standard",
        },
        "full_3_signal": {
            "zone_id": "BTM_LAYOUT",
            "rainfall_mm_hr": 18.5,
            "aqi_value": 240,
            "order_drop_pct": 0.52,
            "signals_confirmed": 3,
            "msc_status": "high",
        },
        "fraud_attempt": {
            "zone_id": "BTM_LAYOUT",
            "rainfall_mm_hr": 12.0,
            "aqi_value": 95,
            "order_drop_pct": 0.39,
            "fraud_gps_override": True,
            "fraud_gps_distance_km": 8.2,
            "signals_confirmed": 2,
            "msc_status": "standard",
        },
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


# Singleton instance
settings = Settings()
