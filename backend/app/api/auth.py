"""Auth API — registration, login, OTP. US-001, US-002, US-003."""

import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.dependencies import DbSession
from backend.app.core.security import Role, create_access_token, hash_otp, require_roles, verify_otp
from backend.app.models.audit_log import ActorType, AuditAction
from backend.app.models.user import User, UserRole, UserStatus
from backend.app.schemas.user import (
    LoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    UserRoleUpdate,
)
from backend.app.services import audit_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _generate_otp() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: DbSession):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists.")

    user = User(email=body.email, full_name=body.full_name)
    db.add(user)
    await db.flush()

    await audit_service.log_action(
        db, AuditAction.USER_CREATED, ActorType.SYSTEM, actor_id=user.id,
    )
    return user


@router.post("/otp/request")
async def request_otp(body: OTPRequest, db: DbSession):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if user.status == UserStatus.LOCKED:
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_423_LOCKED, "Account locked. Try again later.")
        user.status = UserStatus.ACTIVE
        user.failed_otp_attempts = 0
        user.locked_until = None

    otp = _generate_otp()
    user.otp_hash = hash_otp(otp)
    user.otp_expires_at = datetime.now(timezone.utc) + timedelta(seconds=settings.OTP_EXPIRY_SECONDS)
    # In production, send OTP via SES/SNS. For dev, log it.
    return {"message": "OTP sent to your email", "otp_debug": otp if settings.DEBUG else None}


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp_endpoint(body: OTPVerifyRequest, db: DbSession):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    if user.status == UserStatus.LOCKED:
        raise HTTPException(status.HTTP_423_LOCKED, "Account locked")

    if not user.otp_hash or not user.otp_expires_at:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No OTP requested")

    if user.otp_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "OTP expired. Request a new one.")

    if not verify_otp(body.otp, user.otp_hash):
        user.failed_otp_attempts += 1
        if user.failed_otp_attempts >= settings.MAX_OTP_ATTEMPTS:
            user.status = UserStatus.LOCKED
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.LOCKOUT_MINUTES)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect OTP")

    # Success
    user.failed_otp_attempts = 0
    user.otp_hash = None
    user.otp_expires_at = None
    user.last_login_at = datetime.now(timezone.utc)

    token = create_access_token(user.id, user.role.value)
    return TokenResponse(access_token=token, role=user.role.value, user_id=user.id)


@router.post("/login", response_model=dict)
async def login(body: LoginRequest, db: DbSession):
    """Alias for request_otp for login flow."""
    return await request_otp(OTPRequest(email=body.email), db)


@router.get("/me", response_model=UserResponse)
async def get_me(
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER, Role.REVIEWER, Role.APPROVER, Role.ADMIN, Role.COMPLIANCE)),
):
    result = await db.execute(select(User).where(User.id == int(current_user["sub"])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    body: UserRoleUpdate,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.ADMIN)),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    old_role = user.role.value
    user.role = UserRole(body.role)

    await audit_service.log_action(
        db, AuditAction.USER_ROLE_CHANGED, ActorType.ADMIN,
        actor_id=int(current_user["sub"]),
        before_state={"role": old_role},
        after_state={"role": body.role},
    )
    return user
