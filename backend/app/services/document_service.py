"""Document service — upload, validation, S3 storage. US-007, US-008."""

import hashlib
import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.models.document import Document, DocumentStatus, FileType

MIME_TO_FILE_TYPE = {
    "application/pdf": FileType.PDF,
    "image/jpeg": FileType.JPG,
    "image/png": FileType.PNG,
}

MAGIC_BYTES = {
    FileType.PDF: b"%PDF",
    FileType.JPG: b"\xff\xd8\xff",
    FileType.PNG: b"\x89PNG",
}


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s\-.]", "", name)
    name = name.replace("..", "").replace("/", "").replace("\\", "")
    return name.strip()[:255]


def validate_file(content_type: str, size: int, file_header: bytes) -> FileType:
    if content_type not in MIME_TO_FILE_TYPE:
        raise ValueError(f"Unsupported file type. Allowed: PDF, JPG, PNG")

    if size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise ValueError(f"File exceeds maximum size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024*1024)} MB")

    file_type = MIME_TO_FILE_TYPE[content_type]
    expected_magic = MAGIC_BYTES[file_type]
    if not file_header.startswith(expected_magic):
        raise ValueError("File content does not match declared type")

    return file_type


def compute_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def create_document_record(
    db: AsyncSession,
    application_id: int,
    file_name: str,
    file_type: FileType,
    file_size: int,
    content_hash: str,
) -> Document:
    safe_name = sanitize_filename(file_name)
    storage_path = f"uploads/{application_id}/{safe_name}"
    doc = Document(
        application_id=application_id,
        file_name=safe_name,
        file_type=file_type,
        file_size_bytes=file_size,
        storage_path=storage_path,
        content_hash=content_hash,
        status=DocumentStatus.UPLOADED,
        uploaded_at=datetime.now(timezone.utc),
    )
    db.add(doc)
    await db.flush()
    return doc


async def get_application_documents(db: AsyncSession, application_id: int) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.application_id == application_id, Document.status != DocumentStatus.DELETED)
    )
    return list(result.scalars().all())


async def soft_delete_document(db: AsyncSession, document_id: int) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc:
        doc.status = DocumentStatus.DELETED
