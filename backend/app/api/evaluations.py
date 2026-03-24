"""Evaluations API — view evaluation results. US-010, US-011."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from backend.app.core.dependencies import DbSession
from backend.app.core.security import Role, require_roles
from backend.app.models.evaluation import Evaluation
from backend.app.schemas.evaluation import EvaluationDetailResponse, EvaluationResponse

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("/{application_id}", response_model=EvaluationResponse)
async def get_evaluation(
    application_id: int,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.REVIEWER, Role.APPROVER, Role.ADMIN, Role.COMPLIANCE)),
):
    result = await db.execute(
        select(Evaluation).where(Evaluation.application_id == application_id)
    )
    evaluation = result.scalar_one_or_none()
    if not evaluation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evaluation not found")
    return evaluation


@router.get("/{application_id}/detail", response_model=EvaluationDetailResponse)
async def get_evaluation_detail(
    application_id: int,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.COMPLIANCE, Role.ADMIN)),
):
    """Full evaluation detail including raw LLM I/O — compliance only."""
    result = await db.execute(
        select(Evaluation).where(Evaluation.application_id == application_id)
    )
    evaluation = result.scalar_one_or_none()
    if not evaluation:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Evaluation not found")
    return evaluation
