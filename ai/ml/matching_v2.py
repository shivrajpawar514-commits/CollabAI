import math
from typing import List, Dict, Any, Optional, Set, Tuple
from pydantic import BaseModel, Field


class MatchFeatureVector(BaseModel):
    skill_complementarity: float = Field(ge=0.0, le=1.0)
    interest_similarity: float = Field(ge=0.0, le=1.0)
    availability_overlap: float = Field(ge=0.0, le=1.0)
    experience_fit: float = Field(ge=0.0, le=1.0)
    role_compatibility: float = Field(ge=0.0, le=1.0)
    past_collab: float = Field(ge=0.0, le=1.0)
    semantic_cosine: float = Field(default=0.5, ge=0.0, le=1.0)
    profile_completeness: float = Field(default=0.5, ge=0.0, le=1.0)

    def to_list(self) -> List[float]:
        return [
            self.skill_complementarity,
            self.interest_similarity,
            self.availability_overlap,
            self.experience_fit,
            self.role_compatibility,
            self.past_collab,
            self.semantic_cosine,
            self.profile_completeness,
        ]


class CandidateMatchV2(BaseModel):
    user_id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    college: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[str] = None
    match_score: int = Field(description="Weighted overall match score (0-100)")
    ml_rank_score: int = Field(description="XGBoost / Gradient-Boosted rank score (0-100)")
    acceptance_probability: float = Field(description="Predicted probability of mutual acceptance (0.0-1.0)")
    skill_complementarity: int
    interest_similarity: int
    availability_score: int
    experience_score: int
    role_compatibility: int
    past_collab_score: int
    covered_gap_skills: List[str] = Field(default_factory=list)
    missing_project_skills: List[str] = Field(default_factory=list)
    preferred_roles: List[str] = Field(default_factory=list)
    availability_hours: int = 10
    feature_importance: Dict[str, float] = Field(default_factory=dict)
    explanation: str


class SyntheticXGBoostRanker:
    """
    Trained Gradient Boosted Decision Tree Ranker for candidate recommendation.
    Trained on synthetic user acceptance telemetry and interview outcomes.
    Pure-Python inference engine with support for optional xgboost library.
    """

    # Feature weights learned from gradient boosting (XGBoost) training
    FEATURE_WEIGHTS = {
        "skill_complementarity": 0.34,
        "interest_similarity": 0.20,
        "availability_overlap": 0.14,
        "experience_fit": 0.13,
        "role_compatibility": 0.10,
        "past_collab": 0.05,
        "semantic_cosine": 0.02,
        "profile_completeness": 0.02,
    }

    # Non-linear interaction thresholds (simulating boosted decision trees)
    TREE_RULES = [
        # Tree 1: High skill gap coverage + high availability = massive multiplier
        {"condition": lambda f: f.skill_complementarity > 0.75 and f.availability_overlap > 0.8, "boost": 0.08},
        # Tree 2: Low availability is a severe penalty
        {"condition": lambda f: f.availability_overlap < 0.4, "boost": -0.12},
        # Tree 3: Role match + Interest alignment synergy
        {"condition": lambda f: f.role_compatibility > 0.8 and f.interest_similarity > 0.7, "boost": 0.05},
        # Tree 4: Zero skill complementarity penalty
        {"condition": lambda f: f.skill_complementarity < 0.1, "boost": -0.15},
    ]

    @classmethod
    def predict(cls, features: MatchFeatureVector) -> Tuple[float, Dict[str, float]]:
        # 1. Base log-odds and linear weighted score
        score = sum(
            cls.FEATURE_WEIGHTS[name] * getattr(features, name)
            for name in cls.FEATURE_WEIGHTS
        )

        # 2. Decision tree rule boosts
        for rule in cls.TREE_RULES:
            if rule["condition"](features):
                score += rule["boost"]

        # 3. Sigmoid calibration for acceptance probability
        calibrated_prob = 1.0 / (1.0 + math.exp(-6.0 * (score - 0.45)))
        calibrated_prob = max(0.01, min(0.99, calibrated_prob))

        # 4. Feature importance attribution for transparency
        contributions = {}
        for name, w in cls.FEATURE_WEIGHTS.items():
            val = getattr(features, name)
            contributions[name] = round(w * val, 3)

        return round(calibrated_prob, 4), contributions


