"""
Trigger Event ORM Model — represents a detected disruption event in a zone.
Created when MSC (Multi-Signal Confluence) is confirmed for a zone.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Index,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base
from backend.models.db.compat import GUID


class TriggerEvent(Base):
    """A detected disruption event for a Bengaluru zone."""

    __tablename__ = "trigger_events"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    zone_id = Column(String(50), nullable=False)

    # Signal values at time of trigger
    rainfall_mm_hr = Column(Float)
    aqi_value = Column(Integer)
    order_drop_pct = Column(Float)          # e.g. 0.47 = 47% drop
    road_disruption_pct = Column(Float)
    civic_alert = Column(Boolean, default=False)

    # MSC evaluation
    signals_confirmed = Column(Integer, nullable=False)  # count of signals above threshold
    msc_status = Column(String(20), nullable=False)      # 'not_met'|'standard'|'high'

    # Timing
    detected_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    ended_at = Column(DateTime(timezone=True))  # NULL while active

    # Source flags
    is_demo_event = Column(Boolean, nullable=False, default=False)
    rain_source = Column(String(20), default="open_meteo")
    aqi_source = Column(String(20), default="open_meteo")

    # Relationships
    claims = relationship("Claim", back_populates="trigger_event", lazy="selectin")

    # Indexes — using string column refs for cross-DB compatibility
    __table_args__ = (
        Index("idx_trigger_events_zone_time", "zone_id", "detected_at"),
    )

    @property
    def duration_hours(self) -> float:
        """Calculate event duration in hours. Returns 4.0 if still active."""
        if self.ended_at:
            delta = self.ended_at - self.detected_at
            return delta.total_seconds() / 3600
        return 4.0  # Default for active events

    def __repr__(self):
        return f"<TriggerEvent zone={self.zone_id} signals={self.signals_confirmed} status={self.msc_status}>"
