import logging
from typing import List

from dispatch.config import DISPATCH_HELP_EMAIL, INCIDENT_RESPONSE_TEAM_EMAIL
from dispatch.database.core import SessionLocal
from dispatch.messaging.strings import (
    INCIDENT_FEEDBACK_DAILY_REPORT,
    MessageType,
)
from dispatch.plugin import service as plugin_service

from .models import Feedback


log = logging.getLogger(__name__)


def send_incident_feedback_daily_report(
    commander_email: str, feedback: List[Feedback], project_id: int, db_session: SessionLocal
):
    """Sends an incident feedback daily report to all incident commanders who received feedback."""
    plugin = plugin_service.get_active_instance(
        db_session=db_session, project_id=project_id, plugin_type="email"
    )

    if not plugin:
        log.warning("Incident feedback daily report not sent. Email plugin is not enabled.")
        return

    items = []
    for piece in feedback:
        participant = piece.participant.individual.name if piece.participant else "Anonymous"
        items.append(
            {
                "name": piece.incident.name,
                "title": piece.incident.title,
                "rating": piece.rating,
                "feedback": piece.feedback,
                "participant": participant,
                "created_at": piece.created_at,
            }
        )

    name = subject = notification_text = "Incident Feedback Daily Report"
    contact_fullname = contact_weblink = DISPATCH_HELP_EMAIL
    plugin.instance.send(
        commander_email,
        notification_text,
        INCIDENT_FEEDBACK_DAILY_REPORT,
        MessageType.incident_feedback_daily_report,
        name=name,
        subject=subject,
        cc=INCIDENT_RESPONSE_TEAM_EMAIL,
        contact_fullname=contact_fullname,
        contact_weblink=contact_weblink,
        items=items,
    )

    log.debug(f"Incident feedback daily report sent to {commander_email}.")
