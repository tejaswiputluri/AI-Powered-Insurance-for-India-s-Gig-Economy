"""
Notification Service — mock SMS + in-app toast notifications.
Phase 1: Print to console + store in audit_logs.
In DEMO_MODE: show as in-app toast banners.
"""

import logging
from uuid import UUID
from datetime import datetime, timezone
from backend.config.settings import settings

logger = logging.getLogger(__name__)

# In-memory notification queue for demo mode
_notifications: list[dict] = []


async def send_notification(
    rider_id: UUID,
    notification_type: str,
    template_data: dict,
    db_session=None,
) -> dict:
    """
    Send a notification to a rider.

    notification_type: PAYOUT_SENT | DISRUPTION_DETECTED | CLAIM_REJECTED |
                       CLAIM_ON_HOLD | WEEKLY_COVERAGE_SUMMARY | PRE_DISRUPTION_WARNING
    """
    templates = {
        "PAYOUT_SENT": (
            "GigShield: ₹{amount} paid to your UPI. Stay safe! "
            "Claim: GS-{claim_short_id}"
        ),
        "DISRUPTION_DETECTED": (
            "GigShield: ⚡ Disruption in {zone_name}. "
            "Auto-processing your payout of ~₹{estimate}."
        ),
        "CLAIM_REJECTED": (
            "GigShield: Claim GS-{claim_short_id} rejected. "
            "Reason: {reason_code}. Contact support if incorrect."
        ),
        "CLAIM_ON_HOLD": (
            "GigShield: Claim GS-{claim_short_id} under review. "
            "Decision within 24 hours."
        ),
        "WEEKLY_COVERAGE_SUMMARY": (
            "GigShield: Week starts! ₹{premium} deducted. "
            "Zone risk: {risk_level}. You're covered."
        ),
        "PRE_DISRUPTION_WARNING": (
            "⚠️ GigShield: High disruption probability in {zone_name} "
            "this week ({probability}%). Coverage active."
        ),
    }

    template = templates.get(notification_type, "GigShield notification")
    try:
        message = template.format(**template_data)
    except KeyError as e:
        message = f"GigShield: {notification_type} — {template_data}"
        logger.warning(f"Template key missing: {e}")

    notification = {
        "rider_id": str(rider_id),
        "type": notification_type,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "read": False,
    }

    # Store in memory for demo mode
    _notifications.append(notification)

    # Log to console (Phase 1 mock SMS)
    logger.info(f"📱 SMS to rider {rider_id}: {message}")

    # Store in audit_logs if db_session provided
    if db_session:
        from backend.models.db.audit_log import AuditLog
        audit = AuditLog(
            entity_type="sms",
            entity_id=rider_id,
            action=f"notification_{notification_type.lower()}",
            detail={"message": message, "type": notification_type},
        )
        db_session.add(audit)

    return notification


def get_rider_notifications(rider_id: str, limit: int = 20) -> list[dict]:
    """Get recent notifications for a rider (in-memory for demo)."""
    rider_notifs = [
        n for n in _notifications
        if n["rider_id"] == rider_id
    ]
    return sorted(rider_notifs, key=lambda x: x["timestamp"], reverse=True)[:limit]


def clear_notifications(rider_id: str):
    """Clear all notifications for a rider."""
    global _notifications
    _notifications = [n for n in _notifications if n["rider_id"] != rider_id]
