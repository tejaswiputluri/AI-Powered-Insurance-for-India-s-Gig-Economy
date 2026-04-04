"""
Payout ORM Model — tracks payment disbursement via Razorpay (test mode).
Status: initiated → processing → success | failed
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, BigInteger, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship
from backend.db.database import Base
from backend.models.db.compat import GUID


class Payout(Base):
    """Payout record — tracks money sent to rider via UPI."""

    __tablename__ = "payouts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    claim_id = Column(GUID(), ForeignKey("claims.id"), nullable=False)
    rider_id = Column(GUID(), ForeignKey("riders.id"), nullable=False)
    amount_paise = Column(BigInteger, nullable=False)

    # Payment gateway
    gateway = Column(String(20), nullable=False, default="razorpay_test")
    gateway_payout_id = Column(String(100))   # Razorpay payout ID
    gateway_status = Column(String(20))
    upi_vpa = Column(String(100))             # UPI VPA of rider

    # Status
    status = Column(String(20), nullable=False, default="initiated")
    # Values: initiated | processing | success | failed

    initiated_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    claim = relationship("Claim", back_populates="payout")
    rider = relationship("Rider", back_populates="payouts")

    def __repr__(self):
        return f"<Payout claim={self.claim_id} amount={self.amount_paise} status={self.status}>"
