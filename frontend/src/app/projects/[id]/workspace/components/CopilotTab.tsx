"use client";

import { useState, useRef, useEffect } from "react";
import {
  Sparkles,
  Bot,
  Send,
  Zap,
  ArrowRight,
  Plus,
  Target,
  Users,
  CheckCircle2,
  AlertCircle,
  Lightbulb,
} from "lucide-react";
import {
  api,
  Project,
  Task,
  Milestone,
  Team,
  CopilotResponse,
  ActionSuggestion,
} from "@/lib/api";

interface CopilotTabProps {
  project: Project | null;
  tasks: Task[];
  milestones: Milestone[];
  team: Team | null;
  onTaskCreated: (task: Task) => void;
  onOpenTeammateMatch: () => void;
  onOpenAiPlanner: () => void;
}

interface ChatEntry {
  id: string;
  role: "user" | "assistant";
  content: string;
  actions?: ActionSuggestion[];
}

export default function CopilotTab({
  project,
  tasks,
  milestones,
  team,
  onTaskCreated,
  onOpenTeammateMatch,
  onOpenAiPlanner,
}: CopilotTabProps) {
  const [messages, setMessages] = useState<ChatEntry[]>([
    {
      id: "initial-greeting",
      role: "assistant",
      content: `Hello! I am your **${project?.title || "Project"} Copilot**. 
I have real-time visibility into your team's ${tasks.length} Kanban tasks, ${milestones.length} roadmap milestones, and team roster. 

How can I help unblock your team today?`,
      actions: [
        {
          action_type: "advice",
          label: "What should we prioritize next?",
          payload: { query: "What should our team prioritize next based on current Kanban status?" },
        },
        {
          action_type: "advice",
          label: "Analyze project risks & blockers",
          payload: { query: "Analyze our project risks and technical bottlenecks." },
        },
        {
          action_type: "advice",
          label: "Recommend architecture patterns",
          payload: { query: "Recommend modern open-source architecture patterns for our tech stack." },
        },
      ],
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [executingActionId, setExecutingActionId] = useState<string | null>(null);
  const chatBottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || !project) return;

    if (!queryText) setInput("");

    const userMsg: ChatEntry = {
      id: `user-${Date.now()}`,
      role: "user",
      content: textToSend,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res: CopilotResponse = await api.copilotChat(project.id, textToSend, history);

      const assistantMsg: ChatEntry = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: res.answer,
        actions: res.suggested_actions,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err-${Date.now()}`,
          role: "assistant",
          content: "Sorry, I encountered an issue processing that query. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteAction = async (action: ActionSuggestion, actionIdx: number) => {
    if (!project) return;
    const actionKey = `${action.action_type}-${actionIdx}`;
    setExecutingActionId(actionKey);

    try {
      if (action.action_type === "create_task" && action.payload?.title) {
        const newTask = await api.createTask(project.id, {
          title: action.payload.title,
          description: action.detail || "Created via AI Copilot recommendation",
          priority: action.payload.priority || "medium",
          estimated_hours: action.payload.hours || 6,
          status: "todo",
        });
        onTaskCreated(newTask);
        alert(`Task "${action.payload.title}" created and added to Kanban!`);
      } else if (action.action_type === "invite_teammate") {
        onOpenTeammateMatch();
      } else if (action.action_type === "create_milestone") {
        onOpenAiPlanner();
      } else if (action.payload?.query) {
        handleSend(action.payload.query);
      }
    } catch (err: any) {
      alert(err.message || "Failed to execute action");
    } finally {
      setExecutingActionId(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Copilot Context Bar */}
      <div className="p-4 rounded-2xl glass-panel border border-blue-500/20 bg-gradient-to-r from-blue-950/30 to-slate-900/40 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-600/20 text-cyan-300 border border-blue-500/30 flex items-center justify-center shrink-0 shadow-md">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-white text-sm">CollabAI Project Copilot</span>
              <span className="text-[10px] px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                Live Context
              </span>
            </div>
            <p className="text-[11px] text-slate-400">
              Aware of {tasks.length} tasks, {milestones.length} milestones, and {team?.members.length || 1} team members.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onOpenAiPlanner}
            className="px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-300 text-[11px] font-semibold border border-white/10 transition-all flex items-center gap-1"
          >
            <Target className="w-3 h-3 text-cyan-400" /> Plan Milestones
          </button>
          <button
            onClick={onOpenTeammateMatch}
            className="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 text-[11px] font-semibold border border-indigo-500/40 transition-all flex items-center gap-1"
          >
            <Users className="w-3 h-3 text-cyan-300" /> Match Teammates
          </button>
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 min-h-[480px] max-h-[580px] flex flex-col justify-between space-y-4">
        <div className="overflow-y-auto space-y-4 pr-1 flex-1 max-h-[440px]">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex items-start gap-3 ${
                m.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              {m.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-cyan-300 border border-indigo-500/30 flex items-center justify-center shrink-0 mt-1">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-4 text-xs space-y-3 leading-relaxed ${
                  m.role === "user"
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/20"
                    : "glass-panel bg-[#101424] border border-white/10 text-slate-200"
                }`}
              >
                {/* Text Formatting */}
                <div className="whitespace-pre-wrap font-sans text-xs sm:text-[13px] space-y-2">
                  {m.content}
                </div>

                {/* Executable Action Suggestion Chips */}
                {m.actions && m.actions.length > 0 && (
                  <div className="pt-2 border-t border-white/10 space-y-2">
                    <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> Suggested Next Actions
                    </span>

                    <div className="flex flex-wrap gap-2">
                      {m.actions.map((act, idx) => {
                        const isThisExecuting = executingActionId === `${act.action_type}-${idx}`;
                        return (
                          <button
                            key={idx}
                            type="button"
                            disabled={isThisExecuting}
                            onClick={() => handleExecuteAction(act, idx)}
                            className="px-3 py-1.5 rounded-lg bg-indigo-500/15 hover:bg-indigo-500/30 text-indigo-200 border border-indigo-500/30 text-[11px] font-semibold flex items-center gap-1.5 transition-all shadow-sm"
                          >
                            {isThisExecuting ? (
                              <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />
                            ) : (
                              <ArrowRight className="w-3 h-3 text-cyan-400" />
                            )}
                            {act.label}
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-cyan-300 border border-indigo-500/30 flex items-center justify-center shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="glass-panel p-3.5 rounded-2xl bg-[#101424] border border-white/10 text-xs text-slate-400 flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-indigo-500 border-t-cyan-400 rounded-full animate-spin" />
                Copilot is thinking with project context...
              </div>
            </div>
          )}

          <div ref={chatBottomRef} />
        </div>

        {/* Query Input */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 pt-2 border-t border-white/10"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask Copilot about architecture, task delegation, next steps..."
            className="flex-1 bg-black/40 border border-white/10 rounded-xl px-4 py-2.5 text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:opacity-95 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/30 disabled:opacity-40"
          >
            <Send className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Ask</span>
          </button>
        </form>
      </div>
    </div>
  );
}
