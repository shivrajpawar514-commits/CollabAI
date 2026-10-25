from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ai.client import LLMClient


class ExtractedActionItem(BaseModel):
    title: str = Field(description="Actionable task title in imperative form (e.g., 'Implement JWT refresh token rotation')")
    description: str = Field(description="Detailed specifications and requirements discussed for this task")
    suggested_assignee: Optional[str] = Field(default=None, description="Name or role of person assigned in meeting")
    suggested_priority: str = Field(default="medium", description="Priority level: 'low', 'medium', 'high', or 'urgent'")
    estimated_hours: int = Field(default=4, description="Estimated engineering hours to complete this task (1-40)")
    suggested_milestone: Optional[str] = Field(default=None, description="Relevant milestone title or phase if mentioned")


class ExtractedDecision(BaseModel):
    what: str = Field(description="The architectural, technical, or product decision made")
    why: str = Field(description="The rationale, trade-offs, and justifications discussed")
    who: str = Field(default="Team Consensus", description="Who proposed or approved the decision")
    alternatives_considered: List[str] = Field(default_factory=list, description="Other options considered but rejected")
    tags: List[str] = Field(default_factory=list, description="Keywords and technology tags (e.g., ['postgres', 'auth'])")


class MeetingAnalysisResult(BaseModel):
    meeting_title: str
    executive_summary: str
    key_topics: List[str] = Field(default_factory=list)
    decisions: List[ExtractedDecision] = Field(default_factory=list)
    action_items: List[ExtractedActionItem] = Field(default_factory=list)
    overall_sentiment: str = Field(default="productive", description="Team mood: 'productive', 'collaborative', 'blocked', or 'urgent'")


SYSTEM_MEETING_ASSISTANT_PROMPT = """You are CollabAI's Senior Engineering Scrum Master and Technical Meeting Assistant.
Your task is to analyze meeting transcripts, standup notes, or audio transcripts and extract:
1. Executive Summary: Crisp, high-signal summary of what was discussed.
2. Key Topics: Main agenda items covered.
3. Decisions Made: Explicit architectural, design, or team agreements (what, why, who, and rejected alternatives).
4. Action Items: Concrete, well-scoped engineering tasks with suggested assignee, priority, hours estimate, and milestone.

Rules:
- Be specific and technical. Avoid vague bullet points like "work on backend". Instead write "Implement PostgreSQL pgvector cosine similarity search endpoint".
- Estimates should be realistic for student/hackathon teams (typically 2-8 hours per task).
- Extract ALL commitments made by team members as actionable items.
"""


class MeetingAssistant:
    def __init__(self):
        self.llm = LLMClient()

    async def analyze_transcript(
        self,
        transcript_text: str,
        project_title: str = "",
        meeting_title: Optional[str] = None,
    ) -> MeetingAnalysisResult:
        if not transcript_text.strip():
            return MeetingAnalysisResult(
                meeting_title=meeting_title or "Quick Standup",
                executive_summary="Empty transcript provided.",
                key_topics=[],
                decisions=[],
                action_items=[],
                overall_sentiment="neutral",
            )

        prompt = f"""Project: {project_title or 'Engineering Project'}
Meeting Title: {meeting_title or 'Team Sync & Standup'}

Transcript Content:
\"\"\"{transcript_text}\"\"\"

Analyze the transcript and produce the structured executive summary, architectural decisions, and concrete engineering action items."""

        try:
            return await self.llm.generate_structured(
                prompt=prompt,
                schema=MeetingAnalysisResult,
                system_instruction=SYSTEM_MEETING_ASSISTANT_PROMPT,
                temperature=0.2,
            )
        except Exception as e:
            # Fallback heuristic parser if LLM structured fails or no API key is provided
            lines = [l.strip() for l in transcript_text.splitlines() if l.strip()]
            summary = "\n".join(lines[:3]) if lines else "Team sync meeting completed."

            extracted_actions = []
            extracted_decisions = []

            for line in lines:
                lower = line.lower()
                speaker = line.split(":", 1)[0].strip() if ":" in line else "Team"
                content = line.split(":", 1)[1].strip() if ":" in line else line

                if any(k in lower for k in ["decision", "agreed", "commit", "choose", "approved"]):
                    extracted_decisions.append(
                        ExtractedDecision(
                            what=content[:120],
                            why="Team consensus discussed in meeting",
                            who=speaker,
                            alternatives_considered=[],
                            tags=["architecture", "meeting"],
                        )
                    )
                elif any(k in lower for k in ["action", "will", "implement", "finish", "complete", "wire up", "test", "estimate"]):
                    priority = "urgent" if "urgent" in lower else "high" if "high" in lower else "medium"
                    hours = 6 if "6" in lower else 4 if "4" in lower else 3
                    extracted_actions.append(
                        ExtractedActionItem(
                            title=content[:80],
                            description=f"Task discussed by {speaker}: {content}",
                            suggested_assignee=speaker if speaker != "Team" else None,
                            suggested_priority=priority,
                            estimated_hours=hours,
                        )
                    )

            if not extracted_actions:
                extracted_actions.append(
                    ExtractedActionItem(
                        title=f"Review meeting notes: {lines[0][:50] if lines else 'Sprint'}",
                        description="Follow up on discussed items from the team transcript.",
                        suggested_priority="medium",
                        estimated_hours=2,
                    )
                )

            if not extracted_decisions:
                extracted_decisions.append(
                    ExtractedDecision(
                        what="Proceed with sprint roadmap deliverables",
                        why="Maintain team sprint velocity",
                        who="Team Consensus",
                        alternatives_considered=["Postpone sprint tasks"],
                        tags=["sprint"],
                    )
                )

            return MeetingAnalysisResult(
                meeting_title=meeting_title or "Team Standup",
                executive_summary=summary,
                key_topics=["Sprint Planning", "Technical Architecture", "Delivery"],
                decisions=extracted_decisions,
                action_items=extracted_actions,
                overall_sentiment="productive",
            )
