"""Notification schemas."""

from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    application_id: int | None = None
    channel: str
    event_type: str
    subject: str
    body: str
    is_read: bool
    sent_at: datetime
    read_at: datetime | None = None

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int
