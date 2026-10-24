import math
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ai.client import LLMClient
from ai.rag.embeddings import EmbeddingClient


class DecisionRecord(BaseModel):
    id: str
    project_id: str
    what: str
    why: str
    who: str
    when: str
    alternatives_considered: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    linked_task_id: Optional[str] = None
    linked_document_id: Optional[str] = None
    score: float = 0.0


class DecisionMemoryAnswer(BaseModel):
    query: str
    answer: str
    confidence_score: float
    matched_decisions: List[DecisionRecord]


SYSTEM_PROJECT_MEMORY_PROMPT = """You are CollabAI's Architectural History and Project Memory System.
Your job is to answer questions about past architectural and technical decisions made by the team (e.g., "Why did we choose PostgreSQL over MongoDB?", "Who decided to use pgvector?", "What was the rationale for Next.js?").

Rely EXCLUSIVELY on the provided historical decision records.
Always cite the decision date, the rationale (why), the decision maker (who), and any rejected alternatives mentioned in the records.
If no record addresses the question, state that no architectural decision record exists for that topic.
"""


class ProjectMemoryEngine:
    def __init__(self):
        self.llm = LLMClient()
        self.embedding_client = EmbeddingClient()

    async def query_memory(
        self,
        query: str,
        decisions: List[Dict[str, Any]],
        project_title: str = "",
    ) -> DecisionMemoryAnswer:
        if not decisions:
            return DecisionMemoryAnswer(
                query=query,
                answer="No architectural decision records have been saved in this project's memory yet.",
                confidence_score=0.0,
                matched_decisions=[],
            )

        # 1. Embed query
        query_vec = self.embedding_client.embed_query(query)

        # 2. Score decision records via text + tag overlap + semantic similarity
        scored_records: List[DecisionRecord] = []
        for d in decisions:
            record_text = f"{d.get('what', '')} {d.get('why', '')} {' '.join(d.get('tags', []))}"
            rec_vec = self.embedding_client.embed_query(record_text)

            # Cosine similarity
            dot = sum(a * b for a, b in zip(query_vec, rec_vec))
            norm_q = math.sqrt(sum(a * a for a in query_vec)) or 1.0
            norm_r = math.sqrt(sum(b * b for b in rec_vec)) or 1.0
            cos_sim = max(0.0, dot / (norm_q * norm_r))

            # Keyword boost if terms in query match 'what' or 'tags'
            q_lower = query.lower()
            tag_matches = sum(1 for t in d.get("tags", []) if t.lower() in q_lower)
            if tag_matches > 0:
                cos_sim = min(1.0, cos_sim + 0.15 * tag_matches)

            record = DecisionRecord(
                id=str(d.get("id", "")),
                project_id=str(d.get("project_id", "")),
                what=d.get("what", ""),
                why=d.get("why", ""),
                who=d.get("who", "Team"),
                when=str(d.get("created_at", d.get("when", ""))),
                alternatives_considered=d.get("alternatives_considered", []),
                tags=d.get("tags", []),
                linked_task_id=d.get("linked_task_id"),
                linked_document_id=d.get("linked_document_id"),
                score=round(cos_sim, 3),
            )
            scored_records.append(record)

        # Sort descending by relevance score
        scored_records.sort(key=lambda x: x.score, reverse=True)
        top_matches = scored_records[:4]

        # 3. Format context for synthesis
        context_parts = []
        for i, m in enumerate(top_matches, 1):
            alts = f" (Alternatives rejected: {', '.join(m.alternatives_considered)})" if m.alternatives_considered else ""
            context_parts.append(
                f"[Decision {i}] ({m.when} by {m.who}):\n"
                f"What: {m.what}\n"
                f"Why: {m.why}{alts}\n"
                f"Tags: {', '.join(m.tags)}"
            )
        context_str = "\n\n".join(context_parts)

        prompt = f"""Project: {project_title or 'Engineering Project'}
Query: "{query}"

Historical Architectural Decision Records:
{context_str}

Please provide a clear, authoritative explanation of why this decision was made, who was involved, and the key trade-offs considered:"""

        try:
            answer = await self.llm.generate(
                prompt=prompt,
                system_instruction=SYSTEM_PROJECT_MEMORY_PROMPT,
                temperature=0.2,
                max_tokens=600,
            )
        except Exception:
            # Fallback if LLM unavailable
            best = top_matches[0]
            answer = f"Decision regarding '{best.what}': {best.why} (Agreed by {best.who} on {best.when})."

        confidence = top_matches[0].score if top_matches else 0.0

        return DecisionMemoryAnswer(
            query=query,
            answer=answer,
            confidence_score=confidence,
            matched_decisions=top_matches,
        )
