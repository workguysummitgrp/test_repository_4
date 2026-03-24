"""Review and approval schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class ReviewerDecisionRequest(BaseModel):
    decision: str = Field(..., pattern=r"^(approved|rejected)$")
    comment: str | None = None


class ReviewerCommentRequest(BaseModel):
    comment: str = Field(..., min_length=1, max_length=5000)


class ReviewerDecisionResponse(BaseModel):
    id: int
    application_id: int
    reviewer_id: int
    decision: str
    comment: str | None = None
    assigned_at: datetime
    decided_at: datetime | None = None

    model_config = {"from_attributes": True}


class ApproverDecisionRequest(BaseModel):
    decision: str = Field(..., pattern=r"^(approved|rejected)$")
    comment: str = Field(..., min_length=1, max_length=5000)


class ApproverDecisionResponse(BaseModel):
    id: int
    application_id: int
    approver_id: int
    decision: str
    comment: str
    source: str
    assigned_at: datetime
    decided_at: datetime | None = None

    model_config = {"from_attributes": True}