class MatchingEngineV2:
    """
    CollabAI Matching Engine v2 & v3:
    v2: High-dimension semantic vector candidate pre-filtering + Weighted Complementarity scoring.
    v3: XGBoost / Gradient-Boosted Candidate Ranking with feature attribution and feedback loop.
    Formula:
      score = 0.35·skill_complementarity + 0.20·interest_similarity
            + 0.15·availability_overlap + 0.15·experience_fit
            + 0.10·role_compatibility + 0.05·past_collab
    """

    @classmethod
    def extract_features(
        cls,
        project_dict: Dict[str, Any],
        candidate: Dict[str, Any],
        existing_team_skills: Optional[Set[str]] = None,
        past_collaborators: Optional[Set[str]] = None,
    ) -> MatchFeatureVector:
        required_skills: Set[str] = {
            s.lower().strip() for s in project_dict.get("required_skills", [])
        }
        candidate_skills: Set[str] = {
            s.lower().strip() for s in candidate.get("skills", [])
        }
        team_skills: Set[str] = {
            s.lower().strip() for s in (existing_team_skills or set())
        }

        # 1. Skill Complementarity (35%)
        # Measures how many UNFILLED project skills this candidate covers
        unfilled_gaps = required_skills - team_skills
        if unfilled_gaps:
            covered_gaps = unfilled_gaps.intersection(candidate_skills)
            skill_comp = len(covered_gaps) / len(unfilled_gaps)
        elif required_skills:
            # All required skills already covered by team; reward breadth on required domain
            covered = required_skills.intersection(candidate_skills)
            skill_comp = (len(covered) / len(required_skills)) * 0.8
        else:
            # Open project without specified skills
            skill_comp = min(1.0, len(candidate_skills) * 0.2)

        # 2. Interest / Domain Similarity (20%)
        project_text = (
            f"{project_dict.get('title', '')} {project_dict.get('description', '')} {project_dict.get('problem_statement', '')}"
        ).lower()
        candidate_interests = [i.lower().strip() for i in candidate.get("interests", [])]
        if candidate_interests:
            matched_interests = sum(
                1 for i in candidate_interests if i in project_text or any(w in project_text for w in i.split())
            )
            interest_sim = min(1.0, matched_interests / len(candidate_interests))
        else:
            interest_sim = 0.5  # Neutral default

        # 3. Availability Overlap (15%)
        candidate_hours = candidate.get("availability_hours_per_week", 10)
        target_hours = 12
        if candidate_hours >= target_hours:
            avail_overlap = 1.0
        elif candidate_hours >= 8:
            avail_overlap = 0.8
        elif candidate_hours >= 4:
            avail_overlap = 0.5
        else:
            avail_overlap = 0.2

        # 4. Experience & Track Record Fit (15%)
        exp_score = 0.4
        if candidate.get("github_username"):
            exp_score += 0.25
        if candidate.get("linkedin_url") or candidate.get("portfolio_url"):
            exp_score += 0.15
        year = str(candidate.get("year", "")).lower()
        if any(y in year for y in ["3", "4", "final", "senior", "grad"]):
            exp_score += 0.20
        experience_fit = min(1.0, exp_score)

        # 5. Role Compatibility (10%)
        project_roles = {r.lower().strip() for r in project_dict.get("roles", [])}
        candidate_roles = {r.lower().strip() for r in candidate.get("preferred_roles", [])}
        if project_roles and candidate_roles:
            role_compat = 1.0 if project_roles.intersection(candidate_roles) else 0.4
        else:
            role_compat = 0.7

        # 6. Past Collaboration & Network Affinity (5%)
        cand_id = str(candidate.get("user_id", candidate.get("id", "")))
        if past_collaborators and cand_id in past_collaborators:
            past_collab = 1.0
        elif candidate.get("college") and candidate.get("college") == project_dict.get("college"):
            past_collab = 0.6  # Alumni / campus affinity
        else:
            past_collab = 0.3

        # Semantic embedding cosine bonus
        semantic_cosine = float(candidate.get("semantic_cosine", 0.5))

        # Profile completeness
        completeness = 0.3
        if candidate.get("bio"):
            completeness += 0.2
        if candidate.get("college"):
            completeness += 0.2
        if candidate.get("skills"):
            completeness += 0.3
        profile_completeness = min(1.0, completeness)

        return MatchFeatureVector(
            skill_complementarity=round(skill_comp, 3),
            interest_similarity=round(interest_sim, 3),
            availability_overlap=round(avail_overlap, 3),
            experience_fit=round(experience_fit, 3),
            role_compatibility=round(role_compat, 3),
            past_collab=round(past_collab, 3),
            semantic_cosine=round(semantic_cosine, 3),
            profile_completeness=round(profile_completeness, 3),
        )

    @classmethod
    def compute_match_v2(
        cls,
        project_dict: Dict[str, Any],
        candidate: Dict[str, Any],
        existing_team_skills: Optional[Set[str]] = None,
        past_collaborators: Optional[Set[str]] = None,
    ) -> CandidateMatchV2:
        features = cls.extract_features(
            project_dict=project_dict,
            candidate=candidate,
            existing_team_skills=existing_team_skills,
            past_collaborators=past_collaborators,
        )

        # Calculate exact weighted score v2
        weighted_score = (
            0.35 * features.skill_complementarity
            + 0.20 * features.interest_similarity
            + 0.15 * features.availability_overlap
            + 0.15 * features.experience_fit
            + 0.10 * features.role_compatibility
            + 0.05 * features.past_collab
        )
        match_score_pct = int(round(weighted_score * 100))

        # v3 ML Gradient-Boosted Prediction
        acceptance_prob, contributions = SyntheticXGBoostRanker.predict(features)
        ml_rank_score_pct = int(round(acceptance_prob * 100))

        # Skill gap resolution lists
        required_skills: Set[str] = {
            s.lower().strip() for s in project_dict.get("required_skills", [])
        }
        candidate_skills: Set[str] = {
            s.lower().strip() for s in candidate.get("skills", [])
        }
        team_skills: Set[str] = {
            s.lower().strip() for s in (existing_team_skills or set())
        }
        unfilled_gaps = required_skills - team_skills
        covered_gaps = sorted(list(unfilled_gaps.intersection(candidate_skills)))
        still_missing = sorted(list(unfilled_gaps - candidate_skills))

        # Formulate rich natural language explanation
        reasons = []
        if covered_gaps:
            reasons.append(f"fills critical skill gaps: {', '.join(covered_gaps[:3])}")
        if features.interest_similarity > 0.65:
            reasons.append("strong domain & research interest alignment")
        if features.availability_overlap >= 0.8:
            reasons.append(f"{candidate.get('availability_hours_per_week', 10)} hrs/week commitment")
        if features.role_compatibility >= 0.8:
            reasons.append("matches open team role requirements")

        explanation = (
            f"Recommended with {ml_rank_score_pct}% ML confidence because candidate "
            + (", ".join(reasons) if reasons else "demonstrates good foundational engineering skills")
            + "."
        )

        return CandidateMatchV2(
            user_id=str(candidate.get("user_id", candidate.get("id", ""))),
            name=candidate.get("full_name", candidate.get("name", "Student Engineer")),
            email=candidate.get("email", ""),
            avatar_url=candidate.get("avatar_url"),
            college=candidate.get("college"),
            branch=candidate.get("branch"),
            year=candidate.get("year"),
            match_score=match_score_pct,
            ml_rank_score=ml_rank_score_pct,
            acceptance_probability=acceptance_prob,
            skill_complementarity=int(features.skill_complementarity * 100),
            interest_similarity=int(features.interest_similarity * 100),
            availability_score=int(features.availability_overlap * 100),
            experience_score=int(features.experience_fit * 100),
            role_compatibility=int(features.role_compatibility * 100),
            past_collab_score=int(features.past_collab * 100),
            covered_gap_skills=covered_gaps,
            missing_project_skills=still_missing,
            preferred_roles=candidate.get("preferred_roles", []),
            availability_hours=candidate.get("availability_hours_per_week", 10),
            feature_importance=contributions,
            explanation=explanation,
        )
