import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.rag import Document, DocumentChunk


class RAGRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(
        self,
        project_id: uuid.UUID,
        uploader_id: uuid.UUID,
        title: str,
        file_name: str,
        file_url: str,
        file_type: str = "pdf",
        file_size_bytes: int = 0,
        status: str = "pending",
    ) -> Document:
        doc = Document(
            id=uuid.uuid4(),
            project_id=project_id,
            uploader_id=uploader_id,
            title=title,
            file_name=file_name,
            file_url=file_url,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            status=status,
            total_pages=1,
            total_chunks=0,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_document(self, document_id: uuid.UUID) -> Optional[Document]:
        stmt = (
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.uploader))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_project_documents(self, project_id: uuid.UUID) -> List[Document]:
        stmt = (
            select(Document)
            .where(Document.id == project_id)
            .order_by(desc(Document.created_at))
            .options(selectinload(Document.uploader))
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update_document_status(
        self,
        document_id: uuid.UUID,
        status: str,
        total_pages: int = 1,
        total_chunks: int = 0,
        error_message: Optional[str] = None,
    ) -> Optional[Document]:
        doc = await self.get_document(document_id)
        if not doc:
            return None
        doc.status = status
        doc.total_pages = total_pages
        doc.total_chunks = total_chunks
        doc.error_message = error_message
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def delete_document(self, document_id: uuid.UUID) -> bool:
        doc = await self.get_document(document_id)
        if not doc:
            return False
        await self.db.delete(doc)
        await self.db.commit()
        return True

    async def create_chunks(self, chunks_data: List[Dict[str, Any]]) -> List[DocumentChunk]:
        created: List[DocumentChunk] = []
        for c in chunks_data:
            chunk = DocumentChunk(
                id=uuid.uuid4(),
                document_id=c["document_id"],
                project_id=c["project_id"],
                chunk_index=c.get("chunk_index", 0),
                content=c["content"],
                page_number=c.get("page_number", 1),
                token_count=c.get("token_count", 0),
                embedding=c.get("embedding"),
                metadata_json=c.get("metadata_json") or {},
            )
            self.db.add(chunk)
            created.append(chunk)

        await self.db.commit()
        return created

    async def get_project_chunks(
        self,
        project_id: uuid.UUID,
        document_ids: Optional[List[uuid.UUID]] = None,
    ) -> List[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.project_id == project_id)
            .options(selectinload(DocumentChunk.document))
        )
        if document_ids:
            stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_document_chunks(self, document_id: uuid.UUID) -> List[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
