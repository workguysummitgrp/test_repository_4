"""LangGraph workflow state definition — US-012."""

from typing import Any
from pydantic import BaseModel, Field


class OnboardingState(BaseModel):
    """State passed between LangGraph nodes."""
    application_id: int
    application_str_id: str = ""
    user_id: int = 0
    form_data: dict[str, Any] = Field(default_factory=dict)
    doc_metadata: list[dict[str, Any]] = Field(default_factory=list)
    score: int | None = None
    confidence: str | None = None
    summary: str | None = None
    flags: list[str] = Field(default_factory=list)
    decision_route: str | None = None
    reviewer_decision: str | None = None
    approver_decision: str | None = None
    current_node: str = "start"
    is_valid_evaluation: bool = True
    error: str | None = None
