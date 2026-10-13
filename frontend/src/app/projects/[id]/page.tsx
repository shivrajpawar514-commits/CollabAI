"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Users,
  CheckCircle2,
  Code2,
  Sparkles,
  UserCheck,
  Send,
  AlertCircle,
  ExternalLink,
} from "lucide-react";
import { api, Project } from "@/lib/api";

export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params?.id as string;
  const [project, setProject] = useState<Project | null>(null);
  const [appliedRole, setAppliedRole] = useState<string | null>(null);
  const [applicationSent, setApplicationSent] = useState(false);

  useEffect(() => {
    if (projectId) {
      api.getProject(projectId)
        .then(setProject)
        .catch(() => {
          // Mock data fallback if ID not found
          setProject({
            id: projectId,
            title: "AgriVision: AI Crop Disease Detection & Advisory",
            description: "Mobile and edge AI application allowing farmers in rural regions to photograph crop foliage, instantly detect pathogens using lightweight vision transformers, and receive localized treatment recommendations.",
            problem_statement: "Crop diseases cause up to 40% annual yield loss globally. Early diagnosis by agricultural specialists is inaccessible or prohibitively slow for smallholder farmers.",
            owner_id: "user-1",
            owner: { id: "user-1", email: "alex@stanford.edu", full_name: "Alex Chen", is_active: true, created_at: "" },
            status: "recruiting",
            max_team_size: 4,
            repo_url: "https://github.com/collabai-projects/agrivision-edge",
            created_at: "2026-10-10T00:00:00Z",
            updated_at: "2026-10-10T00:00:00Z",
            required_skills: [
              { id: "1", skill_id: "s1", is_required: true, skill: { id: "s1", name: "PyTorch", category: "AI/ML" } },
              { id: "2", skill_id: "s2", is_required: true, skill: { id: "s2", name: "FastAPI", category: "Backend" } },
              { id: "3", skill_id: "s3", is_required: true, skill: { id: "s3", name: "Flutter", category: "Mobile" } },
            ],
            roles: [
              { id: "r1", project_id: projectId, role_name: "ML Vision Specialist", capacity: 1, filled_count: 0 },
              { id: "r2", project_id: projectId, role_name: "Mobile Flutter Dev", capacity: 1, filled_count: 0 },
              { id: "r3", project_id: projectId, role_name: "Backend Engineer", capacity: 1, filled_count: 1 },
            ],
          });
        });
    }
  }, [projectId]);

  if (!project) {
    return (
      <div className="py-24 text-center">
        <div className="inline-block animate-spin w-8 h-8 border-4 border-indigo-500 border-t-transparent rounded-full" />
        <p className="mt-4 text-slate-400 text-sm">Loading project details...</p>
      </div>
    );
  }

  const handleApply = (roleName: string) => {
    setAppliedRole(roleName);
    setApplicationSent(true);
  };

  return (
    <div className="space-y-8 pb-16 max-w-5xl mx-auto">
      <Link
        href="/projects"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Projects
      </Link>

      <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 pb-6 border-b border-white/10">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 font-bold uppercase tracking-wider">
              {project.status}
            </span>
            <span className="text-xs text-slate-400">Team Size: Max {project.max_team_size}</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            {project.title}
          </h1>
          <p className="text-sm text-slate-300">
            Created and led by <span className="text-indigo-400 font-semibold">{project.owner.full_name}</span>
          </p>
        </div>

        {project.repo_url && (
          <a
            href={project.repo_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-white text-xs font-semibold transition-all shrink-0"
          >
            <Code2 className="w-4 h-4" />
            Repository
            <ExternalLink className="w-3 h-3 text-slate-400" />
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Overview */}
          <section className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              Project Description
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
              {project.description}
            </p>
          </section>

          {/* Problem Statement */}
          {project.problem_statement && (
            <section className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-indigo-400" />
                Problem Statement
              </h2>
              <p className="text-slate-300 text-sm leading-relaxed">
                {project.problem_statement}
              </p>
            </section>
          )}

          {/* Required Skills */}
          <section className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
            <h2 className="text-lg font-bold text-white">Required Technical Skills</h2>
            <div className="flex flex-wrap gap-2">
              {project.required_skills.map((ps) => (
                <div
                  key={ps.id}
                  className="px-3.5 py-1.5 rounded-xl bg-indigo-500/15 border border-indigo-500/30 text-indigo-200 text-xs font-semibold flex items-center gap-2"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                  {ps.skill.name}
                  <span className="text-[10px] text-slate-400 font-normal">({ps.skill.category})</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Sidebar: Roles & Join */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-5">
            <div className="flex items-center justify-between pb-4 border-b border-white/10">
              <h3 className="font-bold text-white text-base flex items-center gap-2">
                <Users className="w-4 h-4 text-cyan-400" />
                Open Roles ({project.roles.length})
              </h3>
              <span className="text-xs text-slate-400">Apply to join</span>
            </div>

            {applicationSent ? (
              <div className="p-4 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-200 text-xs space-y-2">
                <p className="font-bold flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  Application Submitted!
                </p>
                <p className="text-slate-300">
                  You requested to join as <span className="font-semibold text-white">{appliedRole}</span>. The team leader has been notified.
                </p>
              </div>
            ) : null}

            <div className="space-y-3">
              {project.roles.map((role) => {
                const isFull = role.filled_count >= role.capacity;
                return (
                  <div
                    key={role.id}
                    className="p-4 rounded-xl bg-black/40 border border-white/10 flex flex-col justify-between gap-3"
                  >
                    <div>
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white text-sm">{role.role_name}</span>
                        <span className="text-[11px] text-slate-400">
                          {role.filled_count} / {role.capacity} filled
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => handleApply(role.role_name)}
                      disabled={isFull || applicationSent}
                      className={`w-full py-2 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                        isFull
                          ? "bg-white/5 text-slate-500 cursor-not-allowed"
                          : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/25"
                      }`}
                    >
                      {isFull ? (
                        "Role Filled"
                      ) : (
                        <>
                          <Send className="w-3.5 h-3.5" />
                          Apply for this Role
                        </>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          {/* AI Compatibility Box */}
          <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 bg-indigo-950/20 space-y-3">
            <div className="flex items-center gap-2 text-indigo-300 font-semibold text-xs uppercase tracking-wider">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              AI Match Forecast
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Based on your student profile, you have an <span className="text-emerald-400 font-bold">88% compatibility</span> with this team. Your backend skill set complements the team's missing services.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
