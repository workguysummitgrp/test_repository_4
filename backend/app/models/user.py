"""User model — US-001, US-002, US-003."""

import enum
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    REVIEWER = "reviewer"
    APPROVER = "approver"
    ADMIN = "admin"
    COMPLIANCE = "compliance"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    LOCKED = "locked"
    DEACTIVATED = "deactivated"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER)
    status: Mapped[UserStatus] = mapped_column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    otp_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    otp_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    failed_otp_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    applications = relationship("Application", back_populates="user", foreign_keys="Application.user_id")
    drafts = relationship("ApplicationDraft", back_populates="user")
    reviewer_decisions = relationship("ReviewerDecision", back_populates="reviewer")
    approver_decisions = relationship("ApproverDecision", back_populates="approver")
    notifications = relationship("Notification", back_populates="user")
