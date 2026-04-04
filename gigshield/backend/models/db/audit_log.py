"""
Audit Log ORM Model — immutable trace of all system actions.
Every money write, status change, and API fallback is logged here.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, DateTime, Index,
)
from backend.db.database import Base
from backend.models.db.compat import GUID, JSONType


class AuditLog(Base):
    """Immutable audit trail for all entity actions."""

    __tablename__ = "audit_logs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(50), nullable=False)  # 'claim'|'policy'|'rider'|'payout'|'sms'
    entity_id = Column(GUID(), nullable=False)
    action = Column(String(100), nullable=False)
    actor = Column(String(50), nullable=False, default="system")
    detail = Column(JSONType())
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    # Indexes
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id", "created_at"),
    )

    def __repr__(self):
        return f"<AuditLog {self.entity_type}:{self.entity_id} action={self.action}>"
