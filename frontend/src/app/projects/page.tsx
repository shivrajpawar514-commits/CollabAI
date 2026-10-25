"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Search,
  Filter,
  Users,
  Sparkles,
  ArrowRight,
  PlusCircle,
  Tag,
  CheckCircle,
  ExternalLink,
} from "lucide-react";
import { api, Project } from "@/lib/api";

const SAMPLE_PROJECTS: Project[] = [
  {
    id: "sample-1",
    title: "AgriVision: AI Crop Disease Detection & Advisory",
    description: "Mobile and edge AI application allowing farmers in rural regions to photograph crop foliage, instantly detect pathogens using lightweight vision transformers, and receive localized treatment recommendations.",
    problem_statement: "Crop diseases cause up to 40% annual yield loss globally. Early diagnosis by agricultural specialists is inaccessible or prohibitively slow for smallholder farmers.",
    owner_id: "user-1",
    owner: { id: "user-1", email: "alex@stanford.edu", full_name: "Alex Chen", is_active: true, created_at: "" },
    status: "recruiting",
    max_team_size: 4,
    created_at: "2026-10-10T00:00:00Z",
    updated_at: "2026-10-10T00:00:00Z",
    required_skills: [
      { id: "1", skill_id: "s1", is_required: true, skill: { id: "s1", name: "PyTorch", category: "AI/ML" } },
      { id: "2", skill_id: "s2", is_required: true, skill: { id: "s2", name: "FastAPI", category: "Backend" } },
      { id: "3", skill_id: "s3", is_required: true, skill: { id: "s3", name: "Flutter", category: "Mobile" } },
    ],
    roles: [
      { id: "r1", project_id: "sample-1", role_name: "ML Vision Specialist", capacity: 1, filled_count: 0 },
      { id: "r2", project_id: "sample-1", role_name: "Mobile Flutter Dev", capacity: 1, filled_count: 0 },
      { id: "r3", project_id: "sample-1", role_name: "Backend Engineer", capacity: 1, filled_count: 1 },
    ],
  },
  {
    id: "sample-2",
    title: "MedFlow: Privacy-Preserving Clinical Trial Matcher",
    description: "Federated search and LLM retrieval engine that matches anonymized patient electronic health records to active ClinicalTrials.gov protocols without exposing PHI.",
    problem_statement: "Less than 5% of eligible cancer patients enroll in clinical trials due to fragmented trial registries and complex medical jargon.",
    owner_id: "user-2",
    owner: { id: "user-2", email: "priya@iitb.ac.in", full_name: "Priya Sharma", is_active: true, created_at: "" },
    status: "recruiting",
    max_team_size: 3,
    created_at: "2026-10-09T00:00:00Z",
    updated_at: "2026-10-09T00:00:00Z",
    required_skills: [
      { id: "4", skill_id: "s4", is_required: true, skill: { id: "s4", name: "LangChain/LangGraph", category: "AI/ML" } },
      { id: "5", skill_id: "s5", is_required: true, skill: { id: "s5", name: "Next.js", category: "Frontend" } },
      { id: "6", skill_id: "s6", is_required: true, skill: { id: "s6", name: "PostgreSQL", category: "Backend" } },
    ],
    roles: [
      { id: "r4", project_id: "sample-2", role_name: "RAG / Agent Architect", capacity: 1, filled_count: 0 },
      { id: "r5", project_id: "sample-2", role_name: "Frontend Next.js Dev", capacity: 1, filled_count: 0 },
    ],
  },
  {
    id: "sample-3",
    title: "OpenDevs: Automated Pull Request Review Copilot",
    description: "A GitHub App bot that automatically parses pull requests, detects architectural anti-patterns, evaluates test coverage, and suggests line-by-line diffs using local LLMs.",
    problem_statement: "Maintainers of open-source student repositories face massive backlogs of PRs with insufficient or unhelpful automated guidance.",
    owner_id: "user-3",
    owner: { id: "user-3", email: "marcus@mit.edu", full_name: "Marcus Vance", is_active: true, created_at: "" },
    status: "recruiting",
    max_team_size: 4,
    created_at: "2026-10-08T00:00:00Z",
    updated_at: "2026-10-08T00:00:00Z",
    required_skills: [
      { id: "7", skill_id: "s7", is_required: true, skill: { id: "s7", name: "Python", category: "Backend" } },
      { id: "8", skill_id: "s8", is_required: true, skill: { id: "s8", name: "Docker", category: "DevOps" } },
      { id: "9", skill_id: "s9", is_required: true, skill: { id: "s9", name: "OpenAI/Gemini APIs", category: "AI/ML" } },
    ],
    roles: [
      { id: "r6", project_id: "sample-3", role_name: "DevOps / CI/CD Lead", capacity: 1, filled_count: 0 },
      { id: "r7", project_id: "sample-3", role_name: "LLM Pipeline Eng", capacity: 1, filled_count: 0 },
    ],
  },
];

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>(SAMPLE_PROJECTS);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTag, setSelectedTag] = useState("All");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Attempt fetching live data from backend
    setLoading(true);
    api.listProjects({ q: searchTerm || undefined })
      .then((res) => {
        if (res.items && res.items.length > 0) {
          setProjects(res.items);
        }
      })
      .catch(() => {
        // Fall back to sample projects if backend is still initializing
      })
      .finally(() => setLoading(false));
  }, [searchTerm]);

  const categories = ["All", "AI/ML", "Backend", "Frontend", "Mobile", "DevOps"];

  const filteredProjects = projects.filter((project) => {
    const matchesSearch =
      project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase());

    if (selectedTag === "All") return matchesSearch;

    const hasTag = project.required_skills.some(
      (s) => s.skill.category.toLowerCase() === selectedTag.toLowerCase()
    );
    return matchesSearch && hasTag;
  });

  return (
    <div className="space-y-8 pb-16">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
            Discover Projects & Teams
            <span className="text-xs px-2.5 py-1 rounded-md bg-blue-500/15 border border-blue-500/30 text-blue-300 font-semibold">
              {filteredProjects.length} Active
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Browse student capstones, hackathon teams, and open source projects looking for teammates.
          </p>
        </div>

        <Link
          href="/projects/create"
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm shadow-md shadow-blue-900/30 transition-all self-start md:self-auto"
        >
          <PlusCircle className="w-4 h-4" />
          Create Project
        </Link>
      </div>

      {/* Search and Category Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="relative w-full sm:w-96">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search projects, skills, topics..."
            className="w-full bg-[#0e111d] border border-white/10 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedTag(cat)}
              className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                selectedTag === cat
                  ? "bg-indigo-500/30 text-indigo-200 border border-indigo-500/50"
                  : "bg-white/[0.03] text-slate-400 hover:text-white border border-white/[0.06]"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Project Cards Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredProjects.map((project) => {
          const openRoles = project.roles.filter((r) => r.filled_count < r.capacity);
          return (
            <div
              key={project.id}
              className="glass-panel glass-panel-hover p-6 rounded-2xl border border-white/10 flex flex-col justify-between space-y-5"
            >
              <div className="space-y-3">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {project.status}
                    </span>
                    <h2 className="text-xl font-bold text-white mt-1.5 hover:text-indigo-300 transition-colors">
                      <Link href={`/projects/${project.id}`}>{project.title}</Link>
                    </h2>
                  </div>

                  <div className="flex items-center gap-1.5 text-xs text-slate-400 shrink-0 bg-white/[0.04] px-2.5 py-1 rounded-md border border-white/[0.06]">
                    <Users className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Max {project.max_team_size}</span>
                  </div>
                </div>

                <p className="text-sm text-slate-300 line-clamp-3 leading-relaxed">
                  {project.description}
                </p>

                {/* Open Roles Pill Badges */}
                {openRoles.length > 0 && (
                  <div className="pt-2">
                    <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                      Open Roles Needed:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {openRoles.map((role) => (
                        <span
                          key={role.id}
                          className="text-xs px-2.5 py-1 rounded-md bg-cyan-500/15 text-cyan-200 border border-cyan-500/30 font-medium"
                        >
                          {role.role_name}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Required Skills Badges */}
                <div className="pt-2">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1.5">
                    Tech Stack:
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {project.required_skills.map((ps) => (
                      <span
                        key={ps.id}
                        className="text-xs px-2.5 py-1 rounded-md bg-white/[0.05] text-slate-300 border border-white/[0.08]"
                      >
                        {ps.skill.name}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Card Footer */}
              <div className="pt-4 border-t border-white/[0.08] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-7 h-7 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-bold flex items-center justify-center">
                    {project.owner.full_name.charAt(0)}
                  </div>
                  <span className="text-xs text-slate-300 font-medium">
                    Led by {project.owner.full_name}
                  </span>
                </div>

                <Link
                  href={`/projects/${project.id}`}
                  className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
                >
                  View Details <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
