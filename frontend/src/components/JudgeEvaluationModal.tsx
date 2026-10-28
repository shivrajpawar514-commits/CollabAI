"use client";

import { useState } from "react";
import {
  X,
  Trophy,
  Award,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  ShieldCheck,
  HelpCircle,
  Lightbulb,
  Layers,
  ChevronRight,
  TrendingUp,
} from "lucide-react";

export interface CriteriaScore {
  name: string;
  score: number;
  weight: number;
  strengths: string[];
  areas_for_improvement: string[];
  judge_tips: string;
}

export interface JudgePersonaCritique {
  judge_role: string;
  verdict_score: number;
  overall_impression: string;
  key_positive: string;
  hard_question_to_prepare: string;
}

export interface HackathonJudgeEvaluation {
  project_title: string;
  overall_score: number;
  percentile_rank_estimate: string;
  verdict_badge: string;
  criteria_breakdown: CriteriaScore[];
  judge_personas: JudgePersonaCritique[];
  top_action_items_before_pitch: string[];
  raw_executive_critique: string;
}

interface JudgeEvaluationModalProps {
  isOpen: boolean;
  onClose: () => void;
  evaluation: HackathonJudgeEvaluation | null;
  loading: boolean;
  onRefresh: () => void;
}

export default function JudgeEvaluationModal({
  isOpen,
  onClose,
  evaluation,
  loading,
  onRefresh,
}: JudgeEvaluationModalProps) {
  const [activeTab, setActiveTab] = useState<"rubric" | "personas" | "checklist">("rubric");

  if (!isOpen) return null;

  const score = evaluation?.overall_score ?? 88;
  const badge = evaluation?.verdict_badge ?? "⭐ Finalist Contender";
  const rank = evaluation?.percentile_rank_estimate ?? "Top 8% of Hackathon Submissions";

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      <div className="glass-panel w-full max-w-4xl bg-[#090c17] border border-white/15 rounded-2xl overflow-hidden flex flex-col max-h-[90vh] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-amber-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-tight">
                  Hackathon Judge Simulator
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-indigo-500/10 border border-indigo-500/30 text-indigo-300">
                  5-Pillar Rubric
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Simulated judging panel evaluation, persona critiques, and pitch Q&A readiness
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={onRefresh}
              disabled={loading}
              className="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-slate-300 text-xs font-medium transition-all flex items-center gap-1.5 disabled:opacity-50"
              title="Re-run simulated evaluation"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-amber-400" : ""}`} />
              {loading ? "Evaluating..." : "Re-evaluate"}
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Score & Verdict Banner */}
        <div className="px-6 py-4 border-b border-white/10 bg-gradient-to-r from-amber-500/[0.05] via-indigo-500/[0.03] to-transparent flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-extrabold text-white">{score}</span>
              <span className="text-sm text-slate-400 font-medium">/100</span>
            </div>
            <div className="h-8 w-px bg-white/10" />
            <div>
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-300 bg-amber-500/10 border border-amber-500/30 px-2.5 py-0.5 rounded-full">
                {badge}
              </span>
              <p className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                <TrendingUp className="w-3 h-3 text-emerald-400" />
                {rank}
              </p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center gap-1.5 bg-white/[0.03] border border-white/10 p-1 rounded-xl">
            {[
              { id: "rubric", label: "Rubric Scores (5)", icon: Layers },
              { id: "personas", label: "Judge Personas (3)", icon: Award },
              { id: "checklist", label: "Pitch Prep Checklist", icon: ShieldCheck },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm"
                      : "text-slate-400 hover:text-white hover:bg-white/[0.04]"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3">
              <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-400">Simulating Hackathon Judging Panel Evaluation...</p>
            </div>
          ) : (
            <>
              {/* TAB 1: RUBRIC BREAKDOWN */}
              {activeTab === "rubric" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {(evaluation?.criteria_breakdown || []).map((crit, idx) => {
                      const pct = Math.round((crit.score / 20) * 100);
                      const barColor =
                        crit.score >= 18
                          ? "bg-emerald-400"
                          : crit.score >= 15
                          ? "bg-cyan-400"
                          : "bg-amber-400";

                      return (
                        <div
                          key={idx}
                          className="p-4 rounded-xl bg-white/[0.02] border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between"
                        >
                          <div>
                            <div className="flex items-center justify-between mb-2">
                              <h4 className="text-xs font-bold text-white tracking-tight flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                                {crit.name}
                              </h4>
                              <span className="text-xs font-extrabold text-amber-300 font-mono">
                                {crit.score} <span className="text-[10px] text-slate-500">/ 20</span>
                              </span>
                            </div>

                            {/* Progress bar */}
                            <div className="w-full h-1.5 bg-white/[0.08] rounded-full overflow-hidden mb-3">
                              <div
                                className={`h-full ${barColor} rounded-full transition-all duration-500`}
                                style={{ width: `${pct}%` }}
                              />
                            </div>

                            {/* Strengths */}
                            <div className="space-y-1.5 mb-3">
                              <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                                Observed Strengths:
                              </p>
                              {crit.strengths.map((str, sIdx) => (
                                <div key={sIdx} className="flex items-start gap-1.5 text-xs text-slate-300">
                                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                                  <span>{str}</span>
                                </div>
                              ))}
                            </div>

                            {/* Constructive improvement */}
                            {crit.areas_for_improvement && crit.areas_for_improvement.length > 0 && (
                              <div className="space-y-1 mb-3">
                                <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                                  Area to Strengthen:
                                </p>
                                {crit.areas_for_improvement.map((area, aIdx) => (
                                  <div key={aIdx} className="flex items-start gap-1.5 text-xs text-amber-200/90">
                                    <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                                    <span>{area}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>

                          {/* Targeted tip */}
                          <div className="mt-2 pt-2.5 border-t border-white/[0.06] flex items-start gap-2 bg-amber-500/[0.03] p-2.5 rounded-lg border border-amber-500/15">
                            <Lightbulb className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                            <p className="text-[11px] text-amber-200/90 leading-relaxed">
                              <span className="font-semibold text-amber-300">Pitch Tip: </span>
                              {crit.judge_tips}
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {/* Executive Panel Summary */}
                  {evaluation?.raw_executive_critique && (
                    <div className="p-4 rounded-xl bg-white/[0.03] border border-white/10 mt-4">
                      <h4 className="text-xs font-bold text-white mb-1.5 flex items-center gap-1.5">
                        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                        Executive Judging Panel Consensus
                      </h4>
                      <p className="text-xs text-slate-300 leading-relaxed">
                        {evaluation.raw_executive_critique}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* TAB 2: JUDGE PERSONA REVIEWS */}
              {activeTab === "personas" && (
                <div className="space-y-4">
                  {(evaluation?.judge_personas || []).map((persona, pIdx) => (
                    <div
                      key={pIdx}
                      className="p-5 rounded-xl bg-white/[0.02] border border-white/10 hover:border-white/20 transition-all space-y-3.5"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center">
                            <Award className="w-4 h-4 text-indigo-400" />
                          </div>
                          <div>
                            <h4 className="text-sm font-bold text-white">{persona.judge_role}</h4>
                            <p className="text-[10px] text-slate-400">Independent Persona Evaluation</p>
                          </div>
                        </div>
                        <span className="px-3 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 font-mono font-bold text-xs">
                          {persona.verdict_score} / 100
                        </span>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed italic">
                        "{persona.overall_impression}"
                      </p>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-2">
                        <div className="p-3 rounded-lg bg-emerald-500/[0.04] border border-emerald-500/20">
                          <p className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" />
                            Key Impressive Element
                          </p>
                          <p className="text-xs text-slate-200">{persona.key_positive}</p>
                        </div>

                        <div className="p-3 rounded-lg bg-amber-500/[0.04] border border-amber-500/20">
                          <p className="text-[10px] font-bold text-amber-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                            <HelpCircle className="w-3 h-3" />
                            Tough Pitch Q&A Question to Prepare
                          </p>
                          <p className="text-xs text-amber-200/95 font-medium">
                            "{persona.hard_question_to_prepare}"
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* TAB 3: PITCH PREP CHECKLIST */}
              {activeTab === "checklist" && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl bg-indigo-500/[0.05] border border-indigo-500/20">
                    <h4 className="text-xs font-bold text-indigo-300 mb-1 flex items-center gap-1.5">
                      <ShieldCheck className="w-4 h-4 text-indigo-400" />
                      Final Presentation Checklist Before Pitching to Judges
                    </h4>
                    <p className="text-xs text-slate-400">
                      High-impact adjustments calculated by the judging panel to maximize your demo presentation.
                    </p>
                  </div>

                  <div className="space-y-2.5">
                    {(evaluation?.top_action_items_before_pitch || []).map((item, iIdx) => (
                      <div
                        key={iIdx}
                        className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 hover:border-white/20 transition-all flex items-start gap-3"
                      >
                        <div className="w-6 h-6 rounded-md bg-amber-500/10 border border-amber-500/30 flex items-center justify-center shrink-0 mt-0.5">
                          <span className="text-xs font-mono font-bold text-amber-300">{iIdx + 1}</span>
                        </div>
                        <div className="flex-1">
                          <p className="text-xs text-slate-200 font-medium leading-relaxed">{item}</p>
                        </div>
                        <CheckCircle2 className="w-4 h-4 text-slate-600 shrink-0 mt-0.5" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-white/10 bg-white/[0.01] flex items-center justify-between text-xs text-slate-400">
          <span>
            {evaluation?.project_title || "Project"} • Simulated against Devpost/Major League Hacking standards
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-md transition-all"
          >
            Done Reviewing
          </button>
        </div>
      </div>
    </div>
  );
}
