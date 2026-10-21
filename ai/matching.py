from typing import List, Dict, Any, Optional, Set
from pydantic import BaseModel, Field


class CandidateMatch(BaseModel):
    user_id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    match_score: int = Field(description="Overall match score percentage from 0 to 100")
    skill_score: int = Field(description="Skill complementarity score percentage")
    interest_score: int = Field(description="Domain / interest alignment score")
    availability_score: int = Field(description="Time commitment match score")
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    preferred_roles: List[str] = Field(default_factory=list)
    availability_hours: int = 10
    explanation: str


class MatchingEngine:
    """
    AI Team Matching Engine.
    Formula:
    Match Score = (0.35 * Skill Complementarity) +
                  (0.20 * Interest & Domain Alignment) +
                  (0.15 * Availability Hours Match) +
                  (0.15 * Role Compatibility) +
                  (0.15 * Experience & Profile Completeness)
    """

    @classmethod
    def compute_match(
        cls,
        project_dict: Dict[str, Any],
        candidate: Dict[str, Any]
    ) -> CandidateMatch:
        required_skills: Set[str] = {
            s.lower().strip() for s in project_dict.get("required_skills", [])
        }
        candidate_skills: Set[str] = {
            s.lower().strip() for s in candidate.get("skills", [])
        }
        
        # 1. Skill Score (35%)
        if required_skills:
            common_skills = required_skills.intersection(candidate_skills)
            skill_coverage = len(common_skills) / len(required_skills)
            # Jaccard bonus if they have relevant complementary skills
            union_skills = required_skills.union(candidate_skills)
            jaccard = len(common_skills) / len(union_skills) if union_skills else 0
            skill_pct = int(min(100, (skill_coverage * 0.75 + jaccard * 0.25) * 100))
            matching_skill_list = sorted(list(common_skills))
            missing_skill_list = sorted(list(required_skills - candidate_skills))
        else:
            # If no explicit skills specified on project, score based on general technical breadth
            skill_pct = min(90, len(candidate_skills) * 15)
            matching_skill_list = sorted(list(candidate_skills))[:5]
            missing_skill_list = []

        # 2. Interest / Domain Alignment (20%)
        project_title_desc = (project_dict.get("title", "") + " " + project_dict.get("description", "")).lower()
        candidate_interests = [i.lower() for i in candidate.get("interests", [])]
        matched_interests = 0
        for interest in candidate_interests:
            if interest in project_title_desc or any(token in project_title_desc for token in interest.split()):
                matched_interests += 1
        interest_pct = int(min(100, (matched_interests / max(1, len(candidate_interests))) * 100) if candidate_interests else 60)

        # 3. Availability Hours Match (15%)
        candidate_hours = candidate.get("availability_hours_per_week", 10)
        target_hours = 10  # Standard student project expected weekly hours
        if candidate_hours >= target_hours:
            availability_pct = 100
        elif candidate_hours >= 6:
            availability_pct = 75
        else:
            availability_pct = 40

        # 4. Role Compatibility (15%)
        project_roles = {r.lower().strip() for r in project_dict.get("roles", [])}
        candidate_roles = {r.lower().strip() for r in candidate.get("preferred_roles", [])}
        if project_roles and candidate_roles:
            role_overlap = project_roles.intersection(candidate_roles)
            role_pct = 100 if role_overlap else 50
        else:
            role_pct = 70

        # 5. Experience & Completeness (15%)
        completeness_points = 50
        if candidate.get("github_username"):
            completeness_points += 20
        if candidate.get("bio") and len(candidate.get("bio", "")) > 20:
            completeness_points += 15
        if candidate.get("college"):
            completeness_points += 15
        exp_pct = min(100, completeness_points)

        # Overall Weighted Score
        weighted_score = (
            (skill_pct * 0.35) +
            (interest_pct * 0.20) +
            (availability_pct * 0.15) +
            (role_pct * 0.15) +
            (exp_pct * 0.15)
        )
        final_score = int(max(20, min(99, round(weighted_score))))

        # Generate explanatory recommendation rationale
        explanation_parts = []
        if matching_skill_list:
            top_skills = ", ".join([s.title() for s in matching_skill_list[:3]])
            explanation_parts.append(f"Brings key skills ({top_skills})")
        if candidate.get("preferred_roles"):
            top_roles = ", ".join(candidate["preferred_roles"][:2])
            explanation_parts.append(f"interested in {top_roles}")
        explanation_parts.append(f"offers {candidate_hours}h/wk commitment")
        explanation = "; ".join(explanation_parts) + "."

        return CandidateMatch(
            user_id=candidate.get("id", ""),
            name=candidate.get("name", "Student"),
            email=candidate.get("email", ""),
            avatar_url=candidate.get("avatar_url"),
            college=candidate.get("college"),
            branch=candidate.get("branch"),
            year=candidate.get("year"),
            match_score=final_score,
            skill_score=skill_pct,
            interest_score=interest_pct,
            availability_score=availability_pct,
            matching_skills=[s.title() for s in matching_skill_list],
            missing_skills=[s.title() for s in missing_skill_list],
            preferred_roles=candidate.get("preferred_roles", []),
            availability_hours=candidate_hours,
            explanation=explanation
        )

    @classmethod
    def rank_candidates(
        cls,
        project_dict: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[CandidateMatch]:
        scored: List[CandidateMatch] = []
        for cand in candidates:
            scored.append(cls.compute_match(project_dict, cand))
        
        # Sort descending by match_score
        scored.sort(key=lambda x: x.match_score, reverse=True)
        return scored[:top_k]
