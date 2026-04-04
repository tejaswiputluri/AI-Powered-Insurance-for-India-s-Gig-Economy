"""
Zone Forecast ORM Model — stores LSTM disruption predictions per zone.
Updated weekly by the forecast service.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Date, DateTime,
    UniqueConstraint,
)
from backend.db.database import Base
from backend.models.db.compat import GUID


class ZoneForecast(Base):
    """LSTM-generated weekly disruption forecast for a Bengaluru zone."""

    __tablename__ = "zone_forecasts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    zone_id = Column(String(50), nullable=False)
    forecast_week_start = Column(Date, nullable=False)
    disruption_probability = Column(Float, nullable=False)  # 0.0–1.0
    expected_claim_count = Column(Integer)
    reserve_estimate_paise = Column(BigInteger)
    model_version = Column(String(20), default="lstm_v1")
    generated_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Unique constraint
    __table_args__ = (
        UniqueConstraint("zone_id", "forecast_week_start", name="idx_zone_forecast_week"),
    )

    def __repr__(self):
        return f"<ZoneForecast zone={self.zone_id} week={self.forecast_week_start} prob={self.disruption_probability}>"
