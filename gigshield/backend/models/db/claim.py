"""
Claim ORM Model — represents an insurance claim created when MSC is confirmed.
Status machine: pending_fraud_check → fraud_checking → approved/flagged/on_hold/rejected → paid
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, DateTime, ForeignKey, Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base
from backend.models.db.compat import GUID


class Claim(Base):
    """Insurance claim tied to a rider, policy, and trigger event."""

    __tablename__ = "claims"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    rider_id = Column(GUID(), ForeignKey("riders.id"), nullable=False)
    policy_id = Column(GUID(), ForeignKey("policies.id"), nullable=False)
    trigger_event_id = Column(GUID(), ForeignKey("trigger_events.id"), nullable=False)

    # Earnings DNA inputs
    baseline_hourly_earning_paise = Column(BigInteger, nullable=False)
    disruption_hours = Column(Float, nullable=False)
    zone_impact_factor = Column(Float, nullable=False)  # 0.60–1.00
    coverage_factor = Column(Float, nullable=False)      # 0.70 or 0.85

    # Computed payout
    calculated_payout_paise = Column(BigInteger, nullable=False)
    capped_payout_paise = Column(BigInteger, nullable=False)  # min(calculated, coverage_cap)

    # Status machine
    status = Column(String(20), nullable=False, default="pending_fraud_check")
    # Values: pending_fraud_check | fraud_checking | approved | flagged | on_hold | rejected | paid

    # Fraud pipeline
    confidence_score = Column(Integer)       # 0–100
    fraud_decision = Column(String(20))      # 'auto_approved'|'flagged'|'held'|'rejected'
    fraud_reason = Column(String(100))       # rejection reason code

    # Timing
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    fraud_checked_at = Column(DateTime(timezone=True))
    payout_initiated_at = Column(DateTime(timezone=True))
    paid_at = Column(DateTime(timezone=True))

    # Relationships
    rider = relationship("Rider", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")
    trigger_event = relationship("TriggerEvent", back_populates="claims")
    fraud_check = relationship("FraudCheck", back_populates="claim", uselist=False, lazy="selectin")
    payout = relationship("Payout", back_populates="claim", uselist=False, lazy="selectin")

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("rider_id", "trigger_event_id", name="idx_claims_rider_event"),
        Index("idx_claims_status", "status"),
    )

    def __repr__(self):
        return f"<Claim rider={self.rider_id} status={self.status} payout={self.capped_payout_paise}>"
