import asyncio
import random
import uuid
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from faker import Faker
from sqlalchemy import select
from app.core.db import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models.user import User
from app.models.profile import Profile
from app.models.skill import Skill, UserSkill
from app.models.project import Project, ProjectSkill, ProjectRole

fake = Faker()

SKILLS_DATA = [
    # AI / ML
    ("PyTorch", "AI/ML"), ("TensorFlow", "AI/ML"), ("Scikit-Learn", "AI/ML"),
    ("Transformers (HuggingFace)", "AI/ML"), ("LangChain/LangGraph", "AI/ML"),
    ("OpenAI/Gemini APIs", "AI/ML"), ("Computer Vision (OpenCV)", "AI/ML"),
    # Backend
    ("Python", "Backend"), ("FastAPI", "Backend"), ("Node.js", "Backend"),
    ("Go (Golang)", "Backend"), ("PostgreSQL", "Backend"), ("Redis", "Backend"),
    ("GraphQL", "Backend"), ("Docker", "DevOps"),
    # Frontend
    ("TypeScript", "Frontend"), ("React", "Frontend"), ("Next.js", "Frontend"),
    ("Tailwind CSS", "Frontend"), ("Vue.js", "Frontend"),
    # Mobile & Cloud
    ("Flutter", "Mobile"), ("React Native", "Mobile"),
    ("Kubernetes", "DevOps"), ("AWS", "Cloud"), ("CI/CD (GitHub Actions)", "DevOps"),
    # Design & Security
    ("Figma / UI Design", "Design"), ("Cybersecurity & Pentesting", "Security")
]

COLLEGES = [
    "MIT", "Stanford University", "UC Berkeley", "Carnegie Mellon University",
    "IIT Bombay", "IIT Delhi", "Georgia Tech", "University of Waterloo",
    "ETH Zurich", "University of Toronto", "NUS Singapore"
]

BRANCHES = [
    "Computer Science", "Data Science & AI", "Electrical Engineering",
    "Software Engineering", "Mathematics & Computing", "Robotics"
]

YEARS = ["1st Year", "2nd Year", "3rd Year", "Final Year", "Master's"]

ROLE_CHOICES = [
    "Fullstack Engineer", "Frontend Developer", "Backend Developer",
    "ML/AI Researcher", "Data Engineer", "DevOps Specialist", "UI/UX Designer"
]

