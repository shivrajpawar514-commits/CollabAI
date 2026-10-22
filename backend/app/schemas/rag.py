from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class DocumentBase(BaseModel):
    title: str = Field(..., max_length=255)
    file_type: str = Field("pdf", max_length=50)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    uploader_id: UUID
    title: str
    file_name: str
    file_url: str
    file_type: str
    file_size_bytes: int
    total_pages: int
    total_chunks: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    project_id: UUID
    chunk_index: int
    content: str
    page_number: int
    token_count: int
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class CitationItem(BaseModel):
    index: int
    document_id: UUID
    document_title: str
    page_number: int
    chunk_id: UUID
    snippet: str
    score: float


class RAGQueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(5, ge=1, le=15)
    document_ids: Optional[List[UUID]] = None
    stream: bool = False


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    groundedness_score: float
    citations: List[CitationItem] = []
    retrieved_chunks: List[DocumentChunkResponse] = []


class DocumentUploadResponse(BaseModel):
    document: DocumentResponse
    message: str = "Document uploaded successfully and queued for indexing."
