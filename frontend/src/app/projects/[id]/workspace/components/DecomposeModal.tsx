"use client";

import { useState } from "react";
import { Zap, X, Check, Clock, AlertTriangle, AlertCircle, Sparkles } from "lucide-react";
import { api, Task, TaskBreakdown, SubTaskItem } from "@/lib/api";

interface DecomposeModalProps {
  task: Task;
  onClose: () => void;
  onApplied: (newTasks: Task[]) => void;
}

export default function DecomposeModal({ task, onClose, onApplied }: DecomposeModalProps) {
  const [loading, setLoading] = useState(false);
  const [breakdown, setBreakdown] = useState<TaskBreakdown | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedSubtasks, setSelectedSubtasks] = useState<SubTaskItem[]>([]);
  const [isApplying, setIsApplying] = useState(false);

  // Trigger initial decomposition on mount if not loaded
  const handleDecompose = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.decomposeTask(task.id);
      setBreakdown(res);
      setSelectedSubtasks(res.subtasks);
    } catch (err: any) {
      setError(err.message || "Failed to decompose task");
    } finally {
      setLoading(false);
    }
  };

  // Run on first load
  useState(() => {
    handleDecompose();
  });

  const toggleSelect = (sub: SubTaskItem) => {
    if (selectedSubtasks.some((s) => s.title === sub.title)) {
      setSelectedSubtasks(selectedSubtasks.filter((s) => s.title !== sub.title));
    } else {
      setSelectedSubtasks([...selectedSubtasks, sub]);
    }
  };

  const handleApply = async () => {
    if (selectedSubtasks.length === 0) return;
    setIsApplying(true);
    try {
      const created = await api.applyDecomposition(task.id, selectedSubtasks, task.milestone_id);
      onApplied(created);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to apply decomposed subtasks");
    } finally {
      setIsApplying(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-2xl glass-panel rounded-2xl border border-indigo-500/30 p-6 space-y-5 bg-[#0b0e1b] shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-cyan-400 flex items-center justify-center border border-indigo-500/30">
              <Zap className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-bold text-white text-sm sm:text-base flex items-center gap-2">
                Smart Task Decomposition
              </h2>
              <p className="text-[11px] text-slate-400 line-clamp-1">
                Parent: <span className="text-white font-medium">{task.title}</span>
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

        {loading && (
          <div className="py-12 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-cyan-400 rounded-full animate-spin" />
            <p className="text-xs text-slate-300 font-medium">Analyzing task architecture and sub-components...</p>
          </div>
        )}

        {error && (
          <div className="p-3.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-200 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {breakdown && !loading && (
          <div className="space-y-4 text-xs">
            {/* Overview & Analysis */}
            <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/5 space-y-1.5">
              <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider block">Architect Analysis</span>
              <p className="text-slate-300 leading-relaxed text-[11px]">{breakdown.analysis}</p>
              <div className="flex items-center gap-3 pt-1 text-[10px] text-slate-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-cyan-400" />
                  Total Estimated: <strong className="text-white">{breakdown.estimated_total_hours}h</strong>
                </span>
                <span>•</span>
                <span>{breakdown.subtasks.length} Subtasks Generated</span>
              </div>
            </div>

            {/* Warnings if any */}
            {breakdown.potential_risks.length > 0 && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-200 space-y-1">
                <span className="text-[10px] font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Architectural Risks
                </span>
                <ul className="list-disc list-inside text-[11px] space-y-0.5 text-slate-300">
                  {breakdown.potential_risks.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Subtasks Selection List */}
            <div className="space-y-2">
              <span className="text-xs font-bold text-white block">
                Select Subtasks to Add to Kanban ({selectedSubtasks.length}/{breakdown.subtasks.length})
              </span>
              <div className="space-y-2">
                {breakdown.subtasks.map((sub, idx) => {
                  const isSelected = selectedSubtasks.some((s) => s.title === sub.title);
                  return (
                    <div
                      key={idx}
                      onClick={() => toggleSelect(sub)}
                      className={`p-3 rounded-xl border transition-all cursor-pointer flex items-start gap-3 ${
                        isSelected
                          ? "bg-indigo-950/40 border-indigo-500/50 text-white"
                          : "bg-white/[0.02] border-white/5 text-slate-400 hover:bg-white/[0.04]"
                      }`}
                    >
                      <div
                        className={`w-4 h-4 rounded mt-0.5 flex items-center justify-center shrink-0 border ${
                          isSelected
                            ? "bg-indigo-600 border-indigo-500 text-white"
                            : "border-white/20 bg-black/40"
                        }`}
                      >
                        {isSelected && <Check className="w-3 h-3" />}
                      </div>

                      <div className="flex-1 space-y-1">
                        <div className="flex items-center justify-between gap-2">
                          <span className="font-semibold text-white text-xs">{sub.title}</span>
                          <div className="flex items-center gap-1.5 shrink-0">
                            <span className="text-[9px] px-1.5 py-0.2 rounded bg-white/10 text-slate-300 uppercase font-bold">
                              {sub.priority}
                            </span>
                            <span className="text-[10px] text-cyan-400 font-semibold flex items-center gap-0.5">
                              <Clock className="w-2.5 h-2.5" /> {sub.estimated_hours}h
                            </span>
                          </div>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-relaxed">{sub.description}</p>
                        <div className="flex flex-wrap items-center gap-1.5 pt-1 text-[9px]">
                          <span className="text-slate-400">Role: <strong className="text-indigo-300">{sub.suggested_role}</strong></span>
                          {sub.required_skills?.map((sk, i) => (
                            <span key={i} className="px-1.5 py-0.2 rounded bg-indigo-500/15 text-indigo-300">
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="pt-3 border-t border-white/10 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 font-semibold text-xs"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleApply}
                disabled={isApplying || selectedSubtasks.length === 0}
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:opacity-95 text-white font-bold text-xs shadow-md shadow-indigo-600/30 flex items-center gap-1.5 disabled:opacity-50"
              >
                {isApplying ? (
                  <>
                    <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Adding to Board...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5 text-cyan-200" />
                    Add {selectedSubtasks.length} Subtasks to Kanban
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