PROJECT_TEMPLATES = [
    {
        "title": "AgriVision: AI Crop Disease Detection & Advisory",
        "description": "Mobile and edge AI application allowing farmers in rural regions to photograph crop foliage, instantly detect pathogens using lightweight vision transformers, and receive localized treatment recommendations.",
        "problem_statement": "Crop diseases cause up to 40% annual yield loss globally. Early diagnosis by agricultural specialists is inaccessible or prohibitively slow for smallholder farmers.",
        "roles": [("ML Vision Specialist", 1), ("Mobile Flutter Developer", 1), ("Backend FastAPI Engineer", 1)],
        "skills": ["PyTorch", "Computer Vision (OpenCV)", "FastAPI", "Flutter"]
    },
    {
        "title": "CampusPulse: Student Skill-Barter & Project Matcher",
        "description": "Peer-to-peer web platform where university students exchange technical skills, collaborate on capstone projects, and build verifiable on-chain portfolios.",
        "problem_statement": "Students frequently get stuck on isolated coursework challenges and struggle to recruit interdisciplinary teammates for hackathons.",
        "roles": [("Frontend Next.js Developer", 1), ("Backend Engineer", 1), ("UI/UX Designer", 1)],
        "skills": ["Next.js", "TypeScript", "FastAPI", "PostgreSQL", "Figma / UI Design"]
    },
    {
        "title": "MedFlow: Privacy-Preserving Clinical Trial Matcher",
        "description": "Federated search and LLM retrieval engine that matches anonymized patient electronic health records to active ClinicalTrials.gov protocols without exposing PHI.",
        "problem_statement": "Less than 5% of eligible cancer patients enroll in clinical trials due to fragmented trial registries and complex medical jargon.",
        "roles": [("AI/RAG Engineer", 1), ("Fullstack Developer", 1), ("Security Engineer", 1)],
        "skills": ["LangChain/LangGraph", "OpenAI/Gemini APIs", "Python", "Cybersecurity & Pentesting"]
    },
    {
        "title": "EcoRoute: Multimodal Carbon-Optimized Transit Planner",
        "description": "An eco-friendly urban routing engine using real-time open transit data and elevation maps to compute the lowest carbon footprint commute.",
        "problem_statement": "Standard navigation algorithms optimize solely for speed, ignoring micro-mobility, bike lanes, and multi-modal transit carbon emissions.",
        "roles": [("Backend / Graph Algorithms", 1), ("Frontend Map Specialist", 1)],
        "skills": ["Go (Golang)", "React", "TypeScript", "Docker"]
    },
    {
        "title": "OpenDevs: Automated Pull Request Review Copilot",
        "description": "A GitHub App bot that automatically parses pull requests, detects architectural anti-patterns, evaluates test coverage, and suggests line-by-line diffs using local LLMs.",
        "problem_statement": "Maintainers of open-source student repositories face massive backlogs of PRs with insufficient or unhelpful automated guidance.",
        "roles": [("LLM Systems Engineer", 1), ("DevOps / CI/CD Engineer", 1)],
        "skills": ["Python", "OpenAI/Gemini APIs", "CI/CD (GitHub Actions)", "Docker"]
    },
    {
        "title": "SoundMind: Real-Time Acoustic Biofeedback for ADHD",
        "description": "A cross-platform audio app generating generative binaural beats and neuro-acoustic soundscapes adapted in real-time to heart-rate variability and focus states.",
        "problem_statement": "Over 360 million people live with ADHD, yet non-pharmacological focus interventions lack personalized real-time physiological feedback.",
        "roles": [("DSP / Audio Engineer", 1), ("React Native Developer", 1)],
        "skills": ["Python", "React Native", "TypeScript"]
    },
    {
        "title": "GovClear: Transparent Civic Budgeting & NLP Explorer",
        "description": "Interactive data visualization dashboard that ingests city municipal council PDF minutes and line-item financial disclosures into semantic search and interactive charts.",
        "problem_statement": "City budget documents are hundreds of pages of scanned non-searchable PDFs, preventing meaningful citizen oversight.",
        "roles": [("Data Engineer", 1), ("Frontend Data Viz Engineer", 1)],
        "skills": ["Python", "FastAPI", "Next.js", "PostgreSQL"]
    },
    {
        "title": "MeshNet: Disaster Emergency Ad-Hoc Communication",
        "description": "LoRa and Bluetooth mesh networking firmware and companion PWA for community communications when cellular towers and power grids fail during natural disasters.",
        "problem_statement": "Hurricanes and earthquakes routinely knock out cellular infrastructure, isolating vulnerable neighborhoods in the critical first 72 hours.",
        "roles": [("Embedded / Systems Engineer", 1), ("Frontend PWA Developer", 1)],
        "skills": ["Go (Golang)", "React", "TypeScript", "Docker"]
    }
]


