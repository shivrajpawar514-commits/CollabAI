from typing import List, Dict, Any, Optional, Set, Tuple
from collections import deque
from pydantic import BaseModel, Field

# Try importing networkx, fallback gracefully to native DAG
try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False


class FreeResource(BaseModel):
    title: str
    url: str
    provider: str
    type: str = "tutorial"  # "docs", "video", "course", "interactive"


class SkillNode(BaseModel):
    name: str
    category: str
    difficulty: str  # "Beginner", "Intermediate", "Advanced"
    estimated_hours: int
    resources: List[FreeResource] = Field(default_factory=list)


class LearningStep(BaseModel):
    step_number: int
    skill_name: str
    category: str
    difficulty: str
    estimated_hours: int
    is_direct_requirement: bool
    prerequisites: List[str] = Field(default_factory=list)
    free_resources: List[FreeResource] = Field(default_factory=list)


class SkillGapAnalysis(BaseModel):
    project_id: str
    required_skills: List[str]
    team_owned_skills: List[str]
    missing_skills: List[str]
    coverage_percentage: float
    total_learning_hours: int
    recommended_learning_path: List[LearningStep]


# Curated Taxonomy of Skill Nodes and Free Resources (Official Docs, freeCodeCamp, MIT OCW, MDN)
CURATED_SKILL_NODES: Dict[str, Dict[str, Any]] = {
    "python": {
        "category": "Backend",
        "difficulty": "Beginner",
        "estimated_hours": 15,
        "resources": [
            {"title": "Official Python Tutorial", "url": "https://docs.python.org/3/tutorial/", "provider": "Python.org", "type": "docs"},
            {"title": "Scientific Computing with Python", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "provider": "freeCodeCamp", "type": "course"},
            {"title": "MIT 6.0001: Intro to CS and Python", "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/", "provider": "MIT OpenCourseWare", "type": "course"},
        ],
    },
    "fastapi": {
        "category": "Backend",
        "difficulty": "Intermediate",
        "estimated_hours": 12,
        "resources": [
            {"title": "FastAPI Official Interactive Tutorial", "url": "https://fastapi.tiangolo.com/tutorial/", "provider": "FastAPI", "type": "docs"},
            {"title": "Python API Development Course", "url": "https://www.freecodecamp.org/news/fastapi-course-for-beginners/", "provider": "freeCodeCamp", "type": "video"},
        ],
    },
    "sql": {
        "category": "Database",
        "difficulty": "Beginner",
        "estimated_hours": 10,
        "resources": [
            {"title": "SQL Tutorial for Beginners", "url": "https://www.sqltutorial.org/", "provider": "SQL Tutorial", "type": "tutorial"},
            {"title": "Relational Databases and SQL", "url": "https://www.freecodecamp.org/news/sql-and-databases-full-course/", "provider": "freeCodeCamp", "type": "video"},
        ],
    },
    "postgresql": {
        "category": "Database",
        "difficulty": "Intermediate",
        "estimated_hours": 12,
        "resources": [
            {"title": "PostgreSQL Official Documentation", "url": "https://www.postgresql.org/docs/", "provider": "PostgreSQL", "type": "docs"},
            {"title": "PostgreSQL for Everybody", "url": "https://www.py4e.com/", "provider": "Dr. Chuck / Free", "type": "course"},
        ],
    },
    "pgvector": {
        "category": "AI/ML",
        "difficulty": "Intermediate",
        "estimated_hours": 8,
        "resources": [
            {"title": "pgvector Official Guide & GitHub", "url": "https://github.com/pgvector/pgvector", "provider": "pgvector", "type": "docs"},
            {"title": "Vector Databases in PostgreSQL", "url": "https://supabase.com/docs/guides/ai/vector-columns", "provider": "Supabase Docs", "type": "docs"},
        ],
    },
    "javascript": {
        "category": "Frontend",
        "difficulty": "Beginner",
        "estimated_hours": 20,
        "resources": [
            {"title": "MDN JavaScript Guide", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "provider": "MDN Web Docs", "type": "docs"},
            {"title": "JavaScript Algorithms & Data Structures", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "provider": "freeCodeCamp", "type": "course"},
        ],
    },
    "typescript": {
        "category": "Frontend",
        "difficulty": "Intermediate",
        "estimated_hours": 14,
        "resources": [
            {"title": "TypeScript Handbook", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "provider": "TypeScript Official", "type": "docs"},
            {"title": "TypeScript for Beginners", "url": "https://www.freecodecamp.org/news/learn-typescript-beginners-guide/", "provider": "freeCodeCamp", "type": "tutorial"},
        ],
    },
    "react": {
        "category": "Frontend",
        "difficulty": "Intermediate",
        "estimated_hours": 18,
        "resources": [
            {"title": "React Official Interactive Docs", "url": "https://react.dev/learn", "provider": "React.dev", "type": "docs"},
            {"title": "Front End Development Libraries", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "provider": "freeCodeCamp", "type": "course"},
        ],
    },
    "next.js": {
        "category": "Frontend",
        "difficulty": "Intermediate",
        "estimated_hours": 14,
        "resources": [
            {"title": "Next.js Official Interactive Learning App", "url": "https://nextjs.org/learn", "provider": "Vercel", "type": "interactive"},
            {"title": "Next.js 14 Full Stack Tutorial", "url": "https://www.freecodecamp.org/news/nextjs-tutorial/", "provider": "freeCodeCamp", "type": "video"},
        ],
    },
    "tailwindcss": {
        "category": "Frontend",
        "difficulty": "Beginner",
        "estimated_hours": 6,
        "resources": [
            {"title": "TailwindCSS Documentation", "url": "https://tailwindcss.com/docs", "provider": "Tailwind Labs", "type": "docs"},
        ],
    },
    "machine learning": {
        "category": "AI/ML",
        "difficulty": "Intermediate",
        "estimated_hours": 25,
        "resources": [
            {"title": "Machine Learning with Python", "url": "https://www.freecodecamp.org/learn/machine-learning-with-python/", "provider": "freeCodeCamp", "type": "course"},
            {"title": "MIT 6.036: Intro to Machine Learning", "url": "https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning-fall-2020/", "provider": "MIT OpenCourseWare", "type": "course"},
        ],
    },
    "xgboost": {
        "category": "AI/ML",
        "difficulty": "Advanced",
        "estimated_hours": 10,
        "resources": [
            {"title": "XGBoost Official Tutorials", "url": "https://xgboost.readthedocs.io/en/stable/tutorials/index.html", "provider": "DMLC XGBoost", "type": "docs"},
            {"title": "Gradient Boosting Explained Visually", "url": "https://explained.ai/gradient-boosting/", "provider": "explained.ai", "type": "tutorial"},
        ],
    },
    "rag": {
        "category": "AI/ML",
        "difficulty": "Advanced",
        "estimated_hours": 12,
        "resources": [
            {"title": "Retrieval Augmented Generation with LangChain", "url": "https://python.langchain.com/docs/use_cases/question_answering/", "provider": "LangChain Docs", "type": "docs"},
            {"title": "Building Production RAG Systems", "url": "https://www.freecodecamp.org/news/rag-from-scratch/", "provider": "freeCodeCamp", "type": "tutorial"},
        ],
    },
    "docker": {
        "category": "DevOps",
        "difficulty": "Beginner",
        "estimated_hours": 10,
        "resources": [
            {"title": "Docker Getting Started Guide", "url": "https://docs.docker.com/get-started/", "provider": "Docker Official", "type": "docs"},
            {"title": "Docker Containerization for Beginners", "url": "https://www.freecodecamp.org/news/docker-simplified-a-hands-on-guide-for-beginners/", "provider": "freeCodeCamp", "type": "tutorial"},
        ],
    },
    "redis": {
        "category": "Database",
        "difficulty": "Intermediate",
        "estimated_hours": 8,
        "resources": [
            {"title": "Redis University Free Courses", "url": "https://university.redis.com/", "provider": "Redis Labs", "type": "course"},
            {"title": "Redis Crash Course", "url": "https://www.freecodecamp.org/news/learn-redis-complete-course/", "provider": "freeCodeCamp", "type": "video"},
        ],
    },
}

