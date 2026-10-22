import re
from typing import List, Dict, Any, Optional
from ai.rag.parser import ParsedPage


class TextChunk:
    def __init__(
        self,
        content: str,
        page_number: int = 1,
        chunk_index: int = 0,
        token_count: int = 0,
        heading: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.content = content.strip()
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.token_count = token_count or max(1, len(self.content.split()))
        self.heading = heading
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "token_count": self.token_count,
            "heading": self.heading,
            "metadata": self.metadata,
        }


class DocumentChunker:
    """
    Recursive character and sentence chunker with sliding window overlap.
    Preserves page boundaries and section headings.
    """

    def __init__(self, chunk_size: int = 700, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: List[ParsedPage]) -> List[TextChunk]:
        all_chunks: List[TextChunk] = []
        global_chunk_idx = 0

        for page in pages:
            text = page.text.strip()
            if not text:
                continue

            page_chunks = self._split_text(text, page.page_number, page.heading)
            for chunk_str in page_chunks:
                if not chunk_str.strip():
                    continue
                words = chunk_str.split()
                token_count = len(words)
                
                chunk = TextChunk(
                    content=chunk_str,
                    page_number=page.page_number,
                    chunk_index=global_chunk_idx,
                    token_count=token_count,
                    heading=page.heading,
                    metadata={
                        "page": page.page_number,
                        "heading": page.heading,
                        "char_count": len(chunk_str),
                    }
                )
                all_chunks.append(chunk)
                global_chunk_idx += 1

        return all_chunks

    def _split_text(self, text: str, page_number: int, heading: str) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        # Break text into paragraphs first
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks: List[str] = []
        current_chunk = ""

        for para in paragraphs:
            # If paragraph fits in current chunk
            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk = f"{current_chunk}\n\n{para}".strip()
            else:
                # If current chunk has content, save it
                if current_chunk:
                    chunks.append(current_chunk)
                    # Create overlap from end of current chunk
                    overlap_seed = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else ""
                    current_chunk = f"{overlap_seed}\n\n{para}".strip() if overlap_seed else para
                else:
                    # Paragraph is longer than chunk_size, split by sentences
                    sentence_chunks = self._split_large_paragraph(para)
                    chunks.extend(sentence_chunks[:-1])
                    current_chunk = sentence_chunks[-1] if sentence_chunks else ""

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        # Split by sentences (. ! ? followed by space)
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        chunks: List[str] = []
        current = ""

        for s in sentences:
            if len(current) + len(s) + 1 <= self.chunk_size:
                current = f"{current} {s}".strip()
            else:
                if current:
                    chunks.append(current)
                if len(s) > self.chunk_size:
                    # Hard slice if a single sentence is massive
                    for i in range(0, len(s), self.chunk_size - self.chunk_overlap):
                        chunks.append(s[i : i + self.chunk_size])
                    current = ""
                else:
                    current = s

        if current.strip():
            chunks.append(current.strip())

        return chunks
