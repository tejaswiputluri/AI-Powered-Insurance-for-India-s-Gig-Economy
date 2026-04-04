"""
Claim Pydantic Schemas — request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ClaimResponse(BaseModel):
    """Claim detail response (rider view — limited fraud info per RULE)."""
    id: UUID
    rider_id: UUID
    policy_id: UUID
    trigger_event_id: UUID
    baseline_hourly_earning_paise: int
    disruption_hours: float
    zone_impact_factor: float
    coverage_factor: float
    calculated_payout_paise: int
    capped_payout_paise: int
    status: str
    confidence_score: Optional[int]
    fraud_decision: Optional[str]
    fraud_reason: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    """A single event in the claim timeline."""
    timestamp: str  # UTC ISO format
    event: str
    detail: str


class ClaimTimelineResponse(BaseModel):
    """Full claim timeline — audit trail."""
    events: list[TimelineEvent]


class ClaimListResponse(BaseModel):
    """List of claims."""
    claims: list[ClaimResponse]
    total: int
