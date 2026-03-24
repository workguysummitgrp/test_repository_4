"""Workflow orchestration service — US-012, US-013."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.application import Application, ApplicationStatus, FinalDecision
from backend.app.models.workflow_state import DecisionRoute, WorkflowState, WorkflowStatus
from backend.app.services import audit_service, evaluation_service, notification_service
from backend.app.models.audit_log import ActorType, AuditAction
from backend.app.models.notification import EventType

logger = logging.getLogger(__name__)


async def start_workflow(db: AsyncSession, application: Application) -> WorkflowState:
    """Initialize workflow after application submission."""
    application.status = ApplicationStatus.UNDER_EVALUATION
    now = datetime.now(timezone.utc)

    ws = WorkflowState(
        application_id=application.id,
        current_node="llm_evaluation",
        workflow_status=WorkflowStatus.ACTIVE,
        state_data={"application_id": application.id, "application_str_id": application.application_id},
        entered_node_at=now,
    )
    db.add(ws)
    await db.flush()

    await audit_service.log_action(
        db, AuditAction.EVALUATION_STARTED, ActorType.SYSTEM,
        application_id=application.id,
        after_state={"status": "under_evaluation"},
    )

    # Run evaluation
    doc_meta = [{"file_name": d.file_name, "file_type": d.file_type.value} for d in application.documents]
    evaluation = await evaluation_service.evaluate_application(
        db, application.id, application.form_data, doc_meta
    )

    await audit_service.log_action(
        db, AuditAction.EVALUATION_COMPLETED, ActorType.SYSTEM,
        application_id=application.id,
        after_state={"score": evaluation.score, "confidence": evaluation.confidence.value},
    )

    # Determine route
    route = _determine_route(evaluation.score, evaluation.is_valid)
    ws.current_node = "decision"
    ws.decision_route = route
    ws.state_data = {
        **ws.state_data,
        "score": evaluation.score,
        "confidence": evaluation.confidence.value,
        "decision_route": route.value,
    }

    await audit_service.log_action(
        db, AuditAction.ROUTED, ActorType.SYSTEM,
        application_id=application.id,
        after_state={"route": route.value, "score": evaluation.score},
    )

    # Execute route
    await _execute_route(db, application, ws, route)
    return ws


def _determine_route(score: int, is_valid: bool) -> DecisionRoute:
    if not is_valid:
        return DecisionRoute.REVIEWER_APPROVER
    if score > 90:
        return DecisionRoute.AUTO_APPROVE
    if score >= 80:
        return DecisionRoute.APPROVER_ONLY
    if score >= 70:
        return DecisionRoute.REVIEWER_APPROVER
    return DecisionRoute.AUTO_REJECT


async def _execute_route(
    db: AsyncSession, application: Application, ws: WorkflowState, route: DecisionRoute
) -> None:
    now = datetime.now(timezone.utc)

    if route == DecisionRoute.AUTO_APPROVE:
        application.status = ApplicationStatus.APPROVED
        application.final_decision = FinalDecision.AUTO_APPROVED
        application.decision_at = now
        ws.current_node = "completed"
        ws.workflow_status = WorkflowStatus.COMPLETED

        await audit_service.log_action(
            db, AuditAction.AUTO_APPROVED, ActorType.SYSTEM,
            application_id=application.id,
        )
        await notification_service.send_notification(
            db, application.user_id, EventType.DECISION_APPROVED,
            application_id=application.id, app_id_str=application.application_id,
        )

    elif route == DecisionRoute.AUTO_REJECT:
        application.status = ApplicationStatus.REJECTED
        application.final_decision = FinalDecision.AUTO_REJECTED
        application.decision_at = now
        ws.current_node = "completed"
        ws.workflow_status = WorkflowStatus.COMPLETED

        await audit_service.log_action(
            db, AuditAction.AUTO_REJECTED, ActorType.SYSTEM,
            application_id=application.id,
        )
        await notification_service.send_notification(
            db, application.user_id, EventType.DECISION_REJECTED,
            application_id=application.id, app_id_str=application.application_id,
        )

    elif route == DecisionRoute.REVIEWER_APPROVER:
        application.status = ApplicationStatus.UNDER_REVIEW
        ws.current_node = "reviewer"
        ws.workflow_status = WorkflowStatus.PAUSED

    elif route == DecisionRoute.APPROVER_ONLY:
        application.status = ApplicationStatus.UNDER_REVIEW
        ws.current_node = "approver"
        ws.workflow_status = WorkflowStatus.PAUSED

    ws.entered_node_at = now
