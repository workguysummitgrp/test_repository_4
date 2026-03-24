"""Evaluation schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    score: int = Field(..., ge=0, le=100)
    confidence: str = Field(..., pattern=r"^(low|medium|high)$")
    summary: str
    flags: list[str] = []


class EvaluationResponse(BaseModel):
    id: int
    application_id: int
    score: int
    confidence: str
    summary: str
    flags: list[Any]
    model_version: str
    temperature: float
    retry_count: int
    is_valid: bool
    evaluated_at: datetime

    model_config = {"from_attributes": True}


class EvaluationDetailResponse(EvaluationResponse):
    raw_input: dict[str, Any]
    raw_output: dict[str, Any]
    validation_errors: dict[str, Any] | None = None
