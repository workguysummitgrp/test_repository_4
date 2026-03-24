"""Application model — US-004, US-009."""

import enum
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class ApplicationStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_EVALUATION = "under_evaluation"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class FinalDecision(str, enum.Enum):
    AUTO_APPROVED = "auto_approved"
    APPROVED = "approved"
    AUTO_REJECTED = "auto_rejected"
    REJECTED = "rejected"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    application_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.DRAFT
    )
    form_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    form_schema_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    final_decision: Mapped[FinalDecision | None] = mapped_column(Enum(FinalDecision), nullable=True)
    final_decision_by: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    user = relationship("User", back_populates="applications", foreign_keys=[user_id])
    documents = relationship("Document", back_populates="application")
    evaluation = relationship("Evaluation", back_populates="application", uselist=False)
    workflow_state = relationship("WorkflowState", back_populates="application", uselist=False)
    reviewer_decisions = relationship("ReviewerDecision", back_populates="application")
    approver_decision = relationship("ApproverDecision", back_populates="application", uselist=False)
    notifications = relationship("Notification", back_populates="application")
    audit_logs = relationship("AuditLog", back_populates="application")
    draft = relationship("ApplicationDraft", back_populates="application", uselist=False)
