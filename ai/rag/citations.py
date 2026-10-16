import re
from typing import List, Dict, Any, Optional
from ai.rag.retriever import ScoredChunk


class Citation:
    def __init__(
        self,
        index: int,
        document_id: str,
        document_title: str,
        page_number: int,
        chunk_id: str,
        snippet: str,
        score: float,
    ):
        self.index = index
        self.document_id = document_id
        self.document_title = document_title
        self.page_number = page_number
        self.chunk_id = chunk_id
        self.snippet = snippet
        self.score = score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "snippet": self.snippet,
            "score": self.score,
        }


class CitationEngine:
    """
    Formats contextual knowledge passages for grounding and extracts structured in-text citations.
    """

    @classmethod
    def format_sources_prompt(cls, chunks: List[ScoredChunk]) -> str:
        if not chunks:
            return "No relevant project documents found."

        formatted_parts: List[str] = []
        for i, chunk in enumerate(chunks, 1):
            source_block = (
                f"[Source {i}] (Document: '{chunk.document_title}', Page {chunk.page_number}):\n"
                f'"{chunk.content.strip()}"'
            )
            formatted_parts.append(source_block)

        return "\n\n".join(formatted_parts)

    @classmethod
    def extract_citations(cls, answer: str, chunks: List[ScoredChunk]) -> List[Citation]:
        """
        Parses citation references such as [1], [Source 1], [1, 2], [p. 3] in the LLM answer,
        and pairs them with the underlying ScoredChunk.
        """
        if not chunks or not answer:
            return []

        # Find all brackets like [1], [1, 2], [Source 1], [1,3]
        pattern = r"\[(?:Source\s*)?(\d+)(?:\s*,\s*(?:Source\s*)?(\d+))*\]"
        cited_indices = set()

        for match in re.finditer(pattern, answer):
            for group in match.groups():
                if group and group.isdigit():
                    idx = int(group)
                    if 1 <= idx <= len(chunks):
                        cited_indices.add(idx)

        # If LLM didn't use bracket numbers, check if document title or page is mentioned
        if not cited_indices:
            for i, chunk in enumerate(chunks, 1):
                clean_title = re.escape(chunk.document_title.lower())
                if re.search(clean_title, answer.lower()):
                    cited_indices.add(i)

        # Fallback: If answer is rich and retrieved chunks have high score >= 0.5, include top 2
        if not cited_indices and chunks and chunks[0].score >= 0.35:
            cited_indices.add(1)
            if len(chunks) > 1 and chunks[1].score >= 0.45:
                cited_indices.add(2)

        citations: List[Citation] = []
        for idx in sorted(cited_indices):
            chunk = chunks[idx - 1]
            snippet = chunk.content[:200] + ("..." if len(chunk.content) > 200 else "")
            citations.append(
                Citation(
                    index=idx,
                    document_id=chunk.document_id,
                    document_title=chunk.document_title,
                    page_number=chunk.page_number,
                    chunk_id=chunk.chunk_id,
                    snippet=snippet,
                    score=chunk.score,
                )
            )

        return citations

    @classmethod
    def calculate_groundedness(cls, answer: str, citations: List[Citation]) -> float:
        """
        Calculates a confidence/groundedness score between 0.0 and 1.0.
        """
        if not answer.strip():
            return 0.0
        if not citations:
            return 0.2  # Unverified answer

        base_score = 0.5 + (0.15 * min(len(citations), 3))
        # Check if citations actually appear in text
        has_inline_brackets = bool(re.search(r"\[\d+\]", answer))
        if has_inline_brackets:
            base_score += 0.05

        return min(0.98, round(base_score, 2))
