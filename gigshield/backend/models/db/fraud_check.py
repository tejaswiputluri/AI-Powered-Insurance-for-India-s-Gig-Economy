"""
FraudCheck ORM Model — stores results of the 4-layer fraud detection pipeline.
L1: GPS Coherence (30pts), L2: Weather Cross-Verify (30pts),
L3: Earnings Anomaly (25pts), L4: Cluster/Ring Detection (15pts).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base
from backend.models.db.compat import GUID


class FraudCheck(Base):
    """Detailed fraud check results for a claim."""

    __tablename__ = "fraud_checks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    claim_id = Column(GUID(), ForeignKey("claims.id"), nullable=False)

    # L1 — GPS Coherence Check
    l1_gps_score = Column(Integer, nullable=False, default=0)    # 0 or 30
    l1_gps_result = Column(String(20), nullable=False)           # 'pass'|'fail'|'skip'
    l1_gps_detail = Column(Text)

    # L2 — Weather Cross-Verify
    l2_weather_score = Column(Integer, nullable=False, default=0)  # 0 or 30
    l2_weather_result = Column(String(20), nullable=False)
    l2_weather_detail = Column(Text)

    # L3 — Earnings Anomaly (Z-Score)
    l3_earnings_score = Column(Integer, nullable=False, default=0)  # 0 or 25
    l3_earnings_result = Column(String(20), nullable=False)
    l3_earnings_detail = Column(Text)

    # L4 — Cluster / Ring Detection
    l4_cluster_score = Column(Integer, nullable=False, default=0)  # 0 or 15
    l4_cluster_result = Column(String(20), nullable=False)
    l4_cluster_detail = Column(Text)

    # Totals
    total_score = Column(Integer, nullable=False)  # sum of all layer scores
    decision = Column(String(20), nullable=False)  # routing decision

    # CNN verify (optional, Phase 3)
    cnn_classification = Column(String(20))   # 'clear'|'light_rain'|'heavy_rain'|'flood'
    cnn_confidence = Column(Float)
    cnn_agrees_with_api = Column(Boolean)

    # Timing
    checked_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationship
    claim = relationship("Claim", back_populates="fraud_check")

    def __repr__(self):
        return f"<FraudCheck claim={self.claim_id} score={self.total_score} decision={self.decision}>"
