"""ApproverDecision model — US-018, US-019, US-020."""

import enum
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class ApproveDecision(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ApproverSource(str, enum.Enum):
    DIRECT = "direct"
    ESCALATED = "escalated"


class ApproverDecision(Base):
    __tablename__ = "approver_decisions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("applications.id"), unique=True, nullable=False
    )
    approver_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    decision: Mapped[ApproveDecision] = mapped_column(
        Enum(ApproveDecision), nullable=False, default=ApproveDecision.PENDING
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[ApproverSource] = mapped_column(Enum(ApproverSource), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    application = relationship("Application", back_populates="approver_decision")
    approver = relationship("User", back_populates="approver_decisions")
