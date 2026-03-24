"""Admin configuration service — thresholds, workflow config. US-014, US-027, US-028."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.threshold_config import ThresholdConfig
from backend.app.models.workflow_config import WorkflowConfig

DEFAULT_THRESHOLDS = [
    {"band_name": "auto_approve", "min_score": 91, "max_score": 100},
    {"band_name": "approver_only", "min_score": 80, "max_score": 90},
    {"band_name": "reviewer_approver", "min_score": 70, "max_score": 79},
    {"band_name": "auto_reject", "min_score": 0, "max_score": 69},
]

DEFAULT_WORKFLOW_NODES = [
    "start", "llm_evaluation", "decision", "auto_approval",
    "reviewer", "approver", "rejection", "notification", "completed",
]


async def get_thresholds(db: AsyncSession) -> list[ThresholdConfig]:
    result = await db.execute(select(ThresholdConfig).order_by(ThresholdConfig.min_score.desc()))
    return list(result.scalars().all())


async def update_threshold(
    db: AsyncSession, band_name: str, min_score: int, max_score: int, admin_id: int
) -> ThresholdConfig:
    if min_score > max_score:
        raise ValueError("min_score cannot exceed max_score")

    result = await db.execute(
        select(ThresholdConfig).where(ThresholdConfig.band_name == band_name)
    )
    config = result.scalar_one_or_none()
    if not config:
        config = ThresholdConfig(band_name=band_name, min_score=min_score, max_score=max_score, updated_by=admin_id)
        db.add(config)
    else:
        config.min_score = min_score
        config.max_score = max_score
        config.updated_by = admin_id
    await db.flush()
    return config


async def seed_defaults(db: AsyncSession) -> None:
    existing = await db.execute(select(ThresholdConfig))
    if not existing.scalars().first():
        for t in DEFAULT_THRESHOLDS:
            db.add(ThresholdConfig(**t))
        for node in DEFAULT_WORKFLOW_NODES:
            db.add(WorkflowConfig(node_name=node, is_enabled=True))
        await db.flush()


async def get_workflow_configs(db: AsyncSession) -> list[WorkflowConfig]:
    result = await db.execute(select(WorkflowConfig))
    return list(result.scalars().all())


async def update_workflow_config(
    db: AsyncSession, node_name: str, is_enabled: bool, admin_id: int
) -> WorkflowConfig:
    result = await db.execute(
        select(WorkflowConfig).where(WorkflowConfig.node_name == node_name)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise ValueError(f"Unknown workflow node: {node_name}")
    config.is_enabled = is_enabled
    config.updated_by = admin_id
    await db.flush()
    return config
