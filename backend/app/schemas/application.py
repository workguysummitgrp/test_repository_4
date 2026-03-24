"""Application and draft schemas."""

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class ApplicationCreateRequest(BaseModel):
    form_data: dict[str, Any] = Field(..., description="Structured form field values")


class ApplicationResponse(BaseModel):
    id: int
    application_id: str
    user_id: int
    status: str
    form_data: dict[str, Any]
    form_schema_version: str
    submitted_at: datetime | None = None
    decision_at: datetime | None = None
    final_decision: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApplicationListResponse(BaseModel):
    items: list[ApplicationResponse]
    total: int
    page: int
    size: int


class DraftSaveRequest(BaseModel):
    form_data: dict[str, Any]
    current_step: int = Field(..., ge=1, le=4)


class DraftResponse(BaseModel):
    id: int
    user_id: int
    form_data: dict[str, Any]
    current_step: int
    last_saved_at: datetime

    model_config = {"from_attributes": True}
