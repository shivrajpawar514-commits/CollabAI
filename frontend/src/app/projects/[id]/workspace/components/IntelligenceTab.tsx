"use client";

import { useState, useEffect } from "react";
import {
  Zap,
  Target,
  BrainCircuit,
  Users,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Clock,
  CheckCircle2,
  TrendingUp,
  Sparkles,
  BookOpen,
  ExternalLink,
  ChevronRight,
  UserPlus,
  X,
  RefreshCw,
  Loader2,
  Award,
  Layers,
  ArrowRight,
  GraduationCap,
  Activity,
} from "lucide-react";
import {
  api,
  DeadlineRiskReport,
  SkillGapAnalysis,
  TeammateMatchV2Response,
  CandidateMatchV2,
  LearningStep,
} from "@/lib/api";

interface IntelligenceTabProps {
  projectId: string;
  projectTitle: string;
}

export default function IntelligenceTab({ projectId, projectTitle }: IntelligenceTabProps) {
  const [activeSubTab, setActiveSubTab] = useState<"risk" | "skill_graph" | "matching">("risk");

  // State
  const [riskData, setRiskData] = useState<DeadlineRiskReport | null>(null);
  const [skillGapData, setSkillGapData] = useState<SkillGapAnalysis | null>(null);
  const [matchData, setMatchData] = useState<TeammateMatchV2Response | null>(null);

  const [loadingRisk, setLoadingRisk] = useState(false);
  const [loadingGap, setLoadingGap] = useState(false);
  const [loadingMatch, setLoadingMatch] = useState(false);

  // Candidate Feedback Action State
  const [feedbackSuccess, setFeedbackSuccess] = useState<string | null>(null);
  const [dismissedUserIds, setDismissedUserIds] = useState<string[]>([]);

  // Fetch functions
  const fetchRisk = async () => {
    try {
      setLoadingRisk(true);
      const res = await api.getDeadlineRisk(projectId);
      setRiskData(res);
    } catch (err: any) {
      console.error("Failed to load deadline risk:", err);
    } finally {
      setLoadingRisk(false);
    }
  };

  const fetchSkillGap = async () => {
    try {
      setLoadingGap(true);
      const res = await api.getSkillGap(projectId);
      setSkillGapData(res);
    } catch (err: any) {
      console.error("Failed to load skill gap:", err);
    } finally {
      setLoadingGap(false);
    }
  };

  const fetchMatching = async () => {
    try {
      setLoadingMatch(true);
      const res = await api.getTeammateRecommendationsV2(projectId);
      setMatchData(res);
    } catch (err: any) {
      console.error("Failed to load teammate matches:", err);
    } finally {
      setLoadingMatch(false);
    }
  };

  useEffect(() => {
    fetchRisk();
    fetchSkillGap();
    fetchMatching();
  }, [projectId]);

  // Handle Candidate Action & Feedback Loop
  const handleCandidateAction = async (
    candidate: CandidateMatchV2,
    action: "accepted" | "invited" | "dismissed"
  ) => {
    try {
      // 1. Log to ML telemetry loop
      await api.logRecommendationFeedback(projectId, {
        candidate_id: candidate.user_id,
        action,
        match_score: candidate.match_score,
        ml_rank_score: candidate.ml_rank_score,
        feature_vector_json: candidate.feature_importance,
      });

      if (action === "dismissed") {
        setDismissedUserIds((prev) => [...prev, candidate.user_id]);
      } else {
        setFeedbackSuccess(`Candidate ${candidate.name} ${action}! Telemetry recorded for ML retraining.`);
        setTimeout(() => setFeedbackSuccess(null), 4000);
      }
    } catch (err: any) {
      alert("Failed to log candidate action: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-amber-950/40 via-purple-950/30 to-indigo-950/40 border border-amber-500/20 p-6 backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30">
                <Zap className="w-4 h-4" />
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                ML Intelligence & Skill Graph
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Phase 5
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
              Gradient-boosted sprint deadline risk classification, NetworkX topological skill learning paths with free MIT & freeCodeCamp courses, and XGBoost teammate ranking with live feedback loops.
            </p>
          </div>

          {/* Sub-tabs selector */}
          <div className="flex items-center gap-1.5 p-1 rounded-xl bg-black/40 border border-white/10 self-start md:self-auto">
            <button
              onClick={() => setActiveSubTab("risk")}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeSubTab === "risk"
                  ? "bg-amber-500 text-black shadow-md shadow-amber-500/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Target className="w-3.5 h-3.5" />
              Deadline Risk
            </button>
            <button
              onClick={() => setActiveSubTab("skill_graph")}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeSubTab === "skill_graph"
                  ? "bg-purple-600 text-white shadow-md shadow-purple-600/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <BrainCircuit className="w-3.5 h-3.5" />
              Skill Graph
            </button>
            <button
              onClick={() => setActiveSubTab("matching")}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeSubTab === "matching"
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              <Users className="w-3.5 h-3.5" />
              XGBoost Matching
            </button>
          </div>
        </div>

        {feedbackSuccess && (
          <div className="mt-4 p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{feedbackSuccess}</span>
          </div>
        )}
      </div>

      {/* SUB-TAB 1: DEADLINE RISK & VELOCITY */}
      {activeSubTab === "risk" && (
        <div className="space-y-6">
          {loadingRisk ? (
            <div className="py-20 flex flex-col items-center gap-3 text-slate-400">
              <Loader2 className="w-7 h-7 animate-spin text-amber-400" />
              <span className="text-xs">Computing sprint velocity & deadline risk gradient features...</span>
            </div>
          ) : !riskData ? (
            <div className="p-8 text-center text-xs text-slate-500">
              Unable to calculate sprint metrics. Ensure tasks are initialized.
            </div>
          ) : (
            <>
              {/* Risk Gauge Header Card */}
              <div
                className={`p-6 rounded-2xl border backdrop-blur-xl transition-all ${
                  riskData.risk_level === "CRITICAL"
                    ? "bg-rose-950/20 border-rose-500/30"
                    : riskData.risk_level === "HIGH"
                    ? "bg-amber-950/20 border-amber-500/30"
                    : riskData.risk_level === "MEDIUM"
                    ? "bg-cyan-950/20 border-cyan-500/30"
                    : "bg-emerald-950/20 border-emerald-500/30"
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div className="flex items-start gap-4">
                    <div
                      className={`p-3.5 rounded-2xl border ${
                        riskData.risk_level === "CRITICAL"
                          ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
                          : riskData.risk_level === "HIGH"
                          ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                          : riskData.risk_level === "MEDIUM"
                          ? "bg-cyan-500/20 text-cyan-400 border-cyan-500/30"
                          : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                      }`}
                    >
                      {riskData.risk_level === "LOW" ? (
                        <ShieldCheck className="w-8 h-8" />
                      ) : riskData.risk_level === "MEDIUM" ? (
                        <Activity className="w-8 h-8" />
                      ) : (
                        <ShieldAlert className="w-8 h-8" />
                      )}
                    </div>
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                          Sprint Delivery Risk Classification
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider ${
                            riskData.risk_level === "CRITICAL"
                              ? "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                              : riskData.risk_level === "HIGH"
                              ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                              : riskData.risk_level === "MEDIUM"
                              ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40"
                              : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                          }`}
                        >
                          {riskData.risk_level} RISK
                        </span>
                      </div>
                      <h3 className="text-2xl font-black text-white">
                        {Math.round(riskData.risk_score * 100)}% Probability of Milestone Slip
                      </h3>
                      <p className="text-xs text-slate-400 max-w-xl">
                        {riskData.projected_delay_days === 0
                          ? "Engineering velocity is optimal; milestones are projected to complete on or ahead of schedule."
                          : `Team pace indicates an estimated ${riskData.projected_delay_days} days delivery slippage without scope adjustment or task unblocking.`}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4">
                    <button
                      onClick={fetchRisk}
                      className="px-3.5 py-2 rounded-xl bg-white/[0.05] hover:bg-white/10 text-slate-300 text-xs font-semibold flex items-center gap-2 border border-white/10 transition-colors"
                    >
                      <RefreshCw className="w-3.5 h-3.5" />
                      Re-evaluate
                    </button>
                  </div>
                </div>
              </div>

              {/* 4 KPI Metrics */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Completion Rate</span>
                  <div className="text-2xl font-bold text-white">{riskData.completion_rate}%</div>
                  <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden mt-2">
                    <div
                      className="bg-indigo-500 h-full rounded-full"
                      style={{ width: `${riskData.completion_rate}%` }}
                    />
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1">
                    {riskData.total_tasks - riskData.remaining_tasks} of {riskData.total_tasks} tasks closed
                  </p>
                </div>

                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Velocity Comparison</span>
                  <div className="text-2xl font-bold text-cyan-400">
                    {riskData.current_velocity_per_week}{" "}
                    <span className="text-xs text-slate-400 font-normal">/ {riskData.required_velocity_per_week} req</span>
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Tasks/week completed vs needed pace
                  </p>
                  <span
                    className={`inline-block mt-1 text-[10px] font-semibold px-2 py-0.5 rounded ${
                      riskData.current_velocity_per_week >= riskData.required_velocity_per_week
                        ? "bg-emerald-500/10 text-emerald-400"
                        : "bg-rose-500/10 text-rose-400"
                    }`}
                  >
                    {riskData.current_velocity_per_week >= riskData.required_velocity_per_week
                      ? "Pace on Track"
                      : "Velocity Deficit"}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Blocked Dependencies</span>
                  <div className="text-2xl font-bold text-amber-400">{riskData.blocked_tasks}</div>
                  <p className="text-[10px] text-slate-400">Tasks waiting on unmet prerequisites</p>
                  <span className="text-[10px] text-slate-500">
                    {riskData.blocked_tasks > 0 ? "Requires upstream triage" : "No active dependency blockers"}
                  </span>
                </div>

                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-slate-400">Days to Deadline</span>
                  <div className="text-2xl font-bold text-purple-400">
                    {riskData.days_left}{" "}
                    <span className="text-xs text-slate-400 font-normal">days</span>
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Team size: {riskData.team_size} {riskData.team_size === 1 ? "engineer" : "engineers"}
                  </p>
                  <span className="text-[10px] text-slate-500">
                    {(riskData.remaining_tasks / riskData.team_size).toFixed(1)} tasks/engineer load
                  </span>
                </div>
              </div>

              {/* 2-Column Details: Bottlenecks & Mitigations */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Bottlenecks */}
                <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    Identified Engineering Bottlenecks ({riskData.bottlenecks.length})
                  </h4>
                  <div className="space-y-2">
                    {riskData.bottlenecks.map((b, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-xl bg-amber-500/[0.04] border border-amber-500/20 text-xs text-slate-300 flex items-start gap-2.5"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 shrink-0" />
                        <span>{b}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Mitigations */}
                <div className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    AI Actionable Mitigations ({riskData.mitigation_suggestions.length})
                  </h4>
                  <div className="space-y-2">
                    {riskData.mitigation_suggestions.map((m, i) => (
                      <div
                        key={i}
                        className="p-3 rounded-xl bg-cyan-500/[0.04] border border-cyan-500/20 text-xs text-slate-300 flex items-start gap-2.5"
                      >
                        <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                        <span>{m}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* SUB-TAB 2: NETWORKX SKILL GRAPH & CURRICULUM */}
      {activeSubTab === "skill_graph" && (
        <div className="space-y-6">
          {loadingGap ? (
            <div className="py-20 flex flex-col items-center gap-3 text-slate-400">
              <Loader2 className="w-7 h-7 animate-spin text-purple-400" />
              <span className="text-xs">Traversing NetworkX skill prerequisite DAG & curriculum...</span>
            </div>
          ) : !skillGapData ? (
            <div className="p-8 text-center text-xs text-slate-500">
              Unable to analyze team skills.
            </div>
          ) : (
            <>
              {/* Coverage Header */}
              <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 space-y-4 backdrop-blur-xl">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <GraduationCap className="w-5 h-5 text-purple-400" />
                      <h3 className="text-base font-bold text-white">
                        Team Skill Gap & Prerequisite Curriculum
                      </h3>
                    </div>
                    <p className="text-xs text-slate-400 max-w-xl">
                      Topological DAG sort bridges missing project competencies through an ordered learning path with curated free MIT, freeCodeCamp, and official documentation resources.
                    </p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-2xl font-black text-purple-400">
                        {skillGapData.coverage_percentage}%
                      </div>
                      <div className="text-[10px] uppercase font-bold text-slate-400">
                        Skill Coverage
                      </div>
                    </div>
                    <div className="text-right border-l border-white/10 pl-4">
                      <div className="text-2xl font-black text-cyan-400">
                        {skillGapData.total_learning_hours}
                      </div>
                      <div className="text-[10px] uppercase font-bold text-slate-400">
                        Total Est. Hours
                      </div>
                    </div>
                  </div>
                </div>

                {/* Skill Matrix Tags */}
                <div className="pt-4 border-t border-white/5 space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold text-slate-400 mr-2">Covered by Team:</span>
                    {skillGapData.team_owned_skills.length === 0 ? (
                      <span className="text-xs text-slate-500">No profile skills registered yet</span>
                    ) : (
                      skillGapData.team_owned_skills.map((s) => (
                        <span
                          key={s}
                          className="px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5"
                        >
                          <CheckCircle2 className="w-3 h-3" />
                          {s}
                        </span>
                      ))
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs font-semibold text-slate-400 mr-2">Missing Skill Gaps:</span>
                    {skillGapData.missing_skills.length === 0 ? (
                      <span className="text-xs text-emerald-400 font-semibold">
                        All project required skills are covered!
                      </span>
                    ) : (
                      skillGapData.missing_skills.map((s) => (
                        <span
                          key={s}
                          className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1.5"
                        >
                          <AlertTriangle className="w-3 h-3" />
                          {s}
                        </span>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Recommended Learning Path Stepper */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <BrainCircuit className="w-4 h-4 text-purple-400" />
                    Topologically Ordered Learning Path ({skillGapData.recommended_learning_path.length} Steps)
                  </h4>
                  <span className="text-[10px] text-slate-500">
                    NetworkX Directed Acyclic Graph (DAG) Traversal
                  </span>
                </div>

                <div className="space-y-3">
                  {skillGapData.recommended_learning_path.map((step) => (
                    <div
                      key={step.step_number}
                      className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 hover:border-purple-500/30 transition-all space-y-3"
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                        <div className="flex items-center gap-3">
                          <span className="flex items-center justify-center w-7 h-7 rounded-xl bg-purple-500/20 text-purple-300 text-xs font-black border border-purple-500/30">
                            {step.step_number}
                          </span>
                          <div>
                            <div className="flex items-center gap-2">
                              <h5 className="text-sm font-bold text-white">{step.skill_name}</h5>
                              {step.is_direct_requirement ? (
                                <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">
                                  REQUIRED GAP
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-slate-500/20 text-slate-300 border border-slate-500/30">
                                  PREREQUISITE
                                </span>
                              )}
                            </div>
                            <span className="text-[10px] text-slate-400">
                              {step.category} &bull; {step.difficulty} Level &bull; ~{step.estimated_hours} Hours
                            </span>
                          </div>
                        </div>

                        {step.prerequisites.length > 0 && (
                          <div className="flex items-center gap-1.5 text-xs text-slate-400">
                            <span className="text-[10px] text-slate-500">Prereqs:</span>
                            {step.prerequisites.map((p) => (
                              <span
                                key={p}
                                className="px-2 py-0.5 rounded bg-white/5 text-slate-300 text-[10px]"
                              >
                                {p}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Free Resources Links */}
                      {step.free_resources.length > 0 && (
                        <div className="pt-2 border-t border-white/5 space-y-1.5">
                          <span className="text-[10px] uppercase font-bold text-slate-500">
                            Free Open-Access Courses & Documentation:
                          </span>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                            {step.free_resources.map((res, i) => (
                              <a
                                key={i}
                                href={res.url}
                                target="_blank"
                                rel="noreferrer"
                                className="p-2.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.07] border border-white/5 hover:border-purple-500/30 text-xs text-slate-300 flex items-center justify-between group transition-all"
                              >
                                <div className="min-w-0 pr-2">
                                  <div className="font-semibold text-white truncate group-hover:text-purple-300 transition-colors">
                                    {res.title}
                                  </div>
                                  <span className="text-[10px] text-slate-500">{res.provider}</span>
                                </div>
                                <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-purple-400 shrink-0" />
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* SUB-TAB 3: XGBOOST TEAMMATE MATCHING (v2/v3) */}
      {activeSubTab === "matching" && (
        <div className="space-y-6">
          {loadingMatch ? (
            <div className="py-20 flex flex-col items-center gap-3 text-slate-400">
              <Loader2 className="w-7 h-7 animate-spin text-indigo-400" />
              <span className="text-xs">Running XGBoost candidate ranking & feature attribution...</span>
            </div>
          ) : !matchData || matchData.recommendations.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No candidates found. Ensure other students are registered in the system.
            </div>
          ) : (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-bold text-white">
                    ML-Ranked Candidate Pool ({matchData.recommendations.filter(c => !dismissedUserIds.includes(c.user_id)).length})
                  </h4>
                  <p className="text-xs text-slate-400">
                    Ranked by mutual acceptance probability via Gradient Boosted Decision Trees (XGBoost).
                  </p>
                </div>
                <span className="text-[10px] text-slate-500">
                  {matchData.total_analyzed} students analyzed
                </span>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {matchData.recommendations
                  .filter((c) => !dismissedUserIds.includes(c.user_id))
                  .map((cand) => (
                    <div
                      key={cand.user_id}
                      className="p-5 rounded-2xl bg-white/[0.02] border border-white/10 hover:border-indigo-500/30 transition-all space-y-4"
                    >
                      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                        {/* Student Info */}
                        <div className="flex items-start gap-3.5">
                          <div className="w-11 h-11 rounded-2xl bg-indigo-500/20 text-indigo-300 font-bold flex items-center justify-center border border-indigo-500/30 text-sm">
                            {cand.name.charAt(0)}
                          </div>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h5 className="text-sm font-bold text-white">{cand.name}</h5>
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                                {cand.ml_rank_score}% ML Rank
                              </span>
                            </div>
                            <p className="text-xs text-slate-400">
                              {cand.branch || "Computer Science"} &bull; {cand.college || "Engineering College"} &bull; {cand.year || "3rd Year"}
                            </p>
                            <p className="text-xs text-indigo-200/80 max-w-xl">
                              {cand.explanation}
                            </p>
                          </div>
                        </div>

                        {/* Acceptance Probability Score */}
                        <div className="flex items-center gap-3 self-end md:self-start">
                          <div className="text-right">
                            <div className="text-xl font-black text-emerald-400">
                              {Math.round(cand.acceptance_probability * 100)}%
                            </div>
                            <div className="text-[9px] uppercase font-bold text-slate-400">
                              Acceptance Prob.
                            </div>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <button
                              onClick={() => handleCandidateAction(cand, "invited")}
                              className="px-3.5 py-1.5 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/25 flex items-center gap-1.5 transition-all"
                            >
                              <UserPlus className="w-3.5 h-3.5" />
                              Invite
                            </button>
                            <button
                              onClick={() => handleCandidateAction(cand, "dismissed")}
                              className="p-1.5 rounded-xl hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                              title="Dismiss recommendation"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      </div>

                      {/* Covered Skill Gaps */}
                      {cand.covered_gap_skills.length > 0 && (
                        <div className="flex items-center gap-2 flex-wrap text-xs">
                          <span className="text-[10px] uppercase font-bold text-slate-500">
                            Fills Missing Gaps:
                          </span>
                          {cand.covered_gap_skills.map((s) => (
                            <span
                              key={s}
                              className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            >
                              + {s}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Feature Breakdown Progress Bars */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-white/5 text-[11px]">
                        <div>
                          <div className="flex justify-between text-slate-400 mb-1">
                            <span>Skill Complementarity</span>
                            <span className="text-white font-bold">{cand.skill_complementarity}%</span>
                          </div>
                          <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-indigo-500 h-full rounded-full"
                              style={{ width: `${cand.skill_complementarity}%` }}
                            />
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between text-slate-400 mb-1">
                            <span>Domain Interest</span>
                            <span className="text-white font-bold">{cand.interest_similarity}%</span>
                          </div>
                          <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-cyan-500 h-full rounded-full"
                              style={{ width: `${cand.interest_similarity}%` }}
                            />
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between text-slate-400 mb-1">
                            <span>Availability ({cand.availability_hours}h/wk)</span>
                            <span className="text-white font-bold">{cand.availability_score}%</span>
                          </div>
                          <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-purple-500 h-full rounded-full"
                              style={{ width: `${cand.availability_score}%` }}
                            />
                          </div>
                        </div>

                        <div>
                          <div className="flex justify-between text-slate-400 mb-1">
                            <span>Experience Fit</span>
                            <span className="text-white font-bold">{cand.experience_score}%</span>
                          </div>
                          <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                            <div
                              className="bg-amber-500 h-full rounded-full"
                              style={{ width: `${cand.experience_score}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
