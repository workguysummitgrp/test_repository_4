"""Notifications API — list, read. US-022, US-024."""

from fastapi import APIRouter, Depends

from backend.app.core.dependencies import DbSession
from backend.app.core.security import Role, require_roles
from backend.app.schemas.notification import NotificationListResponse
from backend.app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationListResponse)
async def list_notifications(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER, Role.REVIEWER, Role.APPROVER, Role.ADMIN, Role.COMPLIANCE)),
):
    user_id = int(current_user["sub"])
    items, total, unread = await notification_service.get_user_notifications(db, user_id)
    return NotificationListResponse(items=items, total=total, unread_count=unread)


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER, Role.REVIEWER, Role.APPROVER, Role.ADMIN, Role.COMPLIANCE)),
):
    user_id = int(current_user["sub"])
    await notification_service.mark_as_read(db, notification_id, user_id)
    return {"status": "ok"}
