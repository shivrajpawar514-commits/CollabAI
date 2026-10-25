"use client";

import Link from "next/link";
import { useState } from "react";
import {
  Sparkles,
  Users,
  Compass,
  ArrowRight,
  Code2,
  Cpu,
  BrainCircuit,
  Layers,
  Zap,
  CheckCircle2,
  Clock,
  ExternalLink,
} from "lucide-react";

export default function HomePage() {
  const [demoIdea, setDemoIdea] = useState(
    "A privacy-preserving mobile app for farmers that diagnoses crop diseases using edge vision transformers."
  );
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedPlan, setGeneratedPlan] = useState<any | null>(null);

  const handleSimulateAI = () => {
    setIsGenerating(true);
    setTimeout(() => {
      setGeneratedPlan({
        title: "AgriVision: Edge-AI Crop Pathogen Detection",
        roles: [
          { role: "ML Vision Specialist", skills: ["PyTorch", "MobileNet/YOLO", "OpenCV"], match: "94%" },
          { role: "Mobile Engineer", skills: ["Flutter", "TensorFlow Lite", "REST"], match: "89%" },
          { role: "Backend Architect", skills: ["FastAPI", "PostgreSQL", "Docker"], match: "91%" },
        ],
        milestones: [
          "Week 1-2: Dataset gathering & baseline CNN training",
          "Week 3-4: Quantization to ONNX/TFLite & edge inference",
          "Week 5-6: Flutter cross-platform UI & offline sync",
          "Week 7: Field validation & college project showcase",
        ],
      });
      setIsGenerating(false);
    }, 900);
  };

  return (
    <div className="space-y-20 pb-16">
      {/* Hero Section */}
      <section className="text-center pt-10 sm:pt-16 max-w-4xl mx-auto space-y-6">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg border border-blue-500/30 bg-blue-500/10 text-xs font-semibold text-blue-300 backdrop-blur-md">
          <Code2 className="w-3.5 h-3.5 text-cyan-400" />
          Student Engineering & Milestone Collaboration Platform
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.15]">
          Find Teammates with <span className="text-gradient">Complementary Skills</span>. Ship Capstones Faster.
        </h1>

        <p className="text-lg sm:text-xl text-slate-300 max-w-2xl mx-auto font-normal leading-relaxed">
          CollabAI pairs engineering students based on technical skill gaps, structures complex project milestones, and coordinates repository deliverables in unified team workspaces.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            href="/projects"
            className="w-full sm:w-auto px-6 py-3.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-semibold flex items-center justify-center gap-2 shadow-lg shadow-blue-900/30 transition-all"
          >
            <Compass className="w-5 h-5 text-cyan-300" />
            Discover Projects
          </Link>
          <Link
            href="/projects/create"
            className="w-full sm:w-auto px-6 py-3.5 rounded-lg border border-white/15 bg-white/5 hover:bg-white/10 text-white font-semibold flex items-center justify-center gap-2 backdrop-blur-md transition-all"
          >
            <Layers className="w-5 h-5 text-blue-400" />
            Project Planner
          </Link>
          <Link
            href="/auth/login"
            className="w-full sm:w-auto px-5 py-3.5 text-slate-300 hover:text-white text-sm font-medium flex items-center justify-center gap-1.5 transition-colors"
          >
            Instant Demo Sign In <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* Interactive AI Project Generator Showcase */}
      <section className="max-w-4xl mx-auto">
        <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 relative overflow-hidden">
          <div className="flex items-center justify-between pb-6 border-b border-white/10">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
                <BrainCircuit className="w-5 h-5 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-white font-bold text-lg">Project Architecture & Team Planner</h3>
                <p className="text-xs text-slate-400">Describe any technical project idea in natural language: generate structured roles, milestones, and deliverables</p>
              </div>
            </div>
            <span className="text-[11px] font-semibold uppercase px-2.5 py-1 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
              Structured Pydantic Model
            </span>
          </div>

          <div className="pt-6 space-y-4">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider block">
              Enter Your Capstone or Hackathon Idea:
            </label>
            <div className="flex flex-col sm:flex-row gap-3">
              <input
                type="text"
                value={demoIdea}
                onChange={(e) => setDemoIdea(e.target.value)}
                placeholder="e.g. A decentralized code bounty platform with AI PR verification..."
                className="flex-1 bg-black/40 border border-white/15 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
              />
              <button
                onClick={handleSimulateAI}
                disabled={isGenerating}
                className="px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-sm font-semibold flex items-center justify-center gap-2 transition-all shadow-md shadow-indigo-600/30"
              >
                {isGenerating ? (
                  <>
                    <Zap className="w-4 h-4 animate-spin text-cyan-300" />
                    Planning...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-cyan-300" />
                    Generate Plan
                  </>
                )}
              </button>
            </div>

            {/* Generated Plan Output */}
            {generatedPlan && (
              <div className="mt-6 p-5 rounded-xl bg-black/50 border border-indigo-500/30 space-y-5 animate-in fade-in duration-300">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <h4 className="font-bold text-white text-base flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    {generatedPlan.title}
                  </h4>
                  <Link
                    href="/projects/create"
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1"
                  >
                    Launch this project on CollabAI <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {generatedPlan.roles.map((r: any, idx: number) => (
                    <div key={idx} className="p-3.5 rounded-lg bg-white/[0.04] border border-white/[0.08] space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-white text-xs">{r.role}</span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">
                          {r.match} fit
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {r.skills.map((s: string, sIdx: number) => (
                          <span key={sIdx} className="text-[10px] px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-200">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="space-y-2 pt-2 border-t border-white/10">
                  <span className="text-xs font-semibold text-slate-400">Roadmap Milestones:</span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-300">
                    {generatedPlan.milestones.map((m: string, mIdx: number) => (
                      <div key={mIdx} className="flex items-start gap-2">
                        <Clock className="w-3.5 h-3.5 text-cyan-400 mt-0.5 shrink-0" />
                        <span>{m}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 4 Pillars Grid */}
      <section className="max-w-6xl mx-auto space-y-10">
        <div className="text-center space-y-3">
          <h2 className="text-2xl sm:text-3xl font-bold text-white">
            Built Specifically for Student Engineering Teams
          </h2>
          <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto">
            Traditional tools like Slack, Trello, and Discord are disconnected. CollabAI unifies matching, project architecture, and execution.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="glass-panel glass-panel-hover p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="w-12 h-12 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
              <Users className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-white text-lg">Skill-Based Matching</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Calculates skill complementarity, interest vector similarity, and schedule overlap so teams don't suffer from duplicate or missing skills.
            </p>
          </div>

          <div className="glass-panel glass-panel-hover p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="w-12 h-12 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-300">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-white text-lg">Milestone Planner</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Transforms technical specs into structured Pydantic milestones, subtasks, estimated hours, and tech stack recommendations.
            </p>
          </div>

          <div className="glass-panel glass-panel-hover p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="w-12 h-12 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-300">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-white text-lg">Project-Specific RAG</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Upload research papers, PDF requirements, and architecture notes. Query your team's private vector knowledge base with citation tracing.
            </p>
          </div>

          <div className="glass-panel glass-panel-hover p-6 rounded-2xl border border-white/10 space-y-4">
            <div className="w-12 h-12 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-300">
              <Code2 className="w-6 h-6" />
            </div>
            <h3 className="font-bold text-white text-lg">100% Free-Tier Stack</h3>
            <p className="text-sm text-slate-400 leading-relaxed">
              Designed to run on free tools: Gemini Free, Groq, Ollama, pgvector on Neon/Supabase, and Docker Compose locally.
            </p>
          </div>
        </div>
      </section>

      {/* Call to action */}
      <section className="glass-panel p-8 sm:p-12 rounded-2xl border border-blue-500/20 text-center max-w-4xl mx-auto space-y-6 relative overflow-hidden">
        <h2 className="text-2xl sm:text-4xl font-extrabold text-white">
          Ready to kick off your next student project?
        </h2>
        <p className="text-slate-300 text-sm sm:text-base max-w-lg mx-auto">
          Explore over 20 seeded student projects or log in with the instant demo account to test the complete workflow.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            href="/projects"
            className="px-6 py-3 rounded-lg bg-white text-black font-semibold hover:bg-slate-200 transition-all text-sm shadow-md"
          >
            Explore Projects
          </Link>
          <Link
            href="/auth/login"
            className="px-6 py-3 rounded-lg border border-white/20 bg-white/5 hover:bg-white/10 text-white font-semibold transition-all text-sm backdrop-blur-md"
          >
            Launch Demo Student
          </Link>
        </div>
      </section>
    </div>
  );
}
