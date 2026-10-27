#!/usr/bin/env python3
"""
CollabAI Daily Commit Pusher
Automates releasing 3 commits per day to GitHub 'main' from the 'release/all-phases' branch.
"""

import argparse
import os
import subprocess
import sys

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

SCHEDULE = [
    {
        "day": 1,
        "date": "2026-10-19",
        "tip_sha": "e0233ee",
        "commits": [
            ("0c1a2f1", "10:15", "Initial commit"),
            ("0f50d7e", "14:30", "feat(backend): implement FastAPI core, async SQLAlchemy models, and pgvector infrastructure"),
            ("e0233ee", "18:45", "feat(ai): integrate swappable LLM client with Gemini, Groq, and Ollama adapters"),
        ],
    },
    {
        "day": 2,
        "date": "2026-10-20",
        "tip_sha": "0fa99bd",
        "commits": [
            ("537dc0f", "10:20", "feat(frontend): build Next.js 14 client, project discovery UI, and complete documentation"),
            ("f522ea4", "14:35", "feat(backend): add Phase 2 data models and Pydantic schemas for teams, kanban tasks, chat, and notifications"),
            ("0fa99bd", "18:50", "feat(backend): implement Phase 2 team management, task service, chat, notifications, and WebSocket room manager"),
        ],
    },
    {
        "day": 3,
        "date": "2026-10-21",
        "tip_sha": "afd521b",
        "commits": [
            ("941fa35", "10:10", "feat(frontend): add interactive project workspace, Kanban board, real-time chat, and notification center"),
            ("00aebd6", "14:25", "feat(ai): implement Phase 3 prompt schemas, streaming adapters, and AI matching engine"),
            ("afd521b", "18:40", "feat(backend): implement Phase 3 AI services and endpoints for project generation, milestone planning, task decomposition, and copilot streaming"),
        ],
    },
    {
        "day": 4,
        "date": "2026-10-22",
        "tip_sha": "07c131b",
        "commits": [
            ("029c420", "10:30", "feat(frontend): integrate AI project generator, workspace copilot, task decomposer, and teammate recommender"),
            ("de15b08", "14:45", "feat(ai): implement Phase 4 RAG document parser, chunker, hybrid retriever, and citation engine"),
            ("07c131b", "19:00", "feat(backend): implement Phase 4 RAG ingestion pipeline, background chunk indexing, and research Q&A endpoints"),
        ],
    },
    {
        "day": 5,
        "date": "2026-10-23",
        "tip_sha": "9bb5404",
        "commits": [
            ("017b4e0", "10:15", "feat(frontend): add AI Research Assistant, document knowledge vault, and interactive citation inspector"),
            ("314961d", "14:30", "feat(ml): implement Phase 5 ML intelligence core - Matching v2/v3 XGBoost ranker, Deadline Risk predictor, and NetworkX Skill Graph"),
            ("9bb5404", "18:45", "feat(backend): implement Phase 5 ML schemas, repositories, recommendation feedback logging, and intelligence API endpoints"),
        ],
    },
    {
        "day": 6,
        "date": "2026-10-24",
        "tip_sha": "61e497f",
        "commits": [
            ("2f4d80a", "10:20", "feat(frontend): add Project ML Intelligence dashboard, interactive Skill Graph, Deadline Risk radar, and feedback loop"),
            ("db4d52f", "14:35", "feat(ai): implement Phase 7 Advanced AI engines - Voice Meeting Assistant, Decision Memory Graph, and Multi-Agent Orchestrator"),
            ("61e497f", "18:50", "feat(backend): implement Phase 7 Advanced AI models, repositories, meeting action-item conversion, and orchestrator API endpoints"),
        ],
    },
    {
        "day": 7,
        "date": "2026-10-25",
        "tip_sha": "6e22e6b",
        "commits": [
            ("7070ba4", "10:15", "feat(frontend): add Autonomous AI Lab workspace tab, Voice Meeting to Tasks converter, Decision Memory Graph, and Multi-Agent console"),
            ("8d81bd3", "14:30", "refactor: apply strict anti-vibe-coding standards, custom domain metadata, favicon, privacy and terms pages"),
            ("6e22e6b", "18:45", "docs: add production deployment verification, release notes, and architecture specification"),
        ],
    },
    {
        "day": 8,
        "date": "2026-10-26",
        "tip_sha": "d421b30",
        "commits": [
            ("3d01a40", "10:15", "ci(infra): add GitHub Actions automated CI workflow, multi-stage frontend Dockerfile, and health verification suite"),
            ("da9c347", "14:30", "feat(backend): implement system observability router, Prometheus metrics export, and LLM provider latency monitor"),
            ("d421b30", "18:45", "feat(frontend): add System Diagnostics dashboard, real-time provider latency badges, and end-to-end operational test suite"),
        ],
    },
    {
        "day": 9,
        "date": "2026-10-27",
        "tip_sha": "757896b",
        "commits": [
            ("c825ba8", "10:15", "feat(ai): implement Hackathon Pitch Deck generator, 7-slide presentation engine, and portfolio exporter"),
            ("34f83da", "14:30", "feat(backend): add sprint velocity analytics, burndown metrics, and project health grading"),
            ("757896b", "18:45", "feat(frontend): add interactive Hackathon Pitch Deck modal, portfolio markdown exporter, and velocity telemetry card"),
        ],
    },
]

