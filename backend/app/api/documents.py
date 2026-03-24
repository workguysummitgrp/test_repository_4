"""Documents API — upload, list, delete. US-007, US-008."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status

from backend.app.core.dependencies import DbSession
from backend.app.core.security import Role, require_roles
from backend.app.schemas.document import DocumentResponse
from backend.app.services import document_service, form_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/{app_id}/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    app_id: str,
    file: UploadFile,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER)),
):
    user_id = int(current_user["sub"])
    application = await form_service.get_application_by_id(db, app_id)
    if not application:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    if application.user_id != user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Access denied")

    content = await file.read()
    file_header = content[:8]
    content_type = file.content_type or "application/octet-stream"

    try:
        file_type = document_service.validate_file(content_type, len(content), file_header)
    except ValueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc

    content_hash = document_service.compute_hash(content)

    doc = await document_service.create_document_record(
        db, application.id, file.filename or "unnamed", file_type, len(content), content_hash,
    )
    # In production, upload to S3 here.
    return doc


@router.get("/{app_id}", response_model=list[DocumentResponse])
async def list_documents(
    app_id: str,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER, Role.REVIEWER, Role.APPROVER, Role.COMPLIANCE)),
):
    application = await form_service.get_application_by_id(db, app_id)
    if not application:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    return await document_service.get_application_documents(db, application.id)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: int,
    db: DbSession,
    current_user: dict = Depends(require_roles(Role.CUSTOMER)),
):
    await document_service.soft_delete_document(db, doc_id)
