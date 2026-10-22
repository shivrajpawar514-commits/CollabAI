"use client";

import { useState } from "react";
import { Target, X, Check, Clock, Sparkles, AlertCircle, ArrowRight, Layers } from "lucide-react";
import { api, Milestone, MilestoneDecomposition, MilestoneItem } from "@/lib/api";

interface AiPlannerModalProps {
  projectId: string;
  projectTitle: string;
  onClose: () => void;
  onApplied: () => void;
}

export default function AiPlannerModal({
  projectId,
  projectTitle,
  onClose,
  onApplied,
}: AiPlannerModalProps) {
  const [timelineWeeks, setTimelineWeeks] = useState(8);
  const [loading, setLoading] = useState(false);
  const [roadmap, setRoadmap] = useState<MilestoneDecomposition | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isApplying, setIsApplying] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.planMilestones(projectId, timelineWeeks);
      setRoadmap(res);
    } catch (err: any) {
      setError(err.message || "Failed to generate milestones");
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async () => {
    if (!roadmap || roadmap.milestones.length === 0) return;
    setIsApplying(true);
    try {
      await api.applyMilestones(projectId, roadmap.milestones);
      onApplied();
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to apply milestones to project");
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-3xl glass-panel rounded-2xl border border-indigo-500/30 p-6 space-y-5 bg-[#0b0e1b] shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
              <Target className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-bold text-white text-sm sm:text-base flex items-center gap-2">
                AI Milestone & Roadmap Planner
              </h2>
              <p className="text-[11px] text-slate-400 line-clamp-1">
                Project: <span className="text-white font-medium">{projectTitle}</span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Configuration Bar */}
        <div className="p-4 rounded-xl bg-white/[0.03] border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="space-y-1">
            <span className="font-semibold text-white block">Project Target Duration</span>
            <p className="text-slate-400 text-[11px]">
              The planner will organize deliverables into sequential hackathon or capstone phases.
            </p>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {[4, 6, 8, 12].map((weeks) => (
              <button
                key={weeks}
                type="button"
                onClick={() => setTimelineWeeks(weeks)}
                className={`px-3 py-1.5 rounded-lg font-bold text-xs transition-all ${
                  timelineWeeks === weeks
                    ? "bg-cyan-500 text-black shadow-md shadow-cyan-500/25"
                    : "bg-white/5 text-slate-400 hover:text-white"
                }`}
              >
                {weeks}w
              </button>
            ))}

            <button
              type="button"
              onClick={handleGenerate}
              disabled={loading}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 flex items-center gap-1.5 transition-all"
            >
              {loading ? (
                <>
                  <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Planning...
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-cyan-300" />
                  Generate Roadmap
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-200 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Generated Roadmap Display */}
        {roadmap && !loading && (
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-white">Generated Phases ({roadmap.milestones.length})</span>
              <span className="text-[11px] text-cyan-400 font-semibold">{roadmap.total_weeks} Weeks Planned</span>
            </div>

            <div className="space-y-3">
              {roadmap.milestones.map((m, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-2.5 hover:border-cyan-500/30 transition-all"
                >
                  <div className="flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-extrabold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 uppercase">
                        Week {m.target_week}
                      </span>
                      <h4 className="font-bold text-white text-xs sm:text-sm">{m.title}</h4>
                    </div>
                    <span className="text-[10px] text-slate-400">
                      {m.suggested_tasks?.length || 0} suggested tasks
                    </span>
                  </div>

                  <p className="text-[11px] text-slate-300 leading-relaxed">{m.description}</p>

                  {/* Deliverables tags */}
                  {m.deliverables?.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {m.deliverables.map((deliv, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded-md bg-white/[0.04] border border-white/5 text-slate-300 text-[10px] flex items-center gap-1"
                        >
                          <Check className="w-2.5 h-2.5 text-cyan-400" />
                          {deliv}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Suggested initial tasks preview */}
                  {m.suggested_tasks?.length > 0 && (
                    <div className="pt-2 border-t border-white/5 space-y-1">
                      <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
                        Included Tasks:
                      </span>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                        {m.suggested_tasks.map((st, i) => (
                          <div key={i} className="p-2 rounded bg-black/40 border border-white/5 text-[10px] space-y-0.5">
                            <span className="font-semibold text-slate-200 block truncate">{st.title}</span>
                            <div className="flex items-center justify-between text-[9px] text-slate-400">
                              <span className="text-cyan-400 font-medium">{st.estimated_hours}h</span>
                              <span className="uppercase text-slate-500 font-bold">{st.priority}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="pt-3 border-t border-white/10 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 font-semibold text-xs"
              >
                Dismiss
              </button>
              <button
                type="button"
                onClick={handleApply}
                disabled={isApplying}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 via-indigo-600 to-purple-600 hover:opacity-95 text-white font-bold text-xs shadow-md shadow-indigo-600/30 flex items-center gap-1.5"
              >
                {isApplying ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Committing to Roadmap...
                  </>
                ) : (
                  <>
                    <Layers className="w-3.5 h-3.5 text-cyan-200" />
                    Apply {roadmap.milestones.length} Milestones & Tasks to Project
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
