"""
Rider ORM Model — represents a delivery partner on the GigShield platform.
All money values stored as INTEGER PAISE (RULE-03). All timestamps UTC (RULE-04).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Boolean, DateTime, Text,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base
from backend.models.db.compat import GUID, JSONType


class Rider(Base):
    """Rider (delivery partner) profile with PRF data and ML-computed fields."""

    __tablename__ = "riders"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    phone = Column(String(15), unique=True, nullable=False)  # E.164: +919999999999
    name = Column(String(100))
    firebase_uid = Column(String(128), unique=True, nullable=False)
    zone_id = Column(String(50), nullable=False)  # FK to zones lookup
    platform = Column(String(20), nullable=False)  # 'swiggy' | 'zomato' | 'dunzo'
    work_hours_start = Column(Integer, nullable=False)  # 24hr: 10 = 10am
    work_hours_end = Column(Integer, nullable=False)    # 24hr: 22 = 10pm
    work_days_per_week = Column(Integer, nullable=False, default=6)
    self_reported_daily_earning_paise = Column(BigInteger, nullable=False)  # RULE-03

    # Computed PRF fields (set by ML service after onboarding)
    prf_zone_risk_score = Column(Float)      # 0.0–1.0
    prf_aqi_exposure_score = Column(Float)   # 0.0–1.0
    prf_season_multiplier = Column(Float)    # 0.85–1.20
    prf_claim_history_score = Column(Float, default=0.0)
    computed_weekly_premium_paise = Column(BigInteger)  # Set by FT-Transformer

    # XAI attention weights (JSON blob from FT-Transformer)
    xai_factors = Column(JSONType())

    # Lifecycle
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    is_active = Column(Boolean, nullable=False, default=True)

    # UPI VPA for payouts
    upi_vpa = Column(String(100))

    # Relationships
    policies = relationship("Policy", back_populates="rider", lazy="selectin")
    claims = relationship("Claim", back_populates="rider", lazy="selectin")
    payouts = relationship("Payout", back_populates="rider", lazy="selectin")

    def __repr__(self):
        return f"<Rider {self.name} ({self.phone}) zone={self.zone_id}>"
