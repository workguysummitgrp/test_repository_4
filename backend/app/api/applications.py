"""Applications API — CRUD, submission, status. US-004, US-005, US-006, US-009."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from backend.app.core.dependencies import CurrentUser, DbSession
from backend.app.core.security import Role, require_roles
from backend.app.models.application import Application, ApplicationStatus
from backend.app.models.audit_log import ActorType, AuditAction
from backend.app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationListResponse,
    ApplicationResponse,
    DraftResponse,
    DraftSaveRequest,
)
from backend.app.services import audit_service, form_service, notification_service, workflow_service
from backend.app.models.notification import EventType

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    body: ApplicationCreateRequest,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER)),
):
    user_id = int(current_user["sub"])
    app = await form_service.create_application(db, user_id, body.form_data)
    return app


@router.get("/", response_model=ApplicationListResponse)
async def list_applications(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER)),
    page: int = 1,
    size: int = 20,
):
    user_id = int(current_user["sub"])
    items, total = await form_service.get_user_applications(db, user_id, page, size)
    return ApplicationListResponse(items=items, total=total, page=page, size=size)


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(app_id: str, db: DbSession, current_user: CurrentUser):
    app = await form_service.get_application_by_id(db, app_id)
    if not app:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    # Customers can only view their own applications
    if current_user.get("role") == "customer" and app.user_id != int(current_user["sub"]):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")
    return app


@router.post("/{app_id}/submit", response_model=ApplicationResponse)
async def submit_application(
    app_id: str,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER)),
):
    user_id = int(current_user["sub"])
    app = await form_service.get_application_by_id(db, app_id)
    if not app:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    if app.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")
    if app.status != ApplicationStatus.DRAFT:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Application already submitted")

    app = await form_service.submit_application(db, app)
    await form_service.delete_draft(db, user_id)

    await audit_service.log_action(
        db, AuditAction.SUBMITTED, ActorType.CUSTOMER,
        application_id=app.id, actor_id=user_id,
    )

    await notification_service.send_notification(
        db, user_id, EventType.SUBMISSION_CONFIRMED,
        application_id=app.id, app_id_str=app.application_id,
    )

    # Trigger workflow
    await workflow_service.start_workflow(db, app)
    return app


@router.post("/drafts", response_model=DraftResponse)
async def save_draft(
    body: DraftSaveRequest,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER)),
):
    user_id = int(current_user["sub"])
    draft = await form_service.save_draft(db, user_id, body.form_data, body.current_step)
    return draft


@router.get("/drafts/current", response_model=DraftResponse | None)
async def get_current_draft(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER)),
):
    user_id = int(current_user["sub"])
    return await form_service.get_draft(db, user_id)
