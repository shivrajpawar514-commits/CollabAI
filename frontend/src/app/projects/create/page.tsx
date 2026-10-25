"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Sparkles,
  Zap,
  Plus,
  Trash2,
  CheckCircle,
  FolderPlus,
} from "lucide-react";
import { api, getAuthToken, ProjectProposal } from "@/lib/api";

export default function CreateProjectPage() {
  const router = useRouter();

  // AI Generator state
  const [ideaPrompt, setIdeaPrompt] = useState("");
  const [isAiGenerating, setIsAiGenerating] = useState(false);
  const [aiProposal, setAiProposal] = useState<ProjectProposal | null>(null);

  // Form state
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [problemStatement, setProblemStatement] = useState("");
  const [maxTeamSize, setMaxTeamSize] = useState(4);
  const [repoUrl, setRepoUrl] = useState("");

  const [roles, setRoles] = useState<{ role_name: string; capacity: number }[]>([
    { role_name: "Frontend Developer", capacity: 1 },
    { role_name: "Backend Developer", capacity: 1 },
  ]);

  const [selectedSkills, setSelectedSkills] = useState<string[]>([
    "Python", "FastAPI", "React"
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAiAutoFill = async () => {
    if (!ideaPrompt.trim()) return;
    setIsAiGenerating(true);
    setError(null);

    try {
      const res = await api.generateProject(ideaPrompt);
      setAiProposal(res);
      setTitle(res.title);
      setProblemStatement(res.problem_statement);
      const desc = `${res.architecture}\n\nObjectives:\n- ` + res.objectives.join("\n- ");
      setDescription(desc);
      setMaxTeamSize(Math.max(3, res.roles_needed?.length || 4));
      if (res.roles_needed?.length) {
        setRoles(res.roles_needed.map((r) => ({ role_name: r.role_name, capacity: r.capacity || 1 })));
      }
      if (res.technologies?.length) {
        setSelectedSkills(res.technologies);
      }
    } catch (err: any) {
      setError(err.message || "AI Proposal generation failed. Please try again.");
    } finally {
      setIsAiGenerating(false);
    }
  };


  const handleAddRole = () => {
    setRoles([...roles, { role_name: "", capacity: 1 }]);
  };

  const handleRemoveRole = (index: number) => {
    setRoles(roles.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const token = getAuthToken();
    if (!token) {
      // Prompt sign in or redirect
      setError("Please sign in or use the demo login before posting a project.");
      setLoading(false);
      return;
    }

    try {
      // Call backend createProject
      await api.createProject({
        title,
        description,
        problem_statement: problemStatement,
        max_team_size: maxTeamSize,
        repo_url: repoUrl || undefined,
        status: "recruiting",
        skills: [],
        roles: roles.filter((r) => r.role_name.trim().length > 0),
      });

      router.push("/projects");
    } catch (err: any) {
      setError(err.message || "Failed to create project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 pb-16">
      <Link
        href="/projects"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Projects
      </Link>

      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
          Create New Project
        </h1>
        <p className="text-sm text-slate-400">
          Publish your capstone or hackathon idea and let complementary teammates discover you.
        </p>
      </div>

      {/* AI Assistant Generator Panel */}
      <div className="glass-panel p-6 rounded-2xl border border-blue-500/20 bg-gradient-to-br from-blue-950/30 to-slate-900/30 space-y-4">
        <div className="flex items-center gap-2 text-blue-300 font-bold text-sm">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          Project Architecture Planner
        </div>
        <p className="text-xs text-slate-300">
          Have an idea but not sure how to break it into milestones, roles, and tech stacks? Describe it here and our planner will outline it.
        </p>
        <div className="flex gap-2">
          <input
            type="text"
            value={ideaPrompt}
            onChange={(e) => setIdeaPrompt(e.target.value)}
            placeholder="e.g. A privacy-preserving biometric audio tool for students..."
            className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <button
            type="button"
            onClick={handleAiAutoFill}
            disabled={isAiGenerating}
            className="px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-1.5 shrink-0 transition-all shadow-md shadow-blue-900/30"
          >
            {isAiGenerating ? (
              <Zap className="w-4 h-4 animate-spin text-cyan-300" />
            ) : (
              <Sparkles className="w-4 h-4 text-cyan-300" />
            )}
            Auto-Fill Form
          </button>
        </div>

        {aiProposal && (
          <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-500/30 space-y-3 animate-in fade-in duration-300">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <CheckCircle className="w-3.5 h-3.5 text-cyan-400" />
                Project Proposal Outline Generated
              </span>
              <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded-md font-semibold">
                Form Pre-filled Below
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-2.5 rounded-lg bg-black/40 border border-white/5 space-y-1">
                <span className="text-slate-400 font-semibold block text-[11px]">Architecture:</span>
                <p className="text-slate-200 line-clamp-3">{aiProposal.architecture}</p>
              </div>

              <div className="p-2.5 rounded-lg bg-black/40 border border-white/5 space-y-1">
                <span className="text-slate-400 font-semibold block text-[11px]">Recommended Tech Stack:</span>
                <div className="flex flex-wrap gap-1">
                  {aiProposal.technologies.map((t, idx) => (
                    <span key={idx} className="px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-[10px]">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {aiProposal.timeline_weeks?.length > 0 && (
              <div className="pt-2 border-t border-white/5">
                <span className="text-[11px] font-semibold text-slate-400 block mb-1.5">Roadmap Phases ({aiProposal.timeline_weeks.length} Weeks):</span>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  {aiProposal.timeline_weeks.slice(0, 3).map((w, idx) => (
                    <div key={idx} className="p-2 rounded bg-black/30 border border-white/5 text-[10px]">
                      <span className="text-cyan-400 font-bold block">{w.title}</span>
                      <span className="text-slate-400 line-clamp-1">{w.deliverables?.join(", ")}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>


      {error && (
        <div className="p-4 rounded-xl bg-red-500/15 border border-red-500/30 text-red-200 text-xs">
          {error}
        </div>
      )}

      {/* Main Form */}
      <form onSubmit={handleSubmit} className="glass-panel p-8 rounded-2xl border border-white/10 space-y-6">
        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
            Project Title *
          </label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. AgriVision: Edge Crop Disease Advisory"
            className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
            Problem Statement
          </label>
          <textarea
            rows={2}
            value={problemStatement}
            onChange={(e) => setProblemStatement(e.target.value)}
            placeholder="What real-world problem does this project tackle?"
            className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="space-y-2">
          <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
            Project Description *
          </label>
          <textarea
            rows={4}
            required
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the solution architecture, deliverables, and goals..."
            className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
              Max Team Size
            </label>
            <input
              type="number"
              min={2}
              max={10}
              value={maxTeamSize}
              onChange={(e) => setMaxTeamSize(parseInt(e.target.value))}
              className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
              Repository URL (Optional)
            </label>
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/your-org/repo"
              className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />
          </div>
        </div>

        {/* Roles Needed Builder */}
        <div className="space-y-3 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
              Open Team Roles Needed
            </label>
            <button
              type="button"
              onClick={handleAddRole}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1"
            >
              <Plus className="w-3.5 h-3.5" /> Add Role
            </button>
          </div>

          <div className="space-y-3">
            {roles.map((r, idx) => (
              <div key={idx} className="flex items-center gap-3">
                <input
                  type="text"
                  placeholder="Role name (e.g. ML Vision Engineer)"
                  value={r.role_name}
                  onChange={(e) => {
                    const updated = [...roles];
                    updated[idx].role_name = e.target.value;
                    setRoles(updated);
                  }}
                  className="flex-1 bg-[#0e111d] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                />
                <input
                  type="number"
                  min={1}
                  max={5}
                  value={r.capacity}
                  onChange={(e) => {
                    const updated = [...roles];
                    updated[idx].capacity = parseInt(e.target.value);
                    setRoles(updated);
                  }}
                  className="w-20 bg-[#0e111d] border border-white/10 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500 text-center"
                  title="Capacity"
                />
                {roles.length > 1 && (
                  <button
                    type="button"
                    onClick={() => handleRemoveRole(idx)}
                    className="p-2 text-slate-500 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm shadow-md shadow-blue-900/30 transition-all flex items-center justify-center gap-2"
        >
          {loading ? "Publishing..." : "Publish Project"}
        </button>
      </form>
    </div>
  );
}
