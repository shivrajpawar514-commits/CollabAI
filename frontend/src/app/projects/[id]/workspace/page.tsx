"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Kanban,
  MessageSquare,
  Users,
  Target,
  FolderArchive,
  Activity,
  Plus,
  ArrowLeft,
  Send,
  Upload,
  Clock,
  AlertCircle,
  CheckCircle2,
  Paperclip,
  Check,
  X,
  Sparkles,
  FileText,
  UserPlus,
  ChevronRight,
  ChevronLeft,
  Pin,
  MessageCircle,
} from "lucide-react";
import {
  api,
  Project,
  Team,
  Task,
  Milestone,
  Message,
  FileAttachment,
  ActivityLog,
  Invitation,
  User,
  getAuthToken,
} from "@/lib/api";

const KANBAN_COLUMNS = [
  { id: "backlog", title: "Backlog", color: "border-slate-500/40 text-slate-400" },
  { id: "todo", title: "To Do", color: "border-blue-500/40 text-blue-400" },
  { id: "in_progress", title: "In Progress", color: "border-amber-500/40 text-amber-400" },
  { id: "review", title: "Review", color: "border-purple-500/40 text-purple-400" },
  { id: "completed", title: "Completed", color: "border-emerald-500/40 text-emerald-400" },
] as const;

function ProjectWorkspaceContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const projectId = params?.id as string;
  const initialTab = (searchParams.get("tab") as any) || "kanban";

  const [activeTab, setActiveTab] = useState<"kanban" | "chat" | "team" | "milestones" | "files" | "activity">(initialTab);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [team, setTeam] = useState<Team | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [files, setFiles] = useState<FileAttachment[]>([]);
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);

  // Modals & form state
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDesc, setNewTaskDesc] = useState("");
  const [newTaskPriority, setNewTaskPriority] = useState<"low" | "medium" | "high" | "urgent">("medium");
  const [newTaskHours, setNewTaskHours] = useState(8);
  const [newTaskMilestone, setNewTaskMilestone] = useState<string>("");
  const [newTaskAssignee, setNewTaskAssignee] = useState<string>("");

  const [selectedTaskDetail, setSelectedTaskDetail] = useState<Task | null>(null);
  const [newCommentText, setNewCommentText] = useState("");

  const [showMilestoneModal, setShowMilestoneModal] = useState(false);
  const [newMilestoneTitle, setNewMilestoneTitle] = useState("");
  const [newMilestoneDesc, setNewMilestoneDesc] = useState("");

  // Chat message input
  const [chatInput, setChatInput] = useState("");
  const [wsConnected, setWsConnected] = useState(false);
  const chatBottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Invite modal
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("Software Engineer");

  useEffect(() => {
    api.getMe().then(setCurrentUser).catch(() => {});
  }, []);

  useEffect(() => {
    if (!projectId) return;

    // Load Project & Workspace datasets
    api.getProject(projectId).then(setProject).catch(() => {});
    api.getTeam(projectId).then(setTeam).catch(() => {});
    api.getTasks(projectId).then(setTasks).catch(() => {});
    api.getMilestones(projectId).then(setMilestones).catch(() => {});
    api.getMessages(projectId).then(setMessages).catch(() => {});
    api.getFiles(projectId).then(setFiles).catch(() => {});
    api.getActivityFeed(projectId).then(setActivities).catch(() => {});
    api.listProjectInvitations(projectId).then(setInvitations).catch(() => {});

    // Setup WebSocket
    const token = getAuthToken() || "";
    const wsUrl = `ws://localhost:8000/api/v1/ws/projects/${projectId}?token=${token}`;
    let socket: WebSocket | null = null;
    try {
      socket = new WebSocket(wsUrl);
      socket.onopen = () => setWsConnected(true);
      socket.onclose = () => setWsConnected(false);
      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "chat_message") {
            setMessages((prev) => [...prev, payload.data]);
          } else if (payload.type === "task_created") {
            setTasks((prev) => [...prev, payload.data]);
          } else if (payload.type === "task_moved" || payload.type === "task_updated") {
            setTasks((prev) => prev.map((t) => (t.id === payload.data.id ? payload.data : t)));
          } else if (payload.type === "task_comment_added") {
            if (selectedTaskDetail && selectedTaskDetail.id === payload.data.task_id) {
              setSelectedTaskDetail((prev) =>
                prev ? { ...prev, comments: [...(prev.comments || []), payload.data.comment] } : null
              );
            }
          } else if (payload.type === "file_uploaded") {
            setFiles((prev) => [payload.data, ...prev]);
          }
        } catch {}
      };
    } catch {
      setWsConnected(false);
    }

    return () => {
      if (socket) socket.close();
    };
  }, [projectId]);

  useEffect(() => {
    if (activeTab === "chat") {
      chatBottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, activeTab]);

  // Task actions
  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    try {
      const created = await api.createTask(projectId, {
        title: newTaskTitle,
        description: newTaskDesc,
        priority: newTaskPriority,
        estimated_hours: newTaskHours,
        milestone_id: newTaskMilestone || undefined,
        assignee_id: newTaskAssignee || undefined,
        status: "todo",
      });
      setTasks((prev) => [...prev, created]);
      setShowTaskModal(false);
      setNewTaskTitle("");
      setNewTaskDesc("");
    } catch (err: any) {
      alert(err.message || "Failed to create task");
    }
  };

  const handleMoveTask = async (task: Task, direction: "prev" | "next") => {
    const colOrder = ["backlog", "todo", "in_progress", "review", "completed"];
    const currentIndex = colOrder.indexOf(task.status);
    const targetIndex = direction === "next" ? currentIndex + 1 : currentIndex - 1;

    if (targetIndex < 0 || targetIndex >= colOrder.length) return;
    const newStatus = colOrder[targetIndex];

    // Optimistic update
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, status: newStatus as any } : t))
    );

    try {
      await api.moveTask(task.id, { status: newStatus, order_index: 0 });
    } catch {
      // Revert on failure
      api.getTasks(projectId).then(setTasks);
    }
  };

  const handleOpenTaskDetail = async (taskId: string) => {
    try {
      const detail = await api.getTaskDetail(taskId);
      setSelectedTaskDetail(detail);
    } catch {
      const fallback = tasks.find((t) => t.id === taskId);
      if (fallback) setSelectedTaskDetail(fallback);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCommentText.trim() || !selectedTaskDetail) return;

    try {
      const comment = await api.addTaskComment(selectedTaskDetail.id, newCommentText);
      setSelectedTaskDetail((prev) =>
        prev ? { ...prev, comments: [...(prev.comments || []), comment] } : null
      );
      setNewCommentText("");
    } catch (err: any) {
      alert(err.message || "Failed to post comment");
    }
  };

  // Milestone action
  const handleCreateMilestone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMilestoneTitle.trim()) return;

    try {
      const created = await api.createMilestone(projectId, {
        title: newMilestoneTitle,
        description: newMilestoneDesc,
        status: "pending",
      });
      setMilestones((prev) => [...prev, created]);
      setShowMilestoneModal(false);
      setNewMilestoneTitle("");
      setNewMilestoneDesc("");
    } catch (err: any) {
      alert(err.message || "Failed to create milestone");
    }
  };

  // Chat actions
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const content = chatInput;
    setChatInput("");

    try {
      const sent = await api.postMessage(projectId, content);
      setMessages((prev) => [...prev, sent]);
    } catch {
      // Fallback local echo if server disconnected
      if (currentUser) {
        setMessages((prev) => [
          ...prev,
          {
            id: `temp-${Date.now()}`,
            project_id: projectId,
            user_id: currentUser.id,
            content,
            mentions: [],
            is_pinned: false,
            created_at: new Date().toISOString(),
            user: currentUser,
          },
        ]);
      }
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      const uploaded = await api.uploadFile(projectId, file);
      setFiles((prev) => [uploaded, ...prev]);
    } catch (err: any) {
      alert(err.message || "Upload failed. Limit is 20MB.");
    }
  };

  // Respond to invitation / join request
  const handleRespondInvitation = async (invId: string, status: "accepted" | "rejected") => {
    try {
      await api.respondToInvitation(invId, status);
      setInvitations((prev) => prev.filter((i) => i.id !== invId));
      api.getTeam(projectId).then(setTeam);
    } catch (err: any) {
      alert(err.message || "Action failed");
    }
  };

  const completedCount = tasks.filter((t) => t.status === "completed").length;
  const progressPct = tasks.length > 0 ? Math.round((completedCount / tasks.length) * 100) : 0;

  return (
    <div className="space-y-6 pb-20 max-w-7xl mx-auto">
      {/* Workspace Top Banner */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <Link
            href={`/projects/${projectId}`}
            className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" /> Project Overview
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              {project?.title || "Project Workspace"}
            </h1>
            <span
              className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${
                wsConnected
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                  : "bg-amber-500/10 border-amber-500/30 text-amber-300"
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${wsConnected ? "bg-emerald-400" : "bg-amber-400"}`} />
              {wsConnected ? "Real-time Live" : "Offline Polling"}
            </span>
          </div>
          <p className="text-xs text-slate-400">
            {team?.name || "Student Engineering Team"} • {team?.members.length || 1} Active Collaborators • {progressPct}% Delivered
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowTaskModal(true)}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-md shadow-indigo-600/30 transition-all flex items-center gap-1.5"
          >
            <Plus className="w-4 h-4" /> Add Task
          </button>
          <button
            onClick={() => setShowMilestoneModal(true)}
            className="px-3.5 py-2.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-slate-200 text-xs font-semibold transition-all flex items-center gap-1.5"
          >
            <Target className="w-4 h-4 text-cyan-400" /> Milestone
          </button>
        </div>
      </div>

      {/* Tabs Bar */}
      <div className="flex flex-wrap items-center gap-2 border-b border-white/10 pb-2">
        {[
          { id: "kanban", name: "Kanban Board", icon: Kanban, count: tasks.length },
          { id: "chat", name: "Team Chat", icon: MessageSquare, count: messages.length },
          { id: "team", name: "Team & Invites", icon: Users, count: team?.members.length },
          { id: "milestones", name: "Roadmap", icon: Target, count: milestones.length },
          { id: "files", name: "Files & Assets", icon: FolderArchive, count: files.length },
          { id: "activity", name: "Activity Log", icon: Activity, count: activities.length },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                isActive
                  ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/25 border border-indigo-400/30"
                  : "bg-white/[0.03] text-slate-400 hover:text-white hover:bg-white/[0.06] border border-white/[0.05]"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.name}
              {tab.count !== undefined && (
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-black/40 text-slate-300">
                  {tab.count}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* TAB 1: KANBAN BOARD */}
      {activeTab === "kanban" && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-start">
            {KANBAN_COLUMNS.map((col) => {
              const colTasks = tasks.filter((t) => t.status === col.id);
              return (
                <div
                  key={col.id}
                  className="glass-panel p-4 rounded-2xl border border-white/10 flex flex-col min-h-[580px] bg-[#0b0e1a]/80"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-3">
                    <span className={`text-xs font-bold uppercase tracking-wider ${col.color}`}>
                      {col.title}
                    </span>
                    <span className="text-[11px] font-bold text-slate-400 px-2 py-0.5 rounded-full bg-white/5">
                      {colTasks.length}
                    </span>
                  </div>

                  <div className="space-y-3 flex-1">
                    {colTasks.map((task) => {
                      const priorityColor =
                        task.priority === "urgent"
                          ? "bg-red-500/20 text-red-300 border-red-500/30"
                          : task.priority === "high"
                          ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                          : task.priority === "medium"
                          ? "bg-indigo-500/20 text-indigo-300 border-indigo-500/30"
                          : "bg-slate-500/20 text-slate-300 border-slate-500/30";

                      return (
                        <div
                          key={task.id}
                          className="p-3.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.07] border border-white/[0.08] transition-all cursor-pointer group space-y-2.5"
                          onClick={() => handleOpenTaskDetail(task.id)}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <span
                              className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded border ${priorityColor}`}
                            >
                              {task.priority}
                            </span>
                            {task.estimated_hours && (
                              <span className="text-[10px] text-slate-400 flex items-center gap-1">
                                <Clock className="w-3 h-3 text-cyan-400" />
                                {task.estimated_hours}h
                              </span>
                            )}
                          </div>

                          <h3 className="font-semibold text-white text-xs leading-snug group-hover:text-indigo-300 transition-colors">
                            {task.title}
                          </h3>

                          {task.description && (
                            <p className="text-[11px] text-slate-400 line-clamp-2">
                              {task.description}
                            </p>
                          )}

                          <div className="pt-2 border-t border-white/[0.06] flex items-center justify-between text-[11px] text-slate-400">
                            <div className="flex items-center gap-2">
                              {task.assignee ? (
                                <div
                                  className="w-5 h-5 rounded-full bg-indigo-500/30 text-indigo-200 text-[10px] font-bold flex items-center justify-center"
                                  title={`Assigned to ${task.assignee.full_name}`}
                                >
                                  {task.assignee.full_name.charAt(0)}
                                </div>
                              ) : (
                                <span className="text-[10px] text-slate-500">Unassigned</span>
                              )}
                              <span className="flex items-center gap-1 text-[10px]">
                                <MessageCircle className="w-3 h-3 text-slate-400" />
                                {task.comments_count || 0}
                              </span>
                            </div>

                            {/* Column shifting buttons */}
                            <div
                              className="flex items-center gap-1"
                              onClick={(e) => e.stopPropagation()}
                            >
                              {col.id !== "backlog" && (
                                <button
                                  onClick={() => handleMoveTask(task, "prev")}
                                  className="p-1 rounded bg-white/5 hover:bg-white/15 text-slate-400 hover:text-white"
                                  title="Move Left"
                                >
                                  <ChevronLeft className="w-3 h-3" />
                                </button>
                              )}
                              {col.id !== "completed" && (
                                <button
                                  onClick={() => handleMoveTask(task, "next")}
                                  className="p-1 rounded bg-white/5 hover:bg-white/15 text-slate-400 hover:text-white"
                                  title="Move Right"
                                >
                                  <ChevronRight className="w-3 h-3" />
                                </button>
                              )}
                            </div>
                          </div>
                        </div>
                      );
                    })}

                    {colTasks.length === 0 && (
                      <div className="py-8 text-center text-[11px] text-slate-500 border border-dashed border-white/[0.08] rounded-xl">
                        No tasks in {col.title}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 2: REAL-TIME CHAT */}
      {activeTab === "chat" && (
        <div className="glass-panel rounded-2xl border border-white/10 flex flex-col h-[650px] overflow-hidden">
          {/* Chat Header */}
          <div className="p-4 border-b border-white/10 flex items-center justify-between bg-black/30">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-bold text-white">#general-team-chat</span>
              <span className="text-xs text-slate-400">({messages.length} messages)</span>
            </div>
            <span className="text-xs text-slate-400">
              Type <code className="text-cyan-400 font-mono">@name</code> to mention teammates
            </span>
          </div>

          {/* Message List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => {
              const isMe = currentUser && msg.user_id === currentUser.id;
              return (
                <div
                  key={msg.id}
                  className={`flex items-start gap-3 ${isMe ? "flex-row-reverse" : "flex-row"}`}
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 text-white text-xs font-bold flex items-center justify-center shrink-0">
                    {msg.user?.full_name?.charAt(0) || "U"}
                  </div>

                  <div className={`space-y-1 max-w-lg ${isMe ? "items-end text-right" : "items-start text-left"}`}>
                    <div className="flex items-center gap-2 text-[11px] text-slate-400">
                      <span className="font-semibold text-white">{msg.user?.full_name || "Teammate"}</span>
                      <span>{new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                      {msg.is_pinned && (
                        <span className="text-[10px] text-amber-400 flex items-center gap-0.5">
                          <Pin className="w-3 h-3" /> Pinned
                        </span>
                      )}
                    </div>

                    <div
                      className={`p-3 rounded-2xl text-xs leading-relaxed ${
                        isMe
                          ? "bg-indigo-600 text-white rounded-tr-none"
                          : "bg-white/[0.06] text-slate-200 border border-white/10 rounded-tl-none"
                      }`}
                    >
                      {msg.content}
                    </div>
                  </div>
                </div>
              );
            })}
            <div ref={chatBottomRef} />
          </div>

          {/* Chat Input Bar */}
          <form
            onSubmit={handleSendMessage}
            className="p-3 border-t border-white/10 bg-black/40 flex items-center gap-2"
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
            />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
              title="Upload Attachment (Max 20MB)"
            >
              <Paperclip className="w-4 h-4" />
            </button>

            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Message your project team... (use @username for mentions)"
              className="flex-1 bg-[#0e111d] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
            />

            <button
              type="submit"
              className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-md shadow-indigo-600/30"
            >
              <Send className="w-3.5 h-3.5" /> Send
            </button>
          </form>
        </div>
      )}

      {/* TAB 3: TEAM & INVITATIONS */}
      {activeTab === "team" && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-6">
            {/* Active Members */}
            <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <Users className="w-4 h-4 text-cyan-400" />
                  Active Team Members ({team?.members.length || 0})
                </h3>
                <span className="text-xs text-slate-400">Max {project?.max_team_size || 4} Members</span>
              </div>

              <div className="divide-y divide-white/[0.06]">
                {team?.members.map((member) => (
                  <div key={member.id} className="py-3 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-500 text-white text-xs font-bold flex items-center justify-center">
                        {member.user.full_name.charAt(0)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-white text-xs">{member.user.full_name}</span>
                          <span className="text-[10px] px-2 py-0.2 rounded-full bg-indigo-500/20 text-indigo-300 font-bold uppercase">
                            {member.role}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">{member.role_title || "Team Engineer"}</p>
                      </div>
                    </div>

                    <span className="text-[11px] text-slate-500">
                      Joined {new Date(member.joined_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Pending Requests */}
            {invitations.length > 0 && (
              <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
                <h3 className="font-bold text-white text-sm flex items-center gap-2 pb-3 border-b border-white/10">
                  <UserPlus className="w-4 h-4 text-amber-400" />
                  Pending Join Requests & Invitations ({invitations.length})
                </h3>

                <div className="space-y-3">
                  {invitations.map((inv) => (
                    <div
                      key={inv.id}
                      className="p-4 rounded-xl bg-black/40 border border-white/10 flex items-center justify-between gap-4"
                    >
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-white text-xs">
                            {inv.sender.full_name}
                          </span>
                          <span className="text-[10px] px-2 py-0.2 rounded bg-amber-500/20 text-amber-300 font-bold uppercase">
                            {inv.type}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          Role: <span className="text-white font-medium">{inv.role_name || "Member"}</span> • "{inv.message || "Excited to collaborate!"}"
                        </p>
                      </div>

                      {inv.status === "pending" && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleRespondInvitation(inv.id, "accepted")}
                            className="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1"
                          >
                            <Check className="w-3.5 h-3.5" /> Accept
                          </button>
                          <button
                            onClick={() => handleRespondInvitation(inv.id, "rejected")}
                            className="px-3 py-1.5 rounded-lg bg-red-600/30 hover:bg-red-600/50 text-red-200 border border-red-500/30 text-xs font-semibold flex items-center gap-1"
                          >
                            <X className="w-3.5 h-3.5" /> Reject
                          </button>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Invite Box */}
          <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 space-y-4 h-fit">
            <h3 className="font-bold text-white text-sm flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              Invite Teammates
            </h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Find students with missing skills (e.g. Flutter, PyTorch) from the discovery catalog and invite them.
            </p>
            <button
              onClick={() => router.push(`/projects?tab=teammates`)}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-cyan-500 hover:opacity-95 text-white text-xs font-bold transition-all flex items-center justify-center gap-1.5 shadow-md shadow-indigo-600/25"
            >
              Browse Teammate Recommendations
            </button>
          </div>
        </div>
      )}

      {/* TAB 4: ROADMAP & MILESTONES */}
      {activeTab === "milestones" && (
        <div className="space-y-6">
          {/* Progress Banner */}
          <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-3">
            <div className="flex items-center justify-between text-xs font-semibold">
              <span className="text-slate-300">Milestone & Delivery Progress</span>
              <span className="text-cyan-400 font-bold">{progressPct}% Complete ({completedCount}/{tasks.length} Tasks)</span>
            </div>
            <div className="w-full bg-black/40 h-2.5 rounded-full overflow-hidden border border-white/10">
              <div
                className="bg-gradient-to-r from-indigo-500 to-cyan-400 h-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>

          <div className="space-y-4">
            {milestones.map((m, idx) => {
              const statusColor =
                m.status === "completed"
                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
                  : m.status === "in_progress"
                  ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
                  : "bg-slate-500/20 text-slate-300 border-slate-500/30";

              return (
                <div
                  key={m.id}
                  className="glass-panel p-5 rounded-2xl border border-white/10 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-cyan-400">Step {idx + 1}</span>
                      <h4 className="font-bold text-white text-sm">{m.title}</h4>
                      <span className={`text-[10px] px-2 py-0.2 rounded border font-semibold uppercase ${statusColor}`}>
                        {m.status}
                      </span>
                    </div>
                    {m.description && <p className="text-xs text-slate-300">{m.description}</p>}
                  </div>

                  <span className="text-[11px] text-slate-400 shrink-0">
                    {tasks.filter((t) => t.milestone_id === m.id).length} linked tasks
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* TAB 5: FILES & ASSETS */}
      {activeTab === "files" && (
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-dashed border-white/20 text-center space-y-3">
            <Upload className="w-8 h-8 text-cyan-400 mx-auto" />
            <div>
              <p className="text-sm font-bold text-white">Upload Project Documents & PDFs</p>
              <p className="text-xs text-slate-400">Upload research papers, architecture diagrams, or datasets (Max 20MB)</p>
            </div>
            <input
              type="file"
              id="file-upload-zone"
              onChange={handleFileUpload}
              className="hidden"
            />
            <label
              htmlFor="file-upload-zone"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs cursor-pointer shadow-md shadow-indigo-600/30 transition-all"
            >
              Choose File
            </label>
          </div>

          <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-3">
            <h3 className="font-bold text-white text-sm pb-2 border-b border-white/10">
              Project Attachments ({files.length})
            </h3>
            <div className="divide-y divide-white/[0.06]">
              {files.map((f) => (
                <div key={f.id} className="py-3 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-indigo-400" />
                    <div>
                      <p className="font-semibold text-white text-xs">{f.file_name}</p>
                      <p className="text-[10px] text-slate-400">
                        {roundSize(f.file_size_bytes)} • Uploaded by {f.uploader?.full_name || "Team"}
                      </p>
                    </div>
                  </div>

                  <a
                    href={f.file_url}
                    download
                    className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold"
                  >
                    Download
                  </a>
                </div>
              ))}
              {files.length === 0 && (
                <p className="py-6 text-center text-xs text-slate-500">No files uploaded yet.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 6: ACTIVITY AUDIT LOG */}
      {activeTab === "activity" && (
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <h3 className="font-bold text-white text-sm pb-3 border-b border-white/10">
            Project Event Stream (AI & Team Context)
          </h3>
          <div className="space-y-4">
            {activities.map((act) => (
              <div key={act.id} className="flex items-start gap-3 text-xs">
                <div className="w-2 h-2 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                <div className="space-y-0.5">
                  <p className="text-white">{act.description}</p>
                  <p className="text-[10px] text-slate-500">
                    {new Date(act.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
            {activities.length === 0 && (
              <p className="py-6 text-center text-xs text-slate-500">No activity logged yet.</p>
            )}
          </div>
        </div>
      )}

      {/* MODAL: CREATE TASK */}
      {showTaskModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl border border-white/15 w-full max-w-lg space-y-4 bg-[#0d101d]">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="font-bold text-white text-base">Add New Kanban Task</h3>
              <button
                onClick={() => setShowTaskModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTask} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Task Title *</label>
                <input
                  type="text"
                  required
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  placeholder="e.g. Implement edge inference benchmarking"
                  className="w-full bg-[#141829] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Description</label>
                <textarea
                  rows={3}
                  value={newTaskDesc}
                  onChange={(e) => setNewTaskDesc(e.target.value)}
                  placeholder="Details, steps, and acceptance criteria..."
                  className="w-full bg-[#141829] border border-white/10 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">Priority</label>
                  <select
                    value={newTaskPriority}
                    onChange={(e) => setNewTaskPriority(e.target.value as any)}
                    className="w-full bg-[#141829] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">Estimated Hours</label>
                  <input
                    type="number"
                    min={1}
                    max={100}
                    value={newTaskHours}
                    onChange={(e) => setNewTaskHours(parseFloat(e.target.value))}
                    className="w-full bg-[#141829] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">Milestone</label>
                  <select
                    value={newTaskMilestone}
                    onChange={(e) => setNewTaskMilestone(e.target.value)}
                    className="w-full bg-[#141829] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">None</option>
                    {milestones.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.title}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-semibold text-slate-300">Assignee</label>
                  <select
                    value={newTaskAssignee}
                    onChange={(e) => setNewTaskAssignee(e.target.value)}
                    className="w-full bg-[#141829] border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Unassigned</option>
                    {team?.members.map((mem) => (
                      <option key={mem.user_id} value={mem.user_id}>
                        {mem.user.full_name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-md shadow-indigo-600/30 transition-all"
              >
                Create Task
              </button>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: TASK DETAIL & COMMENTS */}
      {selectedTaskDetail && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl border border-white/15 w-full max-w-xl space-y-4 bg-[#0d101d] max-h-[85vh] overflow-y-auto">
            <div className="flex items-start justify-between gap-4 pb-3 border-b border-white/10">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  {selectedTaskDetail.status} • {selectedTaskDetail.priority}
                </span>
                <h3 className="font-bold text-white text-base mt-2">{selectedTaskDetail.title}</h3>
              </div>
              <button
                onClick={() => setSelectedTaskDetail(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {selectedTaskDetail.description && (
              <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.06] text-xs text-slate-300 whitespace-pre-line">
                {selectedTaskDetail.description}
              </div>
            )}

            {/* Threaded Comments */}
            <div className="space-y-3 pt-2">
              <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                <MessageSquare className="w-3.5 h-3.5 text-cyan-400" />
                Comments & Discussion ({selectedTaskDetail.comments?.length || 0})
              </h4>

              <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                {selectedTaskDetail.comments?.map((c) => (
                  <div key={c.id} className="p-3 rounded-xl bg-black/30 border border-white/[0.06] space-y-1 text-xs">
                    <div className="flex items-center justify-between text-[10px] text-slate-400">
                      <span className="font-bold text-indigo-300">{c.user.full_name}</span>
                      <span>{new Date(c.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                    </div>
                    <p className="text-slate-200">{c.content}</p>
                  </div>
                ))}
                {(!selectedTaskDetail.comments || selectedTaskDetail.comments.length === 0) && (
                  <p className="text-[11px] text-slate-500 italic">No comments yet. Start the conversation!</p>
                )}
              </div>

              <form onSubmit={handleAddComment} className="flex gap-2 pt-2">
                <input
                  type="text"
                  value={newCommentText}
                  onChange={(e) => setNewCommentText(e.target.value)}
                  placeholder="Write a comment..."
                  className="flex-1 bg-[#141829] border border-white/10 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  Post
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: CREATE MILESTONE */}
      {showMilestoneModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel p-6 rounded-2xl border border-white/15 w-full max-w-md space-y-4 bg-[#0d101d]">
            <div className="flex items-center justify-between pb-3 border-b border-white/10">
              <h3 className="font-bold text-white text-base">Add Roadmap Milestone</h3>
              <button
                onClick={() => setShowMilestoneModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateMilestone} className="space-y-4">
              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Milestone Title *</label>
                <input
                  type="text"
                  required
                  value={newMilestoneTitle}
                  onChange={(e) => setNewMilestoneTitle(e.target.value)}
                  placeholder="e.g. Phase 2: Edge Quantization & Inference"
                  className="w-full bg-[#141829] border border-white/10 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-semibold text-slate-300">Deliverables / Notes</label>
                <textarea
                  rows={3}
                  value={newMilestoneDesc}
                  onChange={(e) => setNewMilestoneDesc(e.target.value)}
                  placeholder="Key outputs expected in this phase..."
                  className="w-full bg-[#141829] border border-white/10 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-md shadow-cyan-600/30 transition-all"
              >
                Create Milestone
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function roundSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function ProjectWorkspacePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#07090e] text-slate-100 flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-slate-400">Loading workspace...</p>
          </div>
        </div>
      }
    >
      <ProjectWorkspaceContent />
    </Suspense>
  );
}

