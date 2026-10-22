import os
import sys
import uuid
import json
import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from ai.client import LLMClient
from ai.rag.parser import DocumentParser
from ai.rag.chunker import DocumentChunker
from ai.rag.embeddings import EmbeddingClient
from ai.rag.retriever import HybridRetriever, ScoredChunk
from ai.rag.citations import CitationEngine, Citation
from ai.prompts.rag_assistant import SYSTEM_RAG_RESEARCH_PROMPT, format_rag_prompt

from app.models.rag import Document, DocumentChunk
from app.models.project import Project
from app.repositories.rag_repo import RAGRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.rag import (
    DocumentResponse,
    DocumentChunkResponse,
    CitationItem,
    RAGQueryRequest,
    RAGQueryResponse,
)

logger = logging.getLogger("collabai.rag")


class RAGService:
    def __init__(self):
        self.llm = LLMClient()
        self.chunker = DocumentChunker(chunk_size=700, chunk_overlap=120)
        self.embedding_client = EmbeddingClient()
        self.retriever = HybridRetriever(dense_weight=0.7, sparse_weight=0.3)
        self.upload_root = os.path.join(ROOT_DIR, "backend", "uploads", "rag")
        os.makedirs(self.upload_root, exist_ok=True)

    async def upload_and_index_document(
        self,
        project_id: uuid.UUID,
        uploader_id: uuid.UUID,
        file_name: str,
        content_bytes: bytes,
        title: Optional[str] = None,
        db: Optional[AsyncSession] = None,
    ) -> Document:
        if not db:
            raise ValueError("Database session required")

        # 1. Check project exists
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # 2. Determine file type & clean title
        ext = os.path.splitext(file_name)[1].lower().replace(".", "")
        if not ext:
            ext = "txt"
        doc_title = title.strip() if title and title.strip() else os.path.splitext(file_name)[0]

        # 3. Save file locally
        proj_dir = os.path.join(self.upload_root, str(project_id))
        os.makedirs(proj_dir, exist_ok=True)
        unique_file_name = f"{uuid.uuid4().hex[:8]}_{file_name}"
        saved_file_path = os.path.join(proj_dir, unique_file_name)

        with open(saved_file_path, "wb") as f:
            f.write(content_bytes)

        file_url = f"/uploads/rag/{project_id}/{unique_file_name}"
        file_size = len(content_bytes)

        # 4. Create document row in database
        rag_repo = RAGRepository(db)
        document = await rag_repo.create_document(
            project_id=project_id,
            uploader_id=uploader_id,
            title=doc_title,
            file_name=file_name,
            file_url=file_url,
            file_type=ext,
            file_size_bytes=file_size,
            status="processing",
        )

        # 5. Extract, Chunk, and Embed
        try:
            parsed_pages = DocumentParser.parse_file(saved_file_path, file_type=ext)
            chunks = self.chunker.chunk_pages(parsed_pages)

            if not chunks:
                # Fallback if file was empty or parsed minimal content
                from ai.rag.chunker import TextChunk
                chunks = [
                    TextChunk(
                        content=f"Document '{doc_title}' uploaded without readable textual content.",
                        page_number=1,
                        chunk_index=0,
                        token_count=10,
                    )
                ]

            # Generate dense embeddings for all chunk texts
            chunk_texts = [c.content for c in chunks]
            embeddings = self.embedding_client.embed_documents(chunk_texts)

            chunks_data = []
            for i, c in enumerate(chunks):
                chunks_data.append({
                    "document_id": document.id,
                    "project_id": project_id,
                    "chunk_index": c.chunk_index,
                    "content": c.content,
                    "page_number": c.page_number,
                    "token_count": c.token_count,
                    "embedding": embeddings[i] if i < len(embeddings) else None,
                    "metadata_json": {
                        "heading": c.heading,
                        "file_name": file_name,
                        "doc_title": doc_title,
                    },
                })

            await rag_repo.create_chunks(chunks_data)
            await rag_repo.update_document_status(
                document_id=document.id,
                status="indexed",
                total_pages=len(parsed_pages),
                total_chunks=len(chunks),
            )
            logger.info(f"Successfully indexed document {document.id} with {len(chunks)} chunks.")
            return document

        except Exception as e:
            logger.exception(f"Failed to process and index document {document.id}: {e}")
            await rag_repo.update_document_status(
                document_id=document.id,
                status="failed",
                error_message=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to index document: {str(e)}"
            )

    async def query_rag(
        self,
        project_id: uuid.UUID,
        request: RAGQueryRequest,
        db: AsyncSession,
    ) -> RAGQueryResponse:
        rag_repo = RAGRepository(db)
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

        # 1. Fetch project chunks
        db_chunks = await rag_repo.get_project_chunks(
            project_id=project_id,
            document_ids=request.document_ids,
        )

        if not db_chunks:
            return RAGQueryResponse(
                query=request.query,
                answer=(
                    "No indexed documents were found in this project's Knowledge Vault. "
                    "Please upload research papers, project briefs, API specs, or notes to ask questions."
                ),
                groundedness_score=0.0,
                citations=[],
                retrieved_chunks=[],
            )

        # 2. Build candidate dicts
        candidates = []
        for c in db_chunks:
            doc_title = c.document.title if c.document else "Project Document"
            candidates.append({
                "id": str(c.id),
                "document_id": str(c.document_id),
                "document_title": doc_title,
                "content": c.content,
                "page_number": c.page_number,
                "chunk_index": c.chunk_index,
                "embedding": c.embedding,
                "metadata_json": c.metadata_json or {},
            })

        # 3. Dense & Hybrid retrieval
        query_vector = self.embedding_client.embed_query(request.query)
        retrieved = self.retriever.retrieve(
            query=request.query,
            query_vector=query_vector,
            candidates=candidates,
            top_k=request.top_k,
            min_score=0.05,
        )

        if not retrieved:
            # Fallback to top candidate if min_score filtered all out
            retrieved = self.retriever.retrieve(
                query=request.query,
                query_vector=query_vector,
                candidates=candidates,
                top_k=min(3, len(candidates)),
                min_score=0.0,
            )

        # 4. Format prompt
        sources_context = CitationEngine.format_sources_prompt(retrieved)
        prompt = format_rag_prompt(
            query=request.query,
            sources_context=sources_context,
            project_title=project.title,
        )

        # 5. Generate answer
        answer = await self.llm.generate(
            prompt=prompt,
            system_instruction=SYSTEM_RAG_RESEARCH_PROMPT,
            temperature=0.2,
            max_tokens=1200,
        )

        # 6. Extract citations & score
        citations_data = CitationEngine.extract_citations(answer, retrieved)
        groundedness = CitationEngine.calculate_groundedness(answer, citations_data)

        # Build schema items
        citation_items = [
            CitationItem(
                index=c.index,
                document_id=uuid.UUID(c.document_id),
                document_title=c.document_title,
                page_number=c.page_number,
                chunk_id=uuid.UUID(c.chunk_id),
                snippet=c.snippet,
                score=c.score,
            )
            for c in citations_data
        ]

        # Map retrieved chunks to response schema
        chunk_map = {str(c.id): c for c in db_chunks}
        retrieved_chunk_items = []
        for r in retrieved:
            if r.chunk_id in chunk_map:
                retrieved_chunk_items.append(
                    DocumentChunkResponse.model_validate(chunk_map[r.chunk_id])
                )

        return RAGQueryResponse(
            query=request.query,
            answer=answer,
            groundedness_score=groundedness,
            citations=citation_items,
            retrieved_chunks=retrieved_chunk_items,
        )

    async def stream_rag(
        self,
        project_id: uuid.UUID,
        request: RAGQueryRequest,
        db: AsyncSession,
    ) -> AsyncGenerator[str, None]:
        rag_repo = RAGRepository(db)
        project_repo = ProjectRepository(db)
        project = await project_repo.get_by_id(project_id)
        if not project:
            yield f"data: {json.dumps({'error': 'Project not found'})}\n\n"
            return

        db_chunks = await rag_repo.get_project_chunks(
            project_id=project_id,
            document_ids=request.document_ids,
        )

        if not db_chunks:
            yield f"data: {json.dumps({'type': 'token', 'content': 'No indexed documents found in this project. Please upload documents first.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            return

        candidates = []
        for c in db_chunks:
            doc_title = c.document.title if c.document else "Project Document"
            candidates.append({
                "id": str(c.id),
                "document_id": str(c.document_id),
                "document_title": doc_title,
                "content": c.content,
                "page_number": c.page_number,
                "chunk_index": c.chunk_index,
                "embedding": c.embedding,
                "metadata_json": c.metadata_json or {},
            })

        query_vector = self.embedding_client.embed_query(request.query)
        retrieved = self.retriever.retrieve(
            query=request.query,
            query_vector=query_vector,
            candidates=candidates,
            top_k=request.top_k,
            min_score=0.05,
        )
        if not retrieved:
            retrieved = self.retriever.retrieve(
                query=request.query,
                query_vector=query_vector,
                candidates=candidates,
                top_k=min(3, len(candidates)),
                min_score=0.0,
            )

        # Notify frontend of retrieval
        yield f"data: {json.dumps({'type': 'retrieval', 'count': len(retrieved)})}\n\n"

        sources_context = CitationEngine.format_sources_prompt(retrieved)
        prompt = format_rag_prompt(
            query=request.query,
            sources_context=sources_context,
            project_title=project.title,
        )

        full_answer = ""
        async for token in self.llm.generate_stream(
            prompt=prompt,
            system_instruction=SYSTEM_RAG_RESEARCH_PROMPT,
            temperature=0.2,
            max_tokens=1200,
        ):
            full_answer += token
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        # Citations & groundedness calculation
        citations_data = CitationEngine.extract_citations(full_answer, retrieved)
        groundedness = CitationEngine.calculate_groundedness(full_answer, citations_data)

        yield f"data: {json.dumps({'type': 'citations', 'citations': [c.to_dict() for c in citations_data], 'groundedness_score': groundedness})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
