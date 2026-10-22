import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.rag_service import RAGService
from app.repositories.rag_repo import RAGRepository
from app.schemas.rag import (
    DocumentResponse,
    DocumentChunkResponse,
    RAGQueryRequest,
    RAGQueryResponse,
    DocumentUploadResponse,
)

router = APIRouter(prefix="", tags=["RAG & Knowledge Vault"])
rag_service = RAGService()


@router.post(
    "/projects/{project_id}/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a project document (PDF, Markdown, Code, Plain Text) to the project's Knowledge Vault.
    Automatically parses pages, sections, generates recursive semantic chunks, and calculates vector embeddings.
    """
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    doc = await rag_service.upload_and_index_document(
        project_id=project_id,
        uploader_id=current_user.id,
        file_name=file.filename or "uploaded_file",
        content_bytes=content,
        title=title,
        db=db,
    )

    return DocumentUploadResponse(
        document=DocumentResponse.model_validate(doc),
        message=f"Document '{doc.title}' successfully uploaded and indexed into {doc.total_chunks} chunks.",
    )


@router.get(
    "/projects/{project_id}/documents",
    response_model=List[DocumentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_project_documents(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve all indexed research papers and documents belonging to this project.
    """
    rag_repo = RAGRepository(db)
    docs = await rag_repo.list_project_documents(project_id)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.get(
    "/projects/{project_id}/documents/{document_id}",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve metadata for a specific uploaded document.
    """
    rag_repo = RAGRepository(db)
    doc = await rag_repo.get_document(document_id)
    if not doc or doc.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    return DocumentResponse.model_validate(doc)


@router.get(
    "/projects/{project_id}/documents/{document_id}/chunks",
    response_model=List[DocumentChunkResponse],
    status_code=status.HTTP_200_OK,
)
async def get_document_chunks(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Inspect the generated vector chunks, token counts, and page mappings for a document.
    """
    rag_repo = RAGRepository(db)
    chunks = await rag_repo.get_document_chunks(document_id)
    return [DocumentChunkResponse.model_validate(c) for c in chunks]


@router.delete(
    "/projects/{project_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    project_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document and purge all its vector chunks from the Knowledge Vault.
    """
    rag_repo = RAGRepository(db)
    doc = await rag_repo.get_document(document_id)
    if not doc or doc.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )
    await rag_repo.delete_document(document_id)
    return None


@router.post(
    "/projects/{project_id}/rag/query",
    response_model=RAGQueryResponse,
    status_code=status.HTTP_200_OK,
)
async def query_project_rag(
    project_id: uuid.UUID,
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Perform a hybrid dense+sparse vector search across project documents and generate a verified,
    grounded answer with in-text citation references.
    """
    return await rag_service.query_rag(
        project_id=project_id,
        request=request,
        db=db,
    )


@router.post(
    "/projects/{project_id}/rag/stream",
    status_code=status.HTTP_200_OK,
)
async def stream_project_rag(
    project_id: uuid.UUID,
    request: RAGQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Stream a grounded RAG research answer in real-time via Server-Sent Events (SSE).
    """
    return StreamingResponse(
        rag_service.stream_rag(
            project_id=project_id,
            request=request,
            db=db,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
