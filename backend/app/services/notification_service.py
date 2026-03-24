"""Notification service — email (SES) and in-app notifications. US-023, US-024."""

import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.notification import EventType, Notification, NotificationChannel

logger = logging.getLogger(__name__)

NOTIFICATION_TEMPLATES: dict[str, dict[str, str]] = {
    "submission_confirmed": {
        "subject": "Application Submitted Successfully",
        "body": "Your application {app_id} has been submitted and is now under evaluation.",
    },
    "evaluation_complete": {
        "subject": "Application Evaluation Complete",
        "body": "Your application {app_id} evaluation is complete. Check your dashboard for details.",
    },
    "reviewer_assigned": {
        "subject": "New Application Assigned for Review",
        "body": "Application {app_id} has been assigned to you for review.",
    },
    "review_completed": {
        "subject": "Application Review Complete",
        "body": "The review for application {app_id} has been completed.",
    },
    "decision_approved": {
        "subject": "Application Approved",
        "body": "Congratulations! Your application {app_id} has been approved.",
    },
    "decision_rejected": {
        "subject": "Application Decision",
        "body": "Your application {app_id} has been reviewed. Please check your dashboard for details.",
    },
}


async def send_notification(
    db: AsyncSession,
    user_id: int,
    event_type: EventType,
    application_id: int | None = None,
    channel: NotificationChannel = NotificationChannel.BOTH,
    app_id_str: str = "",
) -> Notification:
    template = NOTIFICATION_TEMPLATES.get(event_type.value, {"subject": "Notification", "body": "You have a new notification."})
    subject = template["subject"]
    body = template["body"].format(app_id=app_id_str)

    notification = Notification(
        user_id=user_id,
        application_id=application_id,
        channel=channel,
        event_type=event_type,
        subject=subject,
        body=body,
    )
    db.add(notification)
    await db.flush()

    if channel in (NotificationChannel.EMAIL, NotificationChannel.BOTH):
        try:
            await _send_email(notification)
            notification.email_sent = True
            notification.email_sent_at = datetime.now(timezone.utc)
        except Exception:
            logger.exception("Failed to send email notification %d", notification.id)

    return notification


async def _send_email(notification: Notification) -> None:
    """Send email via AWS SES. Stub for local development."""
    logger.info("Email sent: %s -> user %d", notification.subject, notification.user_id)


async def get_user_notifications(
    db: AsyncSession, user_id: int
) -> tuple[list[Notification], int, int]:
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.sent_at.desc())
        .limit(50)
    )
    items = list(result.scalars().all())

    count_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.user_id == user_id)
    )
    total = count_result.scalar_one()

    unread_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id, Notification.is_read == False  # noqa: E712
        )
    )
    unread = unread_result.scalar_one()
    return items, total, unread


async def mark_as_read(db: AsyncSession, notification_id: int, user_id: int) -> None:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id)
    )
    notif = result.scalar_one_or_none()
    if notif and not notif.is_read:
        notif.is_read = True
        notif.read_at = datetime.now(timezone.utc)
