"""Reviews API — reviewer and approver operations. US-015 through US-020."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from backend.app.core.dependencies import DbSession
from backend.app.core.security import Role, require_roles
from backend.app.models.application import Application, ApplicationStatus, FinalDecision
from backend.app.models.approver_decision import ApproveDecision, ApproverDecision, ApproverSource
from backend.app.models.audit_log import ActorType, AuditAction
from backend.app.models.notification import EventType
from backend.app.models.reviewer_decision import ReviewDecision, ReviewerDecision
from backend.app.models.workflow_state import WorkflowState, WorkflowStatus
from backend.app.schemas.review import (
    ApproverDecisionRequest,
    ApproverDecisionResponse,
    ReviewerCommentRequest,
    ReviewerDecisionRequest,
    ReviewerDecisionResponse,
)
from backend.app.services import audit_service, notification_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


# --- Reviewer endpoints ---

@router.get("/reviewer/queue", response_model=list[ReviewerDecisionResponse])
async def reviewer_queue(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.REVIEWER)),
):
    reviewer_id = int(current_user["sub"])
    result = await db.execute(
        select(ReviewerDecision)
        .where(ReviewerDecision.reviewer_id == reviewer_id, ReviewerDecision.decision == ReviewDecision.PENDING)
        .order_by(ReviewerDecision.assigned_at.asc())
    )
    return list(result.scalars().all())


@router.post("/{app_id}/comment", response_model=ReviewerDecisionResponse)
async def add_reviewer_comment(
    app_id: int,
    body: ReviewerCommentRequest,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.REVIEWER)),
):
    reviewer_id = int(current_user["sub"])
    result = await db.execute(
        select(ReviewerDecision).where(
            ReviewerDecision.application_id == app_id,
            ReviewerDecision.reviewer_id == reviewer_id,
        )
    )
    rd = result.scalar_one_or_none()
    if not rd:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review assignment not found")
    rd.comment = body.comment

    await audit_service.log_action(
        db, AuditAction.REVIEWER_COMMENTED, ActorType.REVIEWER,
        application_id=app_id, actor_id=reviewer_id,
    )
    return rd


@router.post("/{app_id}/reviewer-decision", response_model=ReviewerDecisionResponse)
async def make_reviewer_decision(
    app_id: int,
    body: ReviewerDecisionRequest,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.REVIEWER)),
):
    reviewer_id = int(current_user["sub"])
    result = await db.execute(
        select(ReviewerDecision).where(
            ReviewerDecision.application_id == app_id,
            ReviewerDecision.reviewer_id == reviewer_id,
        )
    )
    rd = result.scalar_one_or_none()
    if not rd:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review assignment not found")

    if body.decision == "rejected" and not body.comment:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Comment required for rejection")

    now = datetime.now(timezone.utc)
    rd.decision = ReviewDecision(body.decision)
    rd.decided_at = now
    if body.comment:
        rd.comment = body.comment

    action = AuditAction.REVIEWER_APPROVED if body.decision == "approved" else AuditAction.REVIEWER_REJECTED
    await audit_service.log_action(
        db, action, ActorType.REVIEWER,
        application_id=app_id, actor_id=reviewer_id,
    )

    # Update application and workflow
    app_result = await db.execute(select(Application).where(Application.id == app_id))
    app = app_result.scalar_one_or_none()

    if body.decision == "approved" and app:
        # Escalate to approver
        ws_result = await db.execute(select(WorkflowState).where(WorkflowState.application_id == app_id))
        ws = ws_result.scalar_one_or_none()
        if ws:
            ws.current_node = "approver"
            ws.entered_node_at = now

        # Create approver assignment (round-robin stub — assign first available approver)
        from backend.app.models.user import User, UserRole
        approver_result = await db.execute(
            select(User).where(User.role == UserRole.APPROVER, User.status == "active").limit(1)
        )
        approver = approver_result.scalar_one_or_none()
        if approver:
            ad = ApproverDecision(
                application_id=app_id,
                approver_id=approver.id,
                comment="",
                source=ApproverSource.ESCALATED,
                assigned_at=now,
            )
            db.add(ad)

    elif body.decision == "rejected" and app:
        app.status = ApplicationStatus.REJECTED
        app.final_decision = FinalDecision.REJECTED
        app.final_decision_by = reviewer_id
        app.decision_at = now

        ws_result = await db.execute(select(WorkflowState).where(WorkflowState.application_id == app_id))
        ws = ws_result.scalar_one_or_none()
        if ws:
            ws.current_node = "completed"
            ws.workflow_status = WorkflowStatus.COMPLETED

        await notification_service.send_notification(
            db, app.user_id, EventType.DECISION_REJECTED,
            application_id=app.id, app_id_str=app.application_id,
        )

    return rd


# --- Approver endpoints ---

@router.get("/approver/queue", response_model=list[ApproverDecisionResponse])
async def approver_queue(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.APPROVER)),
):
    approver_id = int(current_user["sub"])
    result = await db.execute(
        select(ApproverDecision)
        .where(ApproverDecision.approver_id == approver_id, ApproverDecision.decision == ApproveDecision.PENDING)
        .order_by(ApproverDecision.assigned_at.asc())
    )
    return list(result.scalars().all())


@router.post("/{app_id}/approver-decision", response_model=ApproverDecisionResponse)
async def make_approver_decision(
    app_id: int,
    body: ApproverDecisionRequest,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.APPROVER)),
):
    approver_id = int(current_user["sub"])
    result = await db.execute(
        select(ApproverDecision).where(
            ApproverDecision.application_id == app_id,
            ApproverDecision.approver_id == approver_id,
        )
    )
    ad = result.scalar_one_or_none()
    if not ad:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Approver assignment not found")

    now = datetime.now(timezone.utc)
    ad.decision = ApproveDecision(body.decision)
    ad.comment = body.comment
    ad.decided_at = now

    action = AuditAction.APPROVER_APPROVED if body.decision == "approved" else AuditAction.APPROVER_REJECTED
    await audit_service.log_action(
        db, action, ActorType.APPROVER,
        application_id=app_id, actor_id=approver_id,
        rationale=body.comment,
    )

    app_result = await db.execute(select(Application).where(Application.id == app_id))
    app = app_result.scalar_one_or_none()
    if app:
        if body.decision == "approved":
            app.status = ApplicationStatus.APPROVED
            app.final_decision = FinalDecision.APPROVED
            event = EventType.DECISION_APPROVED
        else:
            app.status = ApplicationStatus.REJECTED
            app.final_decision = FinalDecision.REJECTED
            event = EventType.DECISION_REJECTED

        app.final_decision_by = approver_id
        app.decision_at = now

        ws_result = await db.execute(select(WorkflowState).where(WorkflowState.application_id == app_id))
        ws = ws_result.scalar_one_or_none()
        if ws:
            ws.current_node = "completed"
            ws.workflow_status = WorkflowStatus.COMPLETED

        await notification_service.send_notification(
            db, app.user_id, event,
            application_id=app.id, app_id_str=app.application_id,
        )

    return ad
