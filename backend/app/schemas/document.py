"""Document schemas."""

from datetime import datetime
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    application_id: int
    file_name: str
    file_type: str
    file_size_bytes: int
    status: str
    uploaded_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PresignedUrlResponse(BaseModel):
    upload_url: str
    document_id: int
    expires_in: int
