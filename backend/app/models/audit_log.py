"""AuditLog model — US-025, US-026."""

import enum
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class AuditAction(str, enum.Enum):
    SUBMITTED = "submitted"
    EVALUATION_STARTED = "evaluation_started"
    EVALUATION_COMPLETED = "evaluation_completed"
    ROUTED = "routed"
    REVIEWER_ASSIGNED = "reviewer_assigned"
    REVIEWER_COMMENTED = "reviewer_commented"
    REVIEWER_APPROVED = "reviewer_approved"
    REVIEWER_REJECTED = "reviewer_rejected"
    APPROVER_ASSIGNED = "approver_assigned"
    APPROVER_APPROVED = "approver_approved"
    APPROVER_REJECTED = "approver_rejected"
    AUTO_APPROVED = "auto_approved"
    AUTO_REJECTED = "auto_rejected"
    STATUS_CHANGED = "status_changed"
    CONFIG_UPDATED = "config_updated"
    USER_CREATED = "user_created"
    USER_ROLE_CHANGED = "user_role_changed"


class ActorType(str, enum.Enum):
    CUSTOMER = "customer"
    REVIEWER = "reviewer"
    APPROVER = "approver"
    ADMIN = "admin"
    COMPLIANCE = "compliance"
    SYSTEM = "system"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    application_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("applications.id"), nullable=True, index=True
    )
    actor_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    actor_type: Mapped[ActorType] = mapped_column(Enum(ActorType), nullable=False)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    before_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    after_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    application = relationship("Application", back_populates="audit_logs")
