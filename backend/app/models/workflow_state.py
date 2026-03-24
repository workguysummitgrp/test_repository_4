"""WorkflowState model — US-012, US-013."""

import enum
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class WorkflowStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class DecisionRoute(str, enum.Enum):
    AUTO_APPROVE = "auto_approve"
    APPROVER_ONLY = "approver_only"
    REVIEWER_APPROVER = "reviewer_approver"
    AUTO_REJECT = "auto_reject"


class WorkflowState(Base):
    __tablename__ = "workflow_states"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("applications.id"), unique=True, nullable=False
    )
    current_node: Mapped[str] = mapped_column(String(50), nullable=False)
    workflow_status: Mapped[WorkflowStatus] = mapped_column(
        Enum(WorkflowStatus), nullable=False, default=WorkflowStatus.ACTIVE
    )
    state_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    decision_route: Mapped[DecisionRoute | None] = mapped_column(Enum(DecisionRoute), nullable=True)
    entered_node_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    application = relationship("Application", back_populates="workflow_state")
