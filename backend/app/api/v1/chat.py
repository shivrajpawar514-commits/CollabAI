import os
import uuid
import shutil
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.chat import MessageCreate, MessageResponse, FileAttachmentResponse
from app.services.chat_service import ChatService

router = APIRouter(tags=["Real-Time Chat & File Attachments"])

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_FILE_SIZE = 20 * 1024 * 1024 # 20MB limit


@router.get("/projects/{project_id}/messages", response_model=List[MessageResponse])
async def get_project_messages(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve message history for a project chat room."""
    service = ChatService(db)
    return await service.get_messages(project_id)


@router.post("/projects/{project_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def post_message(
    project_id: uuid.UUID,
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Post a message to the project chat room and broadcast to connected peers."""
    service = ChatService(db)
    return await service.post_message(project_id, current_user.id, msg_in)


@router.get("/projects/{project_id}/files", response_model=List[FileAttachmentResponse])
async def list_project_files(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all uploaded files and attachments for a project."""
    service = ChatService(db)
    return await service.get_files(project_id)


@router.post("/projects/{project_id}/files/upload", response_model=FileAttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload project document or asset (Max 20MB)."""
    # Read file content safely with size check
    contents = await file.read()
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of 20MB (received {round(file_size / (1024 * 1024), 2)}MB)."
        )

    ext = os.path.splitext(file.filename or "")[1]
    safe_filename = f"{uuid.uuid4()}{ext}"
    project_upload_dir = os.path.join(UPLOAD_DIR, str(project_id))
    os.makedirs(project_upload_dir, exist_ok=True)
    file_path = os.path.join(project_upload_dir, safe_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    file_url = f"/uploads/{project_id}/{safe_filename}"

    service = ChatService(db)
    return await service.register_file(
        project_id=project_id,
        uploader_id=current_user.id,
        file_name=file.filename or "attachment",
        file_url=file_url,
        file_size_bytes=file_size,
        content_type=file.content_type or "application/octet-stream"
    )