async def seed():
    print("🌱 Initializing Database tables...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Seed Skills
        print("🌱 Seeding Skills taxonomy...")
        skill_models = {}
        for name, category in SKILLS_DATA:
            res = await session.execute(select(Skill).where(Skill.name == name))
            skill = res.scalar_one_or_none()
            if not skill:
                skill = Skill(name=name, category=category)
                session.add(skill)
                await session.flush()
            skill_models[name] = skill
        await session.commit()
        print(f"✅ Loaded {len(skill_models)} skills.")

        # 2. Seed Default Demo User
        demo_email = "student@collabai.dev"
        res = await session.execute(select(User).where(User.email == demo_email))
        demo_user = res.scalar_one_or_none()
        if not demo_user:
            demo_user = User(
                email=demo_email,
                hashed_password=hash_password("password123"),
                full_name="Alex Chen",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80"
            )
            session.add(demo_user)
            await session.flush()

            demo_profile = Profile(
                user_id=demo_user.id,
                college="Stanford University",
                branch="Computer Science",
                year="3rd Year",
                bio="Passionate about building AI-powered developer tools, fullstack web applications, and autonomous multi-agent systems.",
                location="San Francisco, CA",
                languages=["English", "Mandarin"],
                interests=["Generative AI", "Distributed Systems", "Hackathons"],
                preferred_roles=["Fullstack Engineer", "AI/ML Researcher"],
                availability_hours_per_week=18,
                github_username="alexchen-ai",
                linkedin_url="https://linkedin.com/in/alexchen"
            )
            session.add(demo_profile)

            # Assign skills to demo user
            for sname in ["Python", "FastAPI", "TypeScript", "Next.js", "OpenAI/Gemini APIs"]:
                if sname in skill_models:
                    session.add(UserSkill(user_id=demo_user.id, skill_id=skill_models[sname].id, proficiency_level=5))
            await session.commit()
            print(f"✅ Created Demo Student account: {demo_email} (password: password123)")

        # 3. Seed 50 Synthetic Students
        print("🌱 Seeding 50 synthetic students and profiles...")
        all_skills_list = list(skill_models.values())
        created_users = [demo_user]

        for i in range(50):
            email = f"student_{i+1}@collabai.edu"
            res = await session.execute(select(User).where(User.email == email))
            if res.scalar_one_or_none():
                continue

            full_name = fake.name()
            user = User(
                email=email,
                hashed_password=hash_password("password123"),
                full_name=full_name,
                avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={email}"
            )
            session.add(user)
            await session.flush()

            profile = Profile(
                user_id=user.id,
                college=random.choice(COLLEGES),
                branch=random.choice(BRANCHES),
                year=random.choice(YEARS),
                bio=fake.sentence(nb_words=14),
                location=f"{fake.city()}, {fake.country_code()}",
                languages=["English"] + ([random.choice(["Spanish", "Hindi", "French", "German", "Japanese"])] if random.random() > 0.4 else []),
                interests=random.sample(["Hackathons", "Open Source", "Robotics", "Web3", "Deep Learning", "Climate Tech", "FinTech"], k=random.randint(2, 4)),
                preferred_roles=random.sample(ROLE_CHOICES, k=random.randint(1, 3)),
                availability_hours_per_week=random.choice([10, 15, 20, 25]),
                github_username=f"{user.full_name.lower().replace(' ', '')}{random.randint(10, 99)}"
            )
            session.add(profile)

            # Assign 3-6 skills
            student_skills = random.sample(all_skills_list, k=random.randint(3, 6))
            for s in student_skills:
                session.add(UserSkill(
                    user_id=user.id,
                    skill_id=s.id,
                    proficiency_level=random.randint(2, 5)
                ))
            created_users.append(user)

        await session.commit()
        print(f"✅ 50 Student profiles successfully created.")

        # 4. Seed 20 Projects
        print("🌱 Seeding 20 collaboration projects...")
        existing_projects = await session.execute(select(Project))
        if len(existing_projects.scalars().all()) < 20:
            for idx in range(20):
                template = PROJECT_TEMPLATES[idx % len(PROJECT_TEMPLATES)]
                owner = random.choice(created_users)
                title = f"{template['title']} #{idx+1}" if idx >= len(PROJECT_TEMPLATES) else template['title']

                project = Project(
                    title=title,
                    description=template['description'],
                    problem_statement=template['problem_statement'],
                    owner_id=owner.id,
                    status="recruiting",
                    max_team_size=random.choice([3, 4, 5]),
                    repo_url=f"https://github.com/collabai-projects/{title.lower().replace(' ', '-').replace(':', '')[:30]}"
                )
                session.add(project)
                await session.flush()

                # Required skills
                for sk_name in template['skills']:
                    if sk_name in skill_models:
                        session.add(ProjectSkill(
                            project_id=project.id,
                            skill_id=skill_models[sk_name].id,
                            is_required=True
                        ))

                # Roles
                for role_name, capacity in template['roles']:
                    session.add(ProjectRole(
                        project_id=project.id,
                        role_name=role_name,
                        capacity=capacity,
                        filled_count=0
                    ))

            await session.commit()
            print("✅ 20 Collaborative projects seeded with skills and roles.")

    print("🎉 Database seeding complete! Ready for Phase 1 testing.")


if __name__ == "__main__":
    asyncio.run(seed())
