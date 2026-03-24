"""Form service — application creation, draft management, submission. US-004, US-005, US-006, US-009."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.application import Application, ApplicationStatus
from backend.app.models.application_draft import ApplicationDraft


async def get_next_application_id(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(Application.id)))
    count = result.scalar_one() + 1
    return f"APP-{count:03d}"


async def create_application(db: AsyncSession, user_id: int, form_data: dict) -> Application:
    app_id = await get_next_application_id(db)
    application = Application(
        application_id=app_id,
        user_id=user_id,
        status=ApplicationStatus.DRAFT,
        form_data=form_data,
    )
    db.add(application)
    await db.flush()
    return application


async def submit_application(db: AsyncSession, application: Application) -> Application:
    application.status = ApplicationStatus.SUBMITTED
    application.submitted_at = datetime.now(timezone.utc)
    await db.flush()
    return application


async def get_application_by_id(db: AsyncSession, app_id: str) -> Application | None:
    result = await db.execute(
        select(Application).where(Application.application_id == app_id)
    )
    return result.scalar_one_or_none()


async def get_user_applications(
    db: AsyncSession, user_id: int, page: int = 1, size: int = 20
) -> tuple[list[Application], int]:
    count_result = await db.execute(
        select(func.count(Application.id)).where(Application.user_id == user_id)
    )
    total = count_result.scalar_one()
    result = await db.execute(
        select(Application)
        .where(Application.user_id == user_id)
        .order_by(Application.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    return list(result.scalars().all()), total


async def save_draft(
    db: AsyncSession, user_id: int, form_data: dict, current_step: int
) -> ApplicationDraft:
    result = await db.execute(
        select(ApplicationDraft).where(ApplicationDraft.user_id == user_id)
    )
    draft = result.scalar_one_or_none()
    if draft:
        draft.form_data = form_data
        draft.current_step = current_step
        draft.last_saved_at = datetime.now(timezone.utc)
    else:
        draft = ApplicationDraft(
            user_id=user_id,
            form_data=form_data,
            current_step=current_step,
        )
        db.add(draft)
    await db.flush()
    return draft


async def get_draft(db: AsyncSession, user_id: int) -> ApplicationDraft | None:
    result = await db.execute(
        select(ApplicationDraft).where(ApplicationDraft.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def delete_draft(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(
        select(ApplicationDraft).where(ApplicationDraft.user_id == user_id)
    )
    draft = result.scalar_one_or_none()
    if draft:
        await db.delete(draft)
