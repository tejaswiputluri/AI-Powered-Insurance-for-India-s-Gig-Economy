"""
DB Models Package — imports all ORM models so SQLAlchemy discovers them.
"""

from backend.models.db.compat import GUID, JSONType
from backend.models.db.rider import Rider
from backend.models.db.policy import Policy
from backend.models.db.claim import Claim
from backend.models.db.trigger_event import TriggerEvent
from backend.models.db.payout import Payout
from backend.models.db.fraud_check import FraudCheck
from backend.models.db.audit_log import AuditLog
from backend.models.db.zone_forecast import ZoneForecast

__all__ = [
    "GUID", "JSONType",
    "Rider", "Policy", "Claim", "TriggerEvent",
    "Payout", "FraudCheck", "AuditLog", "ZoneForecast",
]
