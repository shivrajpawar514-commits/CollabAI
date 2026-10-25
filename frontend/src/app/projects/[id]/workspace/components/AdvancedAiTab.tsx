"use client";

import { useState, useEffect } from "react";
import {
  Bot,
  Mic,
  BrainCircuit,
  Cpu,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Clock,
  Sparkles,
  ArrowRight,
  ChevronRight,
  ListPlus,
  Play,
  RotateCcw,
  FileCode,
  Shield,
  Layers,
  Search,
  Plus,
  Tag,
  Users,
  Award,
  Check,
  Copy,
  Loader2,
  Calendar,
  AlertTriangle,
  FolderGit2,
  Lightbulb,
} from "lucide-react";
import {
  api,
  MeetingNoteItem,
  MeetingActionItem,
  ProjectDecisionItem,
  DecisionQueryResponse,
  OrchestratorResponse,
  CodeReviewResponse,
  GeneratedTestsResult,
  ProjectReadinessReport,
  Milestone,
} from "@/lib/api";

interface AdvancedAiTabProps {
  projectId: string;
  projectTitle: string;
  milestones: Milestone[];
  onTasksUpdated?: () => void;
}

const SAMPLE_TRANSCRIPTS = [
  {
    title: "Sprint Planning: DB Architecture & RAG Pipeline",
    text: `Alex: Alright team, let's align on our vector database strategy. We tested Pinecone and PostgreSQL with pgvector.
Maya: pgvector is running locally in Docker with zero extra cloud fees, and it handles our chunk size of 800 tokens with cosine similarity perfectly under 40 milliseconds.
Sam: I agree. Let's officially commit to PostgreSQL with pgvector for all semantic search and knowledge vault storage.
Alex: Agreed. Action items: Maya, please finish the Alembic migration and indexing for chunk embeddings by Thursday.
Sam: I will implement the streaming API endpoint for the RAG responses using Server-Sent Events.
Maya: I also estimate the pgvector migration will take about 6 hours.
Sam: Streaming endpoint will take 4 hours. Priority is high because the frontend demo is next Monday.`,
  },
  {
    title: "Security & Auth Review Standup",
    text: `David: Team, let's review the security audit findings for our authentication flow.
Elena: Right now our JWT tokens don't rotate refresh tokens on each session issuance, which leaves a window for token hijacking.
David: We should enforce SHA-256 password hashing with bcrypt, set access token expiration to 15 minutes, and rotate refresh tokens stored as HttpOnly cookies.
Elena: Decision made: Implement strict refresh token rotation with HttpOnly SameSite=Lax cookie storage. Rejected localStorage storage due to XSS vulnerability risks.
David: Elena, please write the test suite for token revocation and expired session cleanup. Estimate: 5 hours, priority urgent.
David: I will update the FastAPI security dependency to validate audience and issuer claims. Estimate: 3 hours, priority high.`,
  },
];

const SAMPLE_CODE_SNIPPETS = {
  python: `async def get_user_profile(user_id: str, db: AsyncSession):
    # Potential SQL injection vulnerability if unparameterized
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    result = await db.execute(text(query))
    user = result.fetchone()
    if not user:
        return None
    return {"id": user[0], "email": user[1], "is_active": user[2]}`,
  typescript: `export async function fetchProjectTasks(projectId: string) {
  const res = await fetch(\`/api/v1/projects/\${projectId}/tasks\`);
  if (!res.ok) {
    throw new Error("Failed to fetch");
  }
  const data = await res.json();
  return data.map((t: any) => ({ ...t, formattedDate: new Date(t.created_at) }));
}`,
};

