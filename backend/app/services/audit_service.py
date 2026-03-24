"""Audit service — immutable audit log. US-025, US-026."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.audit_log import ActorType, AuditAction, AuditLog


async def log_action(
    db: AsyncSession,
    action: AuditAction,
    actor_type: ActorType,
    application_id: int | None = None,
    actor_id: int | None = None,
    before_state: dict[str, Any] | None = None,
    after_state: dict[str, Any] | None = None,
    rationale: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        application_id=application_id,
        actor_id=actor_id,
        actor_type=actor_type,
        action=action,
        before_state=before_state,
        after_state=after_state,
        rationale=rationale,
    )
    db.add(entry)
    await db.flush()
    return entry


async def get_audit_logs(
    db: AsyncSession,
    application_id: int | None = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[AuditLog], int]:
    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))

    if application_id:
        query = query.where(AuditLog.application_id == application_id)
        count_query = count_query.where(AuditLog.application_id == application_id)

    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    result = await db.execute(
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    return list(result.scalars().all()), total