def run_git(cmd):
    return subprocess.check_output(["git"] + cmd, cwd=REPO_DIR, text=True).strip()

def get_current_day():
    main_rev = run_git(["rev-parse", "refs/heads/main"])
    for item in SCHEDULE:
        full_tip = run_git(["rev-parse", item["tip_sha"]])
        if main_rev == full_tip:
            return item["day"]
    return None

def print_status():
    current_day = get_current_day()
    print("=" * 70)
    print("CollabAI Daily Commit Schedule Status")
    print("=" * 70)
    print(f"Current branch 'main' is at: Day {current_day if current_day else 'Unknown'}")
    print("-" * 70)
    for item in SCHEDULE:
        marker = "▶ [LIVE ON MAIN]" if item["day"] == current_day else "  [QUEUED]" if (current_day and item["day"] > current_day) else "✓ [COMPLETED]"
        print(f"{marker} Day {item['day']} ({item['date']}):")
        for sha, time_slot, msg in item["commits"]:
            print(f"     • {sha} ({time_slot}) {msg[:55]}...")
    print("=" * 70)

def push_day(target_day):
    target = next((item for item in SCHEDULE if item["day"] == target_day), None)
    if not target:
        print(f"Error: Invalid day {target_day}. Must be between 1 and 9.")
        sys.exit(1)
    
    tip_sha = run_git(["rev-parse", target["tip_sha"]])
    print(f"Advancing branch 'main' to Day {target_day} ({target['date']}) -> {target['tip_sha']}...")
    run_git(["update-ref", "refs/heads/main", tip_sha])
    
    print(f"Pushing 'main' to GitHub origin...")
    output = run_git(["push", "--force", "origin", "main"])
    print("Push complete!")
    print(f"GitHub 'main' is now at Day {target_day} ({len(target['commits']) * target_day} total commits).")

def main():
    parser = argparse.ArgumentParser(description="CollabAI Daily Commit Pusher")
    parser.add_argument("--status", action="store_true", help="Display current release schedule status")
    parser.add_argument("--next", action="store_true", help="Push the next queued day's 3 commits to origin main")
    parser.add_argument("--day", type=int, help="Push a specific day (1-9) to origin main")
    
    args = parser.parse_args()
    
    if args.day:
        push_day(args.day)
    elif args.next:
        curr = get_current_day()
        if curr is None:
            print("Cannot determine current day. Use --day N instead.")
            sys.exit(1)
        if curr >= 9:
            print("All 9 days (27 commits) are already pushed to main!")
            sys.exit(0)
        push_day(curr + 1)

    else:
        print_status()

if __name__ == "__main__":
    main()