export default function AdvancedAiTab({
  projectId,
  projectTitle,
  milestones,
  onTasksUpdated,
}: AdvancedAiTabProps) {
  const [activeSection, setActiveSection] = useState<
    "meetings" | "decisions" | "orchestrator" | "code_audit"
  >("meetings");

  // --- Sub-Tab 1: Meetings State ---
  const [meetings, setMeetings] = useState<MeetingNoteItem[]>([]);
  const [loadingMeetings, setLoadingMeetings] = useState(false);
  const [transcriptText, setTranscriptText] = useState("");
  const [meetingTitleInput, setMeetingTitleInput] = useState("");
  const [analyzingMeeting, setAnalyzingMeeting] = useState(false);
  const [selectedActionItemIds, setSelectedActionItemIds] = useState<string[]>([]);
  const [targetMilestoneId, setTargetMilestoneId] = useState<string>("");
  const [convertingActions, setConvertingActions] = useState(false);
  const [conversionSuccessMsg, setConversionSuccessMsg] = useState<string | null>(null);

  // --- Sub-Tab 2: Decisions State ---
  const [decisions, setDecisions] = useState<ProjectDecisionItem[]>([]);
  const [loadingDecisions, setLoadingDecisions] = useState(false);
  const [decisionQuery, setDecisionQuery] = useState("");
  const [queryingMemory, setQueryingMemory] = useState(false);
  const [memoryAnswer, setMemoryAnswer] = useState<DecisionQueryResponse | null>(null);
  const [showAddDecision, setShowAddDecision] = useState(false);
  const [newDecisionWhat, setNewDecisionWhat] = useState("");
  const [newDecisionWhy, setNewDecisionWhy] = useState("");
  const [newDecisionWho, setNewDecisionWho] = useState("Team Consensus");
  const [newDecisionAlternatives, setNewDecisionAlternatives] = useState("");
  const [newDecisionTags, setNewDecisionTags] = useState("");
  const [savingDecision, setSavingDecision] = useState(false);

  // --- Sub-Tab 3: Orchestrator State ---
  const [orchestratorQuery, setOrchestratorQuery] = useState(
    "Synthesize our milestone velocity, blocked tasks, and architecture readiness for the upcoming demo."
  );
  const [orchestrating, setOrchestrating] = useState(false);
  const [orchestratorResult, setOrchestratorResult] = useState<OrchestratorResponse | null>(null);

  // --- Sub-Tab 4: Code Assistant & Audit State ---
  const [auditReport, setAuditReport] = useState<ProjectReadinessReport | null>(null);
  const [loadingAudit, setLoadingAudit] = useState(false);
  const [codeSnippet, setCodeSnippet] = useState(SAMPLE_CODE_SNIPPETS.python);
  const [codeLanguage, setCodeLanguage] = useState("python");
  const [testFramework, setTestFramework] = useState("pytest");
  const [reviewResult, setReviewResult] = useState<CodeReviewResponse | null>(null);
  const [generatedTests, setGeneratedTests] = useState<GeneratedTestsResult | null>(null);
  const [reviewingCode, setReviewingCode] = useState(false);
  const [generatingTests, setGeneratingTests] = useState(false);
  const [copiedCode, setCopiedCode] = useState(false);

  // Load initial data
  useEffect(() => {
    loadMeetings();
    loadDecisions();
  }, [projectId]);

  const loadMeetings = async () => {
    setLoadingMeetings(true);
    try {
      const data = await api.getProjectMeetings(projectId);
      setMeetings(data);
    } catch (err) {
      console.error("Failed to load meetings", err);
    } finally {
      setLoadingMeetings(false);
    }
  };

  const loadDecisions = async () => {
    setLoadingDecisions(true);
    try {
      const data = await api.getProjectDecisions(projectId);
      setDecisions(data);
    } catch (err) {
      console.error("Failed to load decisions", err);
    } finally {
      setLoadingDecisions(false);
    }
  };

  // 1. Analyze Meeting
  const handleAnalyzeMeeting = async () => {
    if (!transcriptText.trim()) return;
    setAnalyzingMeeting(true);
    setConversionSuccessMsg(null);
    try {
      const result = await api.analyzeMeeting(
        projectId,
        transcriptText,
        meetingTitleInput.trim() || undefined
      );
      setMeetings((prev) => [result, ...prev]);
      // Auto-select pending action items
      const pendingIds = result.action_items.filter((item) => !item.is_converted).map((i) => i.id);
      setSelectedActionItemIds(pendingIds);
      setTranscriptText("");
      setMeetingTitleInput("");
      // Refresh decisions as well since decisions are extracted automatically
      loadDecisions();
    } catch (err) {
      console.error("Meeting analysis failed", err);
    } finally {
      setAnalyzingMeeting(false);
    }
  };

  // Convert Action Items to Tasks
  const handleConvertActionItems = async (itemIdsToConvert?: string[]) => {
    const ids = itemIdsToConvert || selectedActionItemIds;
    if (ids.length === 0) return;
    setConvertingActions(true);
    setConversionSuccessMsg(null);
    try {
      const res = await api.convertMeetingActionItems(
        projectId,
        ids,
        targetMilestoneId || undefined
      );
      setConversionSuccessMsg(`Successfully converted ${res.converted_count} action items into Kanban tasks!`);
      // Refresh meetings list to show updated converted status
      await loadMeetings();
      setSelectedActionItemIds([]);
      if (onTasksUpdated) {
        onTasksUpdated();
      }
    } catch (err) {
      console.error("Conversion failed", err);
    } finally {
      setConvertingActions(false);
    }
  };

  // 2. Query Decision Memory
  const handleQueryMemory = async () => {
    if (!decisionQuery.trim()) return;
    setQueryingMemory(true);
    try {
      const res = await api.queryDecisionMemory(projectId, decisionQuery);
      setMemoryAnswer(res);
    } catch (err) {
      console.error("Decision query failed", err);
    } finally {
      setQueryingMemory(false);
    }
  };

  // Save new decision
  const handleSaveDecision = async () => {
    if (!newDecisionWhat.trim() || !newDecisionWhy.trim()) return;
    setSavingDecision(true);
    try {
      const alts = newDecisionAlternatives
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const tags = newDecisionTags
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);

      const saved = await api.createDecision(projectId, {
        what: newDecisionWhat,
        why: newDecisionWhy,
        who: newDecisionWho || "Team Consensus",
        alternatives: alts,
        tags: tags,
      });
      setDecisions((prev) => [saved, ...prev]);
      setShowAddDecision(false);
      setNewDecisionWhat("");
      setNewDecisionWhy("");
      setNewDecisionAlternatives("");
      setNewDecisionTags("");
    } catch (err) {
      console.error("Failed to save decision", err);
    } finally {
      setSavingDecision(false);
    }
  };

  // 3. Multi-Agent Orchestrator
  const handleRunOrchestrator = async () => {
    if (!orchestratorQuery.trim()) return;
    setOrchestrating(true);
    try {
      const res = await api.runMultiAgentOrchestrator(projectId, orchestratorQuery);
      setOrchestratorResult(res);
    } catch (err) {
      console.error("Orchestrator failed", err);
    } finally {
      setOrchestrating(false);
    }
  };

  // 4. Code Assistant & Readiness Audit
  const handleRunAudit = async () => {
    setLoadingAudit(true);
    try {
      const rep = await api.auditProjectReadiness(projectId);
      setAuditReport(rep);
    } catch (err) {
      console.error("Audit failed", err);
    } finally {
      setLoadingAudit(false);
    }
  };

  const handleReviewCode = async () => {
    if (!codeSnippet.trim()) return;
    setReviewingCode(true);
    setReviewResult(null);
    try {
      const rep = await api.reviewCode(
        projectId,
        codeSnippet,
        codeLanguage === "python" ? "main.py" : "index.ts",
        codeLanguage
      );
      setReviewResult(rep);
    } catch (err) {
      console.error("Review failed", err);
    } finally {
      setReviewingCode(false);
    }
  };

  const handleGenerateTests = async () => {
    if (!codeSnippet.trim()) return;
    setGeneratingTests(true);
    setGeneratedTests(null);
    try {
      const rep = await api.generateTests(
        projectId,
        codeSnippet,
        codeLanguage === "python" ? "main.py" : "index.ts",
        testFramework
      );
      setGeneratedTests(rep);
    } catch (err) {
      console.error("Test generation failed", err);
    } finally {
      setGeneratingTests(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Hero */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-blue-950/30 via-slate-900/40 to-slate-900/40 border border-blue-500/20 p-6 shadow-xl">
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-1.5 rounded-lg bg-blue-500/20 text-blue-300 border border-blue-500/30">
                <Bot className="w-5 h-5 text-blue-400" />
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Autonomous AI Lab & Decision Memory
              </h2>
            </div>
            <p className="text-xs text-slate-300 max-w-2xl leading-relaxed">
              Voice-to-Task meeting breakdown, architectural decision graph (ADRs), LangGraph-style
              multi-agent orchestration, and 4-pillar project readiness auditing.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setActiveSection("code_audit");
                handleRunAudit();
              }}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-900/30 transition-all border border-blue-400/40"
            >
              <Award className="w-4 h-4 text-blue-200" />
              Run Readiness Audit
            </button>
          </div>
        </div>

        {/* Sub-tab Navigation */}
        <div className="flex flex-wrap items-center gap-2 mt-6 pt-4 border-t border-white/10">
          {[
            { id: "meetings", label: "Voice & Meeting Assistant", icon: Mic },
            { id: "decisions", label: "Project Memory & Decision Graph", icon: BrainCircuit },
            { id: "orchestrator", label: "Multi-Agent Orchestrator", icon: Cpu },
            { id: "code_audit", label: "Code Review & Readiness", icon: ShieldCheck },
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeSection === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveSection(tab.id as any)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-md shadow-blue-900/30 border border-blue-400/50"
                    : "bg-white/[0.04] text-slate-400 hover:text-white hover:bg-white/[0.08] border border-white/[0.05]"
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* SECTION 1: VOICE & MEETING ASSISTANT */}
      {activeSection === "meetings" && (
        <div className="space-y-6">
          {/* Transcript Ingestion Panel */}
          <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-4 bg-[#0d111f]/70">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Mic className="w-4 h-4 text-blue-400" /> Ingest Meeting / Voice Transcript
                </h3>
                <p className="text-xs text-slate-400">
                  Drop in raw meeting notes, Whisper audio transcripts, or standup updates. CollabAI extracts
                  executive summaries, architectural decisions, and converts action items into real Kanban tasks.
                </p>
              </div>

              {/* Sample Templates */}
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-slate-400">Quick Samples:</span>
                {SAMPLE_TRANSCRIPTS.map((sample, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setMeetingTitleInput(sample.title);
                      setTranscriptText(sample.text);
                    }}
                    className="px-2.5 py-1 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] text-[11px] text-blue-300 border border-blue-500/20 transition-all"
                  >
                    {idx === 0 ? "DB Architecture" : "Auth Standup"}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <input
                type="text"
                placeholder="Meeting Title (e.g. Sprint 2 Architectural Alignment)"
                value={meetingTitleInput}
                onChange={(e) => setMeetingTitleInput(e.target.value)}
                className="col-span-1 md:col-span-2 px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
              />
              <button
                onClick={handleAnalyzeMeeting}
                disabled={analyzingMeeting || !transcriptText.trim()}
                className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center justify-center gap-2"
              >
                {analyzingMeeting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Analyzing Transcript...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-blue-200" /> Analyze & Extract Actions
                  </>
                )}
              </button>
            </div>

            <textarea
              rows={5}
              placeholder="Paste raw meeting transcript, notes, or spoken conversation..."
              value={transcriptText}
              onChange={(e) => setTranscriptText(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500 placeholder-slate-500 leading-relaxed font-mono"
            />
          </div>

          {/* Success Banner */}
          {conversionSuccessMsg && (
            <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              <span>{conversionSuccessMsg}</span>
            </div>
          )}

          {/* Action Items Conversion Bar (if items selected) */}
          {selectedActionItemIds.length > 0 && (
            <div className="p-4 rounded-xl bg-blue-950/40 border border-blue-500/30 flex flex-col md:flex-row items-center justify-between gap-3 animate-in fade-in duration-200">
              <div className="flex items-center gap-2">
                <span className="w-6 h-6 rounded-md bg-blue-500/20 text-blue-200 flex items-center justify-center text-xs font-bold">
                  {selectedActionItemIds.length}
                </span>
                <span className="text-xs text-white font-medium">
                  action items selected for Kanban task creation
                </span>
              </div>

              <div className="flex items-center gap-2 w-full md:w-auto">
                <select
                  value={targetMilestoneId}
                  onChange={(e) => setTargetMilestoneId(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-black/50 border border-white/10 text-slate-200 text-xs focus:outline-none"
                >
                  <option value="">No Milestone (Backlog)</option>
                  {milestones.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.title}
                    </option>
                  ))}
                </select>

                <button
                  onClick={() => handleConvertActionItems()}
                  disabled={convertingActions}
                  className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center gap-1.5 whitespace-nowrap"
                >
                  {convertingActions ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <ListPlus className="w-3.5 h-3.5" />
                  )}
                  Convert to Tasks
                </button>
              </div>
            </div>
          )}

          {/* Meetings List */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider flex items-center gap-2">
              <Calendar className="w-3.5 h-3.5 text-blue-400" /> Past Meetings & Action Items ({meetings.length})
            </h4>

            {loadingMeetings ? (
              <div className="text-center py-12 text-slate-400">
                <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-400" />
                <p className="text-xs">Loading meeting records...</p>
              </div>
            ) : meetings.length === 0 ? (
              <div className="glass-panel p-8 rounded-2xl border border-white/5 text-center text-slate-400">
                <Mic className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <p className="text-xs">No meetings analyzed yet. Ingest a transcript above to get started!</p>
              </div>
            ) : (
              meetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className="glass-panel p-5 rounded-2xl border border-white/10 bg-[#0d111f]/60 space-y-4"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-white/5 pb-3">
                    <div>
                      <h4 className="text-sm font-bold text-white flex items-center gap-2">
                        {meeting.title}
                        <span className="text-[10px] px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30 font-medium">
                          {meeting.overall_sentiment}
                        </span>
                      </h4>
                      <p className="text-[11px] text-slate-400">
                        {new Date(meeting.created_at).toLocaleDateString(undefined, {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>

                    <div className="flex flex-wrap gap-1.5">
                      {meeting.key_topics_json?.map((topic, i) => (
                        <span
                          key={i}
                          className="px-2 py-0.5 rounded-md bg-white/[0.04] text-[10px] text-slate-300 border border-white/10"
                        >
                          #{topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Summary */}
                  <div className="p-3.5 rounded-xl bg-black/30 border border-white/5 text-xs text-slate-300 leading-relaxed">
                    <span className="font-semibold text-blue-300 block mb-1">Executive Summary:</span>
                    {meeting.executive_summary}
                  </div>

                  {/* Action items */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-xs text-slate-400 font-semibold">
                      <span>Extracted Action Items ({meeting.action_items.length}):</span>
                    </div>

                    <div className="grid grid-cols-1 gap-2">
                      {meeting.action_items.map((item) => {
                        const isConverted = item.is_converted;
                        const isSelected = selectedActionItemIds.includes(item.id);

                        return (
                          <div
                            key={item.id}
                            className={`p-3 rounded-xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-3 ${
                              isConverted
                                ? "bg-emerald-950/20 border-emerald-500/20 opacity-80"
                                : isSelected
                                ? "bg-blue-900/20 border-blue-500/40"
                                : "bg-white/[0.02] border-white/5 hover:border-white/10"
                            }`}
                          >
                            <div className="flex items-start gap-3">
                              {!isConverted ? (
                                <input
                                  type="checkbox"
                                  checked={isSelected}
                                  onChange={(e) => {
                                    if (e.target.checked) {
                                      setSelectedActionItemIds((prev) => [...prev, item.id]);
                                    } else {
                                      setSelectedActionItemIds((prev) =>
                                        prev.filter((id) => id !== item.id)
                                      );
                                    }
                                  }}
                                  className="mt-1 rounded accent-blue-600 cursor-pointer"
                                />
                              ) : (
                                <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                              )}

                              <div>
                                <h5
                                  className={`text-xs font-semibold ${
                                    isConverted ? "text-slate-300 line-through" : "text-white"
                                  }`}
                                >
                                  {item.title}
                                </h5>
                                <p className="text-[11px] text-slate-400 mt-0.5">{item.description}</p>
                              </div>
                            </div>

                            <div className="flex items-center gap-2 shrink-0">
                              <span className="text-[10px] px-2 py-0.5 rounded bg-white/[0.04] text-slate-400 border border-white/5">
                                {item.suggested_assignee || "Unassigned"}
                              </span>
                              <span
                                className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded border ${
                                  item.priority === "urgent"
                                    ? "bg-red-500/20 text-red-300 border-red-500/30"
                                    : item.priority === "high"
                                    ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                                    : "bg-indigo-500/20 text-indigo-300 border-indigo-500/30"
                                }`}
                              >
                                {item.priority}
                              </span>
                              <span className="text-[10px] text-slate-400 flex items-center gap-1">
                                <Clock className="w-3 h-3" /> {item.estimated_hours}h
                              </span>

                              {isConverted ? (
                                <span className="text-[10px] px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 font-semibold border border-emerald-500/30">
                                  Task Created
                                </span>
                              ) : (
                                <button
                                  onClick={() => handleConvertActionItems([item.id])}
                                  className="px-2.5 py-1 rounded bg-blue-600/30 hover:bg-blue-600/50 text-[10px] font-bold text-blue-200 border border-blue-500/40 transition-all"
                                >
                                  Convert
                                </button>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* SECTION 2: PROJECT MEMORY & DECISION GRAPH */}
      {activeSection === "decisions" && (
        <div className="space-y-6">
          {/* Query Bar */}
          <div className="glass-panel p-5 rounded-2xl border border-white/10 space-y-4 bg-[#0d111f]/70">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <BrainCircuit className="w-4 h-4 text-blue-400" /> Architectural Decision Knowledge Graph
              </h3>
              <p className="text-xs text-slate-400">
                Ask questions about past architectural trade-offs, technology choices, and design rationale.
                The system executes semantic retrieval over all recorded ADRs.
              </p>
            </div>

            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="text"
                  placeholder="e.g. 'Why did we choose PostgreSQL over MongoDB?' or 'What was the rationale for Next.js?'"
                  value={decisionQuery}
                  onChange={(e) => setDecisionQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleQueryMemory()}
                  className="w-full pl-10 pr-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>
              <button
                onClick={handleQueryMemory}
                disabled={queryingMemory || !decisionQuery.trim()}
                className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center gap-2"
              >
                {queryingMemory ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                Query Memory
              </button>
              <button
                onClick={() => setShowAddDecision(!showAddDecision)}
                className="px-3.5 py-2.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-white text-xs font-semibold transition-all flex items-center gap-1.5"
              >
                <Plus className="w-4 h-4 text-blue-300" /> Record ADR
              </button>
            </div>

            {/* Answer Display */}
            {memoryAnswer && (
              <div className="p-4 rounded-xl bg-gradient-to-br from-blue-950/30 to-slate-900/30 border border-blue-500/20 space-y-3 animate-in fade-in duration-200">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-blue-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-blue-400" /> Synthesized Rationale
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-300 border border-blue-500/30">
                    Confidence: {(memoryAnswer.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed font-sans">{memoryAnswer.answer}</p>

                {memoryAnswer.matched_decisions?.length > 0 && (
                  <div className="pt-2 border-t border-white/5 space-y-1.5">
                    <span className="text-[10px] text-slate-400 font-semibold block">Grounding Records:</span>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {memoryAnswer.matched_decisions.map((d, i) => (
                        <div
                          key={i}
                          className="p-2.5 rounded-lg bg-black/40 border border-white/5 text-[11px] space-y-1"
                        >
                          <div className="font-semibold text-white truncate">{d.what}</div>
                          <div className="text-slate-400 line-clamp-2">{d.why}</div>
                          <div className="text-[10px] text-blue-300">
                            By {d.who} • {d.when}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Record New ADR Modal / Panel */}
          {showAddDecision && (
            <div className="glass-panel p-5 rounded-2xl border border-blue-500/30 space-y-4 bg-[#0e1222] animate-in fade-in duration-200">
              <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Plus className="w-3.5 h-3.5 text-blue-400" /> Record Architectural Decision Record (ADR)
              </h4>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-[11px] text-slate-400 font-medium">What was decided? *</label>
                  <input
                    type="text"
                    placeholder="e.g. Use pgvector on PostgreSQL for vector embeddings"
                    value={newDecisionWhat}
                    onChange={(e) => setNewDecisionWhat(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[11px] text-slate-400 font-medium">Who made/approved the decision?</label>
                  <input
                    type="text"
                    placeholder="e.g. Architecture Team / Lead"
                    value={newDecisionWho}
                    onChange={(e) => setNewDecisionWho(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] text-slate-400 font-medium">Why? Rationale & Trade-offs *</label>
                <textarea
                  rows={3}
                  placeholder="Explain the advantages, performance characteristics, and why other options were discarded..."
                  value={newDecisionWhy}
                  onChange={(e) => setNewDecisionWhy(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-[11px] text-slate-400 font-medium">Alternatives Considered (comma-separated)</label>
                  <input
                    type="text"
                    placeholder="Pinecone, Qdrant, ChromaDB"
                    value={newDecisionAlternatives}
                    onChange={(e) => setNewDecisionAlternatives(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-[11px] text-slate-400 font-medium">Tags (comma-separated)</label>
                  <input
                    type="text"
                    placeholder="postgres, database, vector, scalability"
                    value={newDecisionTags}
                    onChange={(e) => setNewDecisionTags(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-2">
                <button
                  onClick={() => setShowAddDecision(false)}
                  className="px-3.5 py-1.5 rounded-xl bg-white/[0.05] text-slate-300 text-xs font-semibold hover:bg-white/[0.1]"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveDecision}
                  disabled={savingDecision || !newDecisionWhat.trim() || !newDecisionWhy.trim()}
                  className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center gap-1.5"
                >
                  {savingDecision ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Check className="w-3.5 h-3.5" />}
                  Save to Knowledge Graph
                </button>
              </div>
            </div>
          )}

          {/* Historical Decisions Grid */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase text-slate-400 tracking-wider flex items-center gap-2">
              <FolderGit2 className="w-3.5 h-3.5 text-blue-400" /> Recorded Architectural Decisions ({decisions.length})
            </h4>

            {loadingDecisions ? (
              <div className="text-center py-10 text-slate-400">
                <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-400" />
                <p className="text-xs">Loading decision graph...</p>
              </div>
            ) : decisions.length === 0 ? (
              <div className="glass-panel p-8 rounded-2xl border border-white/5 text-center text-slate-400">
                <BrainCircuit className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <p className="text-xs">No ADRs recorded yet. Record your first decision above or analyze a meeting!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {decisions.map((dec) => (
                  <div
                    key={dec.id}
                    className="glass-panel p-4 rounded-xl border border-white/10 bg-[#0d111f]/60 space-y-3 hover:border-blue-500/30 transition-all"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h5 className="text-xs font-bold text-white leading-snug">{dec.what}</h5>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-medium shrink-0">
                        {dec.who}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-black/20 p-2.5 rounded-lg border border-white/5">
                      <strong className="text-blue-300 font-semibold block mb-0.5 text-[11px]">Rationale:</strong>
                      {dec.why}
                    </p>

                    {dec.alternatives_json && dec.alternatives_json.length > 0 && (
                      <div className="text-[11px] text-slate-400">
                        <span className="text-slate-500">Rejected Alternatives:</span>{" "}
                        {dec.alternatives_json.join(", ")}
                      </div>
                    )}

                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      {dec.tags_json?.map((tag, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 rounded bg-white/[0.04] text-[10px] text-slate-400 border border-white/5 flex items-center gap-1"
                        >
                          <Tag className="w-2.5 h-2.5 text-blue-400" /> {tag}
                        </span>
                      ))}
                      <span className="text-[10px] text-slate-500 ml-auto">
                        {new Date(dec.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* SECTION 3: MULTI-AGENT ORCHESTRATOR */}
      {activeSection === "orchestrator" && (
        <div className="space-y-6">
          {/* Agent Architecture Overview */}
          <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-[#0d111f]/70 space-y-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Cpu className="w-4 h-4 text-blue-400" /> Autonomous Multi-Agent Orchestration State Machine
              </h3>
              <p className="text-xs text-slate-400">
                Dispatches three autonomous specialized agents across project telemetry, synthesized by an
                Executive Supervisor into an actionable decision memo.
              </p>
            </div>

            {/* Visual Agent Mesh */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
              <div className="p-3.5 rounded-xl bg-blue-950/30 border border-blue-500/20 space-y-1.5">
                <div className="flex items-center gap-2 text-blue-300 font-semibold text-xs">
                  <Calendar className="w-4 h-4 text-blue-400" /> Planner Agent
                </div>
                <p className="text-[11px] text-slate-400">
                  Monitors roadmap velocity, milestone sequencing, and delivery feasibility.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-blue-950/30 border border-blue-500/20 space-y-1.5">
                <div className="flex items-center gap-2 text-blue-300 font-semibold text-xs">
                  <BrainCircuit className="w-4 h-4 text-blue-400" /> Research Agent
                </div>
                <p className="text-[11px] text-slate-400">
                  Reviews architectural design patterns, RAG document vault, and technical trade-offs.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-amber-950/30 border border-amber-500/20 space-y-1.5">
                <div className="flex items-center gap-2 text-amber-300 font-semibold text-xs">
                  <Layers className="w-4 h-4 text-amber-400" /> Task / Execution Agent
                </div>
                <p className="text-[11px] text-slate-400">
                  Audits active Kanban tasks, blocked dependencies, and sprint throughput.
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/20 space-y-1.5">
                <div className="flex items-center gap-2 text-emerald-300 font-semibold text-xs">
                  <Sparkles className="w-4 h-4 text-emerald-400" /> Lead Supervisor
                </div>
                <p className="text-[11px] text-slate-400">
                  Synthesizes agent insights into an executive decision memo with next actions.
                </p>
              </div>
            </div>

            {/* Orchestrator Prompt Input */}
            <div className="space-y-2 pt-2">
              <div className="flex items-center justify-between">
                <label className="text-[11px] text-slate-300 font-semibold">Orchestration Directive / Objective:</label>
                <div className="flex gap-2">
                  {[
                    "Sprint Bottlenecks",
                    "Demo Readiness",
                    "Architecture Trade-offs",
                  ].map((preset, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        if (idx === 0) setOrchestratorQuery("Identify critical bottlenecks, overdue tasks, and milestone sequencing risks for our current sprint.");
                        if (idx === 1) setOrchestratorQuery("Synthesize our milestone velocity, blocked tasks, and architecture readiness for the upcoming demo.");
                        if (idx === 2) setOrchestratorQuery("Analyze technical debt, missing documentation, and architectural decisions made so far.");
                      }}
                      className="px-2 py-0.5 rounded bg-white/[0.04] hover:bg-white/[0.08] text-[10px] text-slate-300 border border-white/5"
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={orchestratorQuery}
                  onChange={(e) => setOrchestratorQuery(e.target.value)}
                  className="flex-1 px-3.5 py-2.5 rounded-xl bg-black/40 border border-white/10 text-white text-xs focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={handleRunOrchestrator}
                  disabled={orchestrating || !orchestratorQuery.trim()}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center gap-2 whitespace-nowrap"
                >
                  {orchestrating ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" /> Orchestrating Agents...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-white" /> Run Orchestrator
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Orchestrator Results */}
          {orchestratorResult && (
            <div className="space-y-4 animate-in fade-in duration-300">
              {/* Executive Synthesis Card */}
              <div className="glass-panel p-5 rounded-2xl border border-blue-500/30 bg-gradient-to-br from-blue-950/20 to-[#0a0c1a] space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-blue-300 uppercase tracking-wider flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-blue-400" /> Executive Supervisor Synthesis
                  </h4>
                  <span className="text-[10px] px-2.5 py-0.5 rounded-md bg-blue-500/20 text-blue-200 border border-blue-500/30 font-medium">
                    {orchestratorResult.participating_agents.length} Agents Synchronized
                  </span>
                </div>
                <div className="text-xs text-slate-200 leading-relaxed whitespace-pre-line font-sans p-4 rounded-xl bg-black/40 border border-white/5">
                  {orchestratorResult.executive_synthesis}
                </div>
              </div>

              {/* 3 Autonomous Agent Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {orchestratorResult.agent_insights.map((insight, idx) => (
                  <div
                    key={idx}
                    className="glass-panel p-4 rounded-2xl border border-white/10 bg-[#0d111f]/60 space-y-3 flex flex-col justify-between"
                  >
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white flex items-center gap-1.5">
                          {insight.agent_name.includes("Planner") ? (
                            <Calendar className="w-3.5 h-3.5 text-blue-400" />
                          ) : insight.agent_name.includes("Research") ? (
                            <BrainCircuit className="w-3.5 h-3.5 text-blue-400" />
                          ) : (
                            <Layers className="w-3.5 h-3.5 text-amber-400" />
                          )}
                          {insight.agent_name}
                        </span>
                        <span className="text-[9px] px-1.5 py-0.5 rounded bg-white/[0.05] text-slate-400">
                          {insight.role}
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300 leading-relaxed">{insight.summary}</p>
                    </div>

                    <div className="space-y-1.5 pt-2 border-t border-white/5">
                      <span className="text-[10px] text-slate-400 font-semibold block">Key Findings:</span>
                      <ul className="space-y-1">
                        {insight.findings.map((finding, fIdx) => (
                          <li
                            key={fIdx}
                            className="text-[10px] text-slate-300 flex items-start gap-1.5 leading-snug"
                          >
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1 shrink-0" />
                            {finding}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>

              {/* Recommended Next Actions Checklist */}
              {orchestratorResult.recommended_next_actions?.length > 0 && (
                <div className="glass-panel p-4 rounded-2xl border border-emerald-500/20 bg-emerald-950/10 space-y-3">
                  <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Recommended Actionable Next Steps
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {orchestratorResult.recommended_next_actions.map((act, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-xl bg-black/40 border border-white/5 text-xs text-slate-200 flex items-start gap-2"
                      >
                        <span className="w-5 h-5 rounded-md bg-emerald-500/20 text-emerald-300 flex items-center justify-center text-[10px] font-bold shrink-0">
                          {idx + 1}
                        </span>
                        <span>{act}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* SECTION 4: CODE ASSISTANT & READINESS AUDIT */}
      {activeSection === "code_audit" && (
        <div className="space-y-6">
          {/* Readiness Report Banner / Results */}
          <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-[#0d111f]/70 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Award className="w-4 h-4 text-blue-400" /> Deterministic Project Readiness Rubric
                </h3>
                <p className="text-xs text-slate-400">
                  Authoritative 4-pillar score evaluating Architecture & Security (30%), Code Quality (25%),
                  Test Coverage (25%), and Documentation (20%).
                </p>
              </div>

              <button
                onClick={handleRunAudit}
                disabled={loadingAudit}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center gap-2 self-start md:self-auto"
              >
                {loadingAudit ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Evaluating Rubric...
                  </>
                ) : (
                  <>
                    <RotateCcw className="w-3.5 h-3.5" /> Re-Evaluate Readiness
                  </>
                )}
              </button>
            </div>

            {auditReport && (
              <div className="space-y-5 animate-in fade-in duration-300 pt-2">
                {/* Hero Grade Card */}
                <div className="p-5 rounded-2xl bg-gradient-to-r from-blue-950/40 via-slate-900/40 to-slate-900/40 border border-blue-500/30 flex flex-col md:flex-row items-center justify-between gap-6">
                  <div className="flex items-center gap-5">
                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-600 to-cyan-600 flex flex-col items-center justify-center text-white shadow-xl shadow-blue-900/30 border border-blue-400/40">
                      <span className="text-3xl font-extrabold leading-none">{auditReport.letter_grade}</span>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-200 mt-1">
                        Grade
                      </span>
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h4 className="text-base font-bold text-white">
                          Overall Readiness Score: {auditReport.readiness_score}/100
                        </h4>
                        <span
                          className={`text-[10px] font-bold px-2 py-0.5 rounded-md border ${
                            auditReport.readiness_score >= 80
                              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                              : auditReport.readiness_score >= 60
                              ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                              : "bg-red-500/20 text-red-300 border-red-500/30"
                          }`}
                        >
                          {auditReport.readiness_score >= 80
                            ? "Demo Ready"
                            : auditReport.readiness_score >= 60
                            ? "In Progress"
                            : "Action Required"}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 max-w-xl">{auditReport.summary}</p>
                    </div>
                  </div>

                  {/* 4 Pillars Progress Meters */}
                  <div className="grid grid-cols-2 gap-3 w-full md:w-80">
                    <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1">
                      <div className="flex justify-between text-[10px]">
                        <span className="text-slate-400">Architecture (30%)</span>
                        <span className="text-blue-300 font-bold">{auditReport.architecture_score}%</span>
                      </div>
                      <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-cyan-500 h-full rounded-full"
                          style={{ width: `${auditReport.architecture_score}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1">
                      <div className="flex justify-between text-[10px]">
                        <span className="text-slate-400">Code Quality (25%)</span>
                        <span className="text-blue-300 font-bold">{auditReport.code_quality_score}%</span>
                      </div>
                      <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-blue-500 h-full rounded-full"
                          style={{ width: `${auditReport.code_quality_score}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1">
                      <div className="flex justify-between text-[10px]">
                        <span className="text-slate-400">Test Coverage (25%)</span>
                        <span className="text-amber-300 font-bold">{auditReport.test_coverage_score}%</span>
                      </div>
                      <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-amber-500 h-full rounded-full"
                          style={{ width: `${auditReport.test_coverage_score}%` }}
                        />
                      </div>
                    </div>

                    <div className="p-2.5 rounded-xl bg-black/40 border border-white/5 space-y-1">
                      <div className="flex justify-between text-[10px]">
                        <span className="text-slate-400">Documentation (20%)</span>
                        <span className="text-emerald-300 font-bold">{auditReport.documentation_score}%</span>
                      </div>
                      <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-emerald-500 h-full rounded-full"
                          style={{ width: `${auditReport.documentation_score}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Passed Checks & Critical Findings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/20 space-y-2">
                    <h5 className="text-xs font-bold text-emerald-300 uppercase tracking-wider flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" /> Passed Quality Gates
                    </h5>
                    <ul className="space-y-1.5">
                      {auditReport.passed_checks?.map((check, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <Check className="w-3.5 h-3.5 text-emerald-400 mt-0.5 shrink-0" />
                          <span>{check}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/20 space-y-2">
                    <h5 className="text-xs font-bold text-amber-300 uppercase tracking-wider flex items-center gap-1.5">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Blockers & Critical Findings
                    </h5>
                    <ul className="space-y-1.5">
                      {auditReport.critical_findings?.map((finding, idx) => (
                        <li key={idx} className="text-xs text-slate-300 flex items-start gap-2">
                          <AlertCircle className="w-3.5 h-3.5 text-amber-400 mt-0.5 shrink-0" />
                          <span>{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Interactive Code Review & Unit Test Generator */}
          <div className="glass-panel p-5 rounded-2xl border border-white/10 bg-[#0d111f]/70 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-blue-400" /> Code Review & Unit Test Generator
                </h3>
                <p className="text-xs text-slate-400">
                  Inspect code for security vulnerabilities, memory anti-patterns, and generate production-ready
                  pytest/vitest suites.
                </p>
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={codeLanguage}
                  onChange={(e) => {
                    const l = e.target.value;
                    setCodeLanguage(l);
                    setCodeSnippet(l === "python" ? SAMPLE_CODE_SNIPPETS.python : SAMPLE_CODE_SNIPPETS.typescript);
                  }}
                  className="px-3 py-1.5 rounded-lg bg-black/50 border border-white/10 text-slate-200 text-xs focus:outline-none"
                >
                  <option value="python">Python</option>
                  <option value="typescript">TypeScript</option>
                </select>

                <select
                  value={testFramework}
                  onChange={(e) => setTestFramework(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-black/50 border border-white/10 text-slate-200 text-xs focus:outline-none"
                >
                  <option value="pytest">pytest</option>
                  <option value="vitest">vitest</option>
                </select>
              </div>
            </div>

            <textarea
              rows={8}
              value={codeSnippet}
              onChange={(e) => setCodeSnippet(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-blue-200 font-mono text-xs focus:outline-none focus:border-blue-500 leading-relaxed"
            />

            <div className="flex items-center gap-3">
              <button
                onClick={handleReviewCode}
                disabled={reviewingCode || !codeSnippet.trim()}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center gap-2"
              >
                {reviewingCode ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Shield className="w-3.5 h-3.5" />}
                Review Code & Security
              </button>

              <button
                onClick={handleGenerateTests}
                disabled={generatingTests || !codeSnippet.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-md flex items-center gap-2"
              >
                {generatingTests ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <FileCode className="w-3.5 h-3.5" />
                )}
                Generate Unit Tests
              </button>
            </div>

            {/* Code Review Result */}
            {reviewResult && (
              <div className="p-4 rounded-xl bg-[#0b0e1a] border border-blue-500/30 space-y-3 animate-in fade-in duration-200">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-blue-300 uppercase tracking-wider flex items-center gap-1.5">
                    <Shield className="w-3.5 h-3.5 text-blue-400" /> Review Score: {reviewResult.score}/100
                  </span>
                  <span className="text-[10px] text-slate-400">{reviewResult.summary}</span>
                </div>

                <div className="space-y-2">
                  {reviewResult.review_items?.map((item, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-lg bg-black/40 border border-white/5 text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-white">{item.issue}</span>
                        <span
                          className={`text-[9px] font-bold uppercase px-1.5 py-0.2 rounded ${
                            item.severity === "high" || item.severity === "critical"
                              ? "bg-red-500/20 text-red-300"
                              : "bg-amber-500/20 text-amber-300"
                          }`}
                        >
                          {item.severity}
                        </span>
                      </div>
                      <p className="text-slate-400 text-[11px]">{item.recommendation}</p>
                    </div>
                  ))}
                </div>

                {reviewResult.suggested_refactor && (
                  <div className="space-y-1.5 pt-2 border-t border-white/5">
                    <span className="text-[11px] font-semibold text-emerald-300 block">Suggested Refactor:</span>
                    <pre className="p-3 rounded-lg bg-black/60 border border-white/10 text-emerald-300 font-mono text-[11px] overflow-x-auto">
                      {reviewResult.suggested_refactor}
                    </pre>
                  </div>
                )}
              </div>
            )}

            {/* Generated Tests Result */}
            {generatedTests && (
              <div className="p-4 rounded-xl bg-[#0b0e1a] border border-indigo-500/30 space-y-3 animate-in fade-in duration-200">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-indigo-300 uppercase tracking-wider flex items-center gap-1.5">
                    <FileCode className="w-3.5 h-3.5 text-indigo-400" /> Generated {generatedTests.framework} Tests
                  </span>
                  <button
                    onClick={() => copyToClipboard(generatedTests.test_code)}
                    className="flex items-center gap-1 px-2.5 py-1 rounded bg-white/[0.05] hover:bg-white/[0.1] text-slate-300 text-[11px] border border-white/10"
                  >
                    {copiedCode ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    {copiedCode ? "Copied!" : "Copy Tests"}
                  </button>
                </div>

                <pre className="p-4 rounded-xl bg-black/60 border border-white/10 text-slate-200 font-mono text-xs overflow-x-auto leading-relaxed">
                  {generatedTests.test_code}
                </pre>

                {generatedTests.test_cases_covered?.length > 0 && (
                  <div className="flex flex-wrap gap-2 pt-1">
                    <span className="text-[10px] text-slate-400 font-medium">Test Cases:</span>
                    {generatedTests.test_cases_covered.map((tc, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 text-[10px] border border-indigo-500/20"
                      >
                        <Check className="w-2.5 h-2.5 inline mr-1 text-emerald-400" />{tc}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
