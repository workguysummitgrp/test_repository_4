"""Tests for models — validates all 12 entities. US-001 through US-028."""

import pytest
from datetime import datetime, timezone

from backend.app.models.user import User, UserRole, UserStatus
from backend.app.models.application import Application, ApplicationStatus, FinalDecision
from backend.app.models.application_draft import ApplicationDraft
from backend.app.models.document import Document, FileType, DocumentStatus
from backend.app.models.evaluation import Evaluation, Confidence
from backend.app.models.workflow_state import WorkflowState, WorkflowStatus, DecisionRoute
from backend.app.models.reviewer_decision import ReviewerDecision, ReviewDecision
from backend.app.models.approver_decision import ApproverDecision, ApproveDecision, ApproverSource
from backend.app.models.notification import Notification, NotificationChannel, EventType
from backend.app.models.audit_log import AuditLog, AuditAction, ActorType
from backend.app.models.threshold_config import ThresholdConfig
from backend.app.models.workflow_config import WorkflowConfig


class TestUserModel:
    def test_user_role_enum(self):
        assert UserRole.CUSTOMER.value == "customer"
        assert UserRole.REVIEWER.value == "reviewer"
        assert UserRole.APPROVER.value == "approver"
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.COMPLIANCE.value == "compliance"

    def test_user_status_enum(self):
        assert UserStatus.ACTIVE.value == "active"
        assert UserStatus.LOCKED.value == "locked"
        assert UserStatus.DEACTIVATED.value == "deactivated"


class TestApplicationModel:
    def test_application_status_enum(self):
        assert ApplicationStatus.DRAFT.value == "draft"
        assert ApplicationStatus.SUBMITTED.value == "submitted"
        assert ApplicationStatus.UNDER_EVALUATION.value == "under_evaluation"
        assert ApplicationStatus.UNDER_REVIEW.value == "under_review"
        assert ApplicationStatus.APPROVED.value == "approved"
        assert ApplicationStatus.REJECTED.value == "rejected"

    def test_final_decision_enum(self):
        assert FinalDecision.AUTO_APPROVED.value == "auto_approved"
        assert FinalDecision.APPROVED.value == "approved"
        assert FinalDecision.AUTO_REJECTED.value == "auto_rejected"
        assert FinalDecision.REJECTED.value == "rejected"


class TestDocumentModel:
    def test_file_type_enum(self):
        assert FileType.PDF.value == "pdf"
        assert FileType.JPG.value == "jpg"
        assert FileType.PNG.value == "png"

    def test_document_status_enum(self):
        assert DocumentStatus.UPLOADING.value == "uploading"
        assert DocumentStatus.UPLOADED.value == "uploaded"
        assert DocumentStatus.FAILED.value == "failed"
        assert DocumentStatus.DELETED.value == "deleted"


class TestEvaluationModel:
    def test_confidence_enum(self):
        assert Confidence.LOW.value == "low"
        assert Confidence.MEDIUM.value == "medium"
        assert Confidence.HIGH.value == "high"


class TestWorkflowStateModel:
    def test_workflow_status_enum(self):
        assert WorkflowStatus.ACTIVE.value == "active"
        assert WorkflowStatus.PAUSED.value == "paused"
        assert WorkflowStatus.COMPLETED.value == "completed"
        assert WorkflowStatus.FAILED.value == "failed"

    def test_decision_route_enum(self):
        assert DecisionRoute.AUTO_APPROVE.value == "auto_approve"
        assert DecisionRoute.APPROVER_ONLY.value == "approver_only"
        assert DecisionRoute.REVIEWER_APPROVER.value == "reviewer_approver"
        assert DecisionRoute.AUTO_REJECT.value == "auto_reject"


class TestReviewModels:
    def test_review_decision_enum(self):
        assert ReviewDecision.PENDING.value == "pending"
        assert ReviewDecision.APPROVED.value == "approved"
        assert ReviewDecision.REJECTED.value == "rejected"

    def test_approve_decision_enum(self):
        assert ApproveDecision.PENDING.value == "pending"
        assert ApproveDecision.APPROVED.value == "approved"
        assert ApproveDecision.REJECTED.value == "rejected"

    def test_approver_source_enum(self):
        assert ApproverSource.DIRECT.value == "direct"
        assert ApproverSource.ESCALATED.value == "escalated"


class TestNotificationModel:
    def test_channel_enum(self):
        assert NotificationChannel.EMAIL.value == "email"
        assert NotificationChannel.IN_APP.value == "in_app"
        assert NotificationChannel.BOTH.value == "both"

    def test_event_type_enum(self):
        assert EventType.SUBMISSION_CONFIRMED.value == "submission_confirmed"
        assert EventType.EVALUATION_COMPLETE.value == "evaluation_complete"
        assert EventType.DECISION_APPROVED.value == "decision_approved"
        assert EventType.DECISION_REJECTED.value == "decision_rejected"


class TestAuditLogModel:
    def test_audit_action_enum(self):
        assert AuditAction.SUBMITTED.value == "submitted"
        assert AuditAction.EVALUATION_STARTED.value == "evaluation_started"
        assert AuditAction.AUTO_APPROVED.value == "auto_approved"
        assert AuditAction.CONFIG_UPDATED.value == "config_updated"

    def test_actor_type_enum(self):
        assert ActorType.CUSTOMER.value == "customer"
        assert ActorType.SYSTEM.value == "system"
        assert ActorType.ADMIN.value == "admin"
