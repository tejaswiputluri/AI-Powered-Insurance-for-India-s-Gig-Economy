"""
Policy ORM Model — represents a rider's weekly insurance policy.
Coverage week runs Monday 00:00 IST to Sunday 23:59 IST.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, BigInteger, Float, Date, DateTime, ForeignKey, Index,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base
from backend.models.db.compat import GUID


class Policy(Base):
    """Weekly insurance policy for a rider."""

    __tablename__ = "policies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    rider_id = Column(GUID(), ForeignKey("riders.id"), nullable=False)
    tier = Column(String(20), nullable=False)  # 'basic'|'balanced'|'pro'|'aggressive'
    weekly_premium_paise = Column(BigInteger, nullable=False)
    coverage_cap_paise = Column(BigInteger, nullable=False)
    msc_threshold = Column(Integer, nullable=False, default=2)
    coverage_factor = Column(Float, nullable=False, default=0.70)

    # Validity
    week_start_date = Column(Date, nullable=False)   # Monday of coverage week
    week_end_date = Column(Date, nullable=False)     # Sunday of coverage week
    status = Column(String(20), nullable=False, default="active")
    # Values: 'active' | 'paused' | 'expired'

    # Payment
    premium_deducted_at = Column(DateTime(timezone=True))
    premium_deduction_status = Column(String(20), default="pending")
    # Values: 'pending' | 'success' | 'failed'

    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    rider = relationship("Rider", back_populates="policies")
    claims = relationship("Claim", back_populates="policy", lazy="selectin")

    # Indexes
    __table_args__ = (
        Index("idx_policies_rider_week", "rider_id", "week_start_date"),
    )

    def __repr__(self):
        return f"<Policy {self.tier} rider={self.rider_id} week={self.week_start_date}>"