# Directed Graph Edges: (prerequisite -> target_skill)
SKILL_PREREQUISITES: List[Tuple[str, str]] = [
    ("python", "fastapi"),
    ("python", "machine learning"),
    ("sql", "postgresql"),
    ("postgresql", "pgvector"),
    ("machine learning", "xgboost"),
    ("machine learning", "rag"),
    ("pgvector", "rag"),
    ("javascript", "typescript"),
    ("javascript", "react"),
    ("typescript", "next.js"),
    ("react", "next.js"),
    ("css", "tailwindcss"),
    ("docker", "redis"),
    ("fastapi", "rag"),
]


class SkillGraphEngine:
    """
    Skill Graph Engine constructed with NetworkX DAG traversal.
    Computes skill gaps, topological learning paths, and attaches free open-access curriculum resources.
    """

    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}  # u -> {v} where u is prereq of v
        self.rev_adj: Dict[str, Set[str]] = {}  # v -> {u} where u is prereq of v
        self.all_nodes: Set[str] = set()

        # Build NetworkX DiGraph if library available
        if HAS_NETWORKX:
            self.nx_graph = nx.DiGraph()
        else:
            self.nx_graph = None

        self._build_graph()

    def _build_graph(self):
        for node in CURATED_SKILL_NODES:
            self.all_nodes.add(node.lower())
            self.adj[node.lower()] = set()
            self.rev_adj[node.lower()] = set()
            if self.nx_graph is not None:
                self.nx_graph.add_node(node.lower())

        for prereq, target in SKILL_PREREQUISITES:
            p = prereq.lower()
            t = target.lower()
            self.all_nodes.add(p)
            self.all_nodes.add(t)
            self.adj.setdefault(p, set()).add(t)
            self.rev_adj.setdefault(t, set()).add(p)
            if self.nx_graph is not None:
                self.nx_graph.add_edge(p, t)

    def analyze_skill_gap(
        self,
        project_id: str,
        required_skills: List[str],
        team_owned_skills: List[str],
    ) -> SkillGapAnalysis:
        req_set = {s.lower().strip() for s in required_skills if s.strip()}
        owned_set = {s.lower().strip() for s in team_owned_skills if s.strip()}

        missing_skills = sorted(list(req_set - owned_set))
        coverage_pct = (
            round((len(req_set - set(missing_skills)) / max(1, len(req_set))) * 100, 1)
            if req_set
            else 100.0
        )

        # Build personalized learning path
        recommended_steps = self._construct_learning_path(missing_skills, owned_set)
        total_hours = sum(s.estimated_hours for s in recommended_steps)

        return SkillGapAnalysis(
            project_id=project_id,
            required_skills=sorted(list(req_set)),
            team_owned_skills=sorted(list(owned_set)),
            missing_skills=missing_skills,
            coverage_percentage=coverage_pct,
            total_learning_hours=total_hours,
            recommended_learning_path=recommended_steps,
        )

    def _construct_learning_path(
        self,
        missing_skills: List[str],
        owned_skills: Set[str],
    ) -> List[LearningStep]:
        # Collect all prerequisite ancestral nodes needed for the missing target skills
        needed_skills: Set[str] = set()
        queue = deque(missing_skills)
        visited = set(missing_skills)

        while queue:
            curr = queue.popleft()
            needed_skills.add(curr)
            for prereq in self.rev_adj.get(curr, set()):
                if prereq not in owned_skills and prereq not in visited:
                    visited.add(prereq)
                    queue.append(prereq)

        # Topological Sort on needed_skills subgraph
        ordered_skills = self._topological_sort(needed_skills)

        # Build LearningStep objects
        steps: List[LearningStep] = []
        for i, skill in enumerate(ordered_skills, 1):
            node_data = CURATED_SKILL_NODES.get(
                skill,
                {
                    "category": "Engineering",
                    "difficulty": "Intermediate",
                    "estimated_hours": 10,
                    "resources": [
                        {
                            "title": f"{skill.capitalize()} Official Docs & Tutorial",
                            "url": f"https://www.google.com/search?q={skill}+tutorial+free",
                            "provider": "Community Docs",
                            "type": "docs",
                        }
                    ],
                },
            )

            prereqs_for_skill = sorted(list(self.rev_adj.get(skill, set())))
            free_res = [FreeResource(**r) for r in node_data.get("resources", [])]

            steps.append(
                LearningStep(
                    step_number=i,
                    skill_name=skill.capitalize(),
                    category=node_data.get("category", "General"),
                    difficulty=node_data.get("difficulty", "Intermediate"),
                    estimated_hours=node_data.get("estimated_hours", 10),
                    is_direct_requirement=(skill in missing_skills),
                    prerequisites=[p.capitalize() for p in prereqs_for_skill],
                    free_resources=free_res,
                )
            )

        return steps

    def _topological_sort(self, subset_nodes: Set[str]) -> List[str]:
        if HAS_NETWORKX and self.nx_graph is not None:
            subgraph = self.nx_graph.subgraph(subset_nodes)
            try:
                return list(nx.topological_sort(subgraph))
            except Exception:
                pass  # Fall back to Kahn's algorithm if cycle or error

        # Kahn's Algorithm for Topological Sort
        in_degree = {n: 0 for n in subset_nodes}
        for u in subset_nodes:
            for v in self.adj.get(u, set()):
                if v in subset_nodes:
                    in_degree[v] += 1

        queue = deque([n for n, d in in_degree.items() if d == 0])
        result = []

        while queue:
            u = queue.popleft()
            result.append(u)
            for v in self.adj.get(u, set()):
                if v in subset_nodes:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        queue.append(v)

        # If any node remains with in_degree > 0 (cycle), append remaining
        for n in subset_nodes:
            if n not in result:
                result.append(n)

        return result
