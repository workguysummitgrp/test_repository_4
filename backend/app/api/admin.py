"""Admin API — thresholds, workflow config. US-014, US-027, US-028."""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.core.dependencies import DbSession
from backend.app.core.security import Role, require_roles
from backend.app.models.audit_log import ActorType, AuditAction
from backend.app.schemas.admin import (
    ThresholdConfigResponse,
    ThresholdUpdateRequest,
    WorkflowConfigResponse,
    WorkflowConfigUpdateRequest,
)
from backend.app.services import admin_service, audit_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/thresholds", response_model=list[ThresholdConfigResponse])
async def get_thresholds(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.ADMIN)),
):
    return await admin_service.get_thresholds(db)


@router.put("/thresholds", response_model=ThresholdConfigResponse)
async def update_threshold(
    body: ThresholdUpdateRequest,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.ADMIN)),
):
    admin_id = int(current_user["sub"])
    try:
        config = await admin_service.update_threshold(db, body.band_name, body.min_score, body.max_score, admin_id)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    await audit_service.log_action(
        db, AuditAction.CONFIG_UPDATED, ActorType.ADMIN,
        actor_id=admin_id,
        after_state={"band_name": body.band_name, "min_score": body.min_score, "max_score": body.max_score},
    )
    return config


@router.get("/workflow-config", response_model=list[WorkflowConfigResponse])
async def get_workflow_configs(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.ADMIN)),
):
    return await admin_service.get_workflow_configs(db)


@router.put("/workflow-config", response_model=WorkflowConfigResponse)
async def update_workflow_config(
    body: WorkflowConfigUpdateRequest,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.ADMIN)),
):
    admin_id = int(current_user["sub"])
    try:
        config = await admin_service.update_workflow_config(db, body.node_name, body.is_enabled, admin_id)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    await audit_service.log_action(
        db, AuditAction.CONFIG_UPDATED, ActorType.ADMIN,
        actor_id=admin_id,
        after_state={"node_name": body.node_name, "is_enabled": body.is_enabled},
    )
    return config
