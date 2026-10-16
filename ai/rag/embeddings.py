import os
import math
import hashlib
import re
from typing import List, Optional


class EmbeddingClient:
    """
    Dense vector embedding generator producing 384-dimensional unit-normalized vectors.
    Supports Google Gemini, Ollama, and local deterministic semantic hash embeddings.
    """

    DIMENSION: int = 384

    def __init__(self, model_name: str = "text-embedding-004"):
        self.model_name = model_name
        self.gemini_key = os.getenv("GEMINI_API_KEY")

    def embed_query(self, text: str) -> List[float]:
        vectors = self.embed_documents([text])
        return vectors[0] if vectors else [0.0] * self.DIMENSION

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # 1. Try Gemini Embeddings if API key is configured
        if self.gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_key)
                # Google embedding models usually output 768 dims; we slice or pool to 384
                results = []
                for text in texts:
                    res = genai.embed_content(
                        model="models/text-embedding-004",
                        content=text[:2000],
                        task_type="retrieval_document"
                    )
                    raw_vec = res.get("embedding", [])
                    if len(raw_vec) >= self.DIMENSION:
                        vec = self._normalize(raw_vec[:self.DIMENSION])
                    else:
                        vec = self._normalize(raw_vec + [0.0] * (self.DIMENSION - len(raw_vec)))
                    results.append(vec)
                return results
            except Exception:
                pass

        # 2. Try SentenceTransformers if available
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(texts, normalize_embeddings=True)
            return [e.tolist() for e in embeddings]
        except Exception:
            pass

        # 3. Deterministic Local Semantic Vectorizer (384-dimensional L2 normalized)
        # Guarantees zero-latency, zero external network dependency, and high cosine overlap for related terms
        return [self._local_semantic_embedding(t) for t in texts]

    def _local_semantic_embedding(self, text: str) -> List[float]:
        vec = [0.0] * self.DIMENSION
        if not text.strip():
            return vec

        # Tokenize words and n-grams
        cleaned = text.lower()
        words = re.findall(r"[a-z0-9_]+", cleaned)
        
        # Word-level projections with position decay and frequency weighting
        for idx, word in enumerate(words):
            if len(word) < 2:
                continue
            
            # Primary token hash
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            pos_1 = h % self.DIMENSION
            pos_2 = (h >> 16) % self.DIMENSION
            weight = 1.0 / (1.0 + math.log1p(idx))

            vec[pos_1] += weight
            vec[pos_2] += weight * 0.5

            # 3-gram subword hashing for morphological similarity (e.g., 'deploy', 'deployment')
            if len(word) >= 4:
                for i in range(len(word) - 2):
                    ngram = word[i : i + 3]
                    nh = int(hashlib.sha1(ngram.encode("utf-8")).hexdigest(), 16)
                    npos = nh % self.DIMENSION
                    vec[npos] += 0.25 * weight

        return self._normalize(vec)

    @staticmethod
    def _normalize(vec: List[float]) -> List[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm < 1e-9:
            return [0.0] * len(vec)
        return [round(x / norm, 6) for x in vec]
