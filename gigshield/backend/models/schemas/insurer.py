"""
Insurer Pydantic Schemas — dashboard response types.
Insurer CAN see full fraud check details (unlike rider).
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class WeekOverview(BaseModel):
    """This week's KPIs for the insurer dashboard."""
    active_riders: int
    premium_collected_paise: int
    claims_paid_paise: int
    loss_ratio: float
    claims_auto_approved: int
    claims_flagged: int
    claims_rejected: int


class InsurerOverviewResponse(BaseModel):
    """Insurer overview endpoint response."""
    this_week: WeekOverview


class HeatmapZone(BaseModel):
    """Zone data for the risk heatmap."""
    zone_id: str
    zone_name: str
    lat: float
    lon: float
    disruption_probability: float
    expected_claims: int
    reserve_estimate_paise: int
    risk_level: str  # "low" | "medium" | "high"


class HeatmapResponse(BaseModel):
    """Risk heatmap response."""
    zones: list[HeatmapZone]
    forecast_week: str


class FraudQueueItem(BaseModel):
    """Single item in the fraud review queue."""
    claim_id: UUID
    rider_name: str
    zone_id: str
    claim_amount_paise: int
    confidence_score: int
    l1_gps_score: int
    l1_gps_result: str
    l2_weather_score: int
    l2_weather_result: str
    l3_earnings_score: int
    l3_earnings_result: str
    l4_cluster_score: int
    l4_cluster_result: str
    created_at: datetime
    time_waiting_minutes: int


class FraudDecisionRequest(BaseModel):
    """Insurer decision on a held claim."""
    decision: str = Field(..., pattern="^(approve|reject)$")
    note: str = Field(default="", max_length=500)


class InsurerClaimResponse(BaseModel):
    """Claim detail with full fraud info (insurer view)."""
    id: UUID
    rider_name: Optional[str]
    zone_id: str
    capped_payout_paise: int
    confidence_score: Optional[int]
    fraud_decision: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ReserveBreakdown(BaseModel):
    """Reserve estimate per zone."""
    zone_id: str
    zone_name: str
    reserve_paise: int
    expected_claims: int


class ReservesResponse(BaseModel):
    """Weekly reserve estimates."""
    current_week_reserve_paise: int
    next_week_estimate_paise: int
    reserve_ratio: float
    breakdown_by_zone: list[ReserveBreakdown]
