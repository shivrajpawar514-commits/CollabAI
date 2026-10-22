import math
import re
from typing import List, Dict, Any, Optional, Tuple


class ScoredChunk:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        document_title: str,
        content: str,
        page_number: int,
        chunk_index: int,
        score: float,
        dense_score: float = 0.0,
        sparse_score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_title = document_title
        self.content = content
        self.page_number = page_number
        self.chunk_index = chunk_index
        self.score = round(score, 4)
        self.dense_score = round(dense_score, 4)
        self.sparse_score = round(sparse_score, 4)
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "document_title": self.document_title,
            "content": self.content,
            "page_number": self.page_number,
            "chunk_index": self.chunk_index,
            "score": self.score,
            "dense_score": self.dense_score,
            "sparse_score": self.sparse_score,
            "metadata": self.metadata,
        }


class HybridRetriever:
    """
    Hybrid search engine combining dense vector cosine similarity and sparse BM25 keyword matching.
    """

    def __init__(self, dense_weight: float = 0.7, sparse_weight: float = 0.3):
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight

    def retrieve(
        self,
        query: str,
        query_vector: List[float],
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[ScoredChunk]:
        """
        candidates: List of dicts representing chunks with keys:
          - id, document_id, document_title, content, page_number, chunk_index, embedding, metadata_json
        """
        if not candidates:
            return []

        # 1. Compute Dense Cosine Similarities
        dense_scores: List[float] = []
        for cand in candidates:
            emb = cand.get("embedding")
            if emb and len(emb) == len(query_vector):
                cos_sim = self._cosine_similarity(query_vector, emb)
                dense_scores.append(max(0.0, cos_sim))
            else:
                dense_scores.append(0.0)

        # 2. Compute Sparse BM25 / Keyword Overlap
        sparse_scores = self._compute_bm25_scores(query, [c.get("content", "") for c in candidates])

        # 3. Min-Max Normalize scores to [0.0, 1.0]
        norm_dense = self._min_max_scale(dense_scores)
        norm_sparse = self._min_max_scale(sparse_scores)

        # 4. Hybrid Linear Combination
        scored_results: List[ScoredChunk] = []
        for i, cand in enumerate(candidates):
            fused_score = (self.dense_weight * norm_dense[i]) + (self.sparse_weight * norm_sparse[i])

            if fused_score >= min_score:
                scored_results.append(
                    ScoredChunk(
                        chunk_id=str(cand.get("id", "")),
                        document_id=str(cand.get("document_id", "")),
                        document_title=cand.get("document_title", "Document"),
                        content=cand.get("content", ""),
                        page_number=cand.get("page_number", 1),
                        chunk_index=cand.get("chunk_index", 0),
                        score=fused_score,
                        dense_score=dense_scores[i],
                        sparse_score=sparse_scores[i],
                        metadata=cand.get("metadata_json") or {},
                    )
                )

        # Sort descending by fused score
        scored_results.sort(key=lambda x: x.score, reverse=True)
        return scored_results[:top_k]

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0
        return dot / (norm_a * norm_b)

    @classmethod
    def _compute_bm25_scores(cls, query: str, documents: List[str]) -> List[float]:
        query_terms = [w.lower() for w in re.findall(r"\b\w{2,}\b", query)]
        if not query_terms or not documents:
            return [0.0] * len(documents)

        # Tokenize docs
        doc_tokens = [[w.lower() for w in re.findall(r"\b\w{2,}\b", d)] for d in documents]
        doc_lens = [len(tokens) for tokens in doc_tokens]
        avg_dl = sum(doc_lens) / max(1, len(doc_lens))
        num_docs = len(documents)

        # Document frequencies for query terms
        df: Dict[str, int] = {}
        for term in query_terms:
            df[term] = sum(1 for tokens in doc_tokens if term in tokens)

        # BM25 Parameters
        k1 = 1.5
        b = 0.75

        scores: List[float] = []
        for i, tokens in enumerate(doc_tokens):
            score = 0.0
            dl = doc_lens[i]
            term_counts: Dict[str, int] = {}
            for t in tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            for term in query_terms:
                if term not in term_counts:
                    continue
                tf = term_counts[term]
                n_docs_with_term = df.get(term, 0)
                # IDF with smoothing
                idf = math.log((num_docs - n_docs_with_term + 0.5) / (n_docs_with_term + 0.5) + 1.0)
                # Term score
                numerator = tf * (k1 + 1.0)
                denominator = tf + k1 * (1.0 - b + b * (dl / avg_dl))
                score += idf * (numerator / max(1e-9, denominator))

            scores.append(score)

        return scores

    @staticmethod
    def _min_max_scale(scores: List[float]) -> List[float]:
        if not scores:
            return []
        min_v = min(scores)
        max_v = max(scores)
        spread = max_v - min_v
        if spread < 1e-9:
            return [1.0 if max_v > 0 else 0.0 for _ in scores]
        return [(s - min_v) / spread for s in scores]
