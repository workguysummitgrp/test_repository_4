"""Audit API — query audit logs. US-025, US-026."""

from fastapi import APIRouter, Depends

from backend.app.core.dependencies import DbSession
from backend.app.core.security import Role, require_roles
from backend.app.schemas.audit import AuditLogListResponse
from backend.app.services import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=AuditLogListResponse)
async def list_audit_logs(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.COMPLIANCE, Role.ADMIN)),
    application_id: int | None = None,
    page: int = 1,
    size: int = 20,
):
    items, total = await audit_service.get_audit_logs(db, application_id, page, size)
    return AuditLogListResponse(items=items, total=total, page=page, size=size)
