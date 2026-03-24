"""Admin config schemas — thresholds, workflow config."""

from pydantic import BaseModel, Field


class ThresholdConfigResponse(BaseModel):
    id: int
    band_name: str
    min_score: int
    max_score: int

    model_config = {"from_attributes": True}


class ThresholdUpdateRequest(BaseModel):
    band_name: str
    min_score: int = Field(..., ge=0, le=100)
    max_score: int = Field(..., ge=0, le=100)


class WorkflowConfigResponse(BaseModel):
    id: int
    node_name: str
    is_enabled: bool

    model_config = {"from_attributes": True}


class WorkflowConfigUpdateRequest(BaseModel):
    node_name: str
    is_enabled: bool
