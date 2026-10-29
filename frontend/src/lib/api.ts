const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export interface User {
  id: string;
  email: string;
  full_name: string;
  avatar_url?: string;
  github_id?: string;
  is_active: boolean;
  created_at: string;
}

export interface Profile {
  id: string;
  user_id: string;
  college?: string;
  branch?: string;
  year?: string;
  bio?: string;
  location?: string;
  languages: string[];
  interests: string[];
  preferred_roles: string[];
  availability_hours_per_week: number;
  github_username?: string;
  linkedin_url?: string;
  portfolio_url?: string;
}

export interface Skill {
  id: string;
  name: string;
  category: string;
}

export interface UserSkill {
  id: string;
  skill_id: string;
  skill: Skill;
  proficiency_level: number;
}

export interface StudentProfileDetail {
  user: User;
  profile?: Profile;
  skills: UserSkill[];
}

export interface ProjectRole {
  id: string;
  project_id: string;
  role_name: string;
  capacity: number;
  filled_count: number;
}

export interface ProjectSkill {
  id: string;
  skill_id: string;
  skill: Skill;
  is_required: boolean;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  problem_statement?: string;
  owner_id: string;
  owner: User;
  status: string;
  max_team_size: number;
  repo_url?: string;
  demo_url?: string;
  created_at: string;
  updated_at: string;
  required_skills: ProjectSkill[];
  roles: ProjectRole[];
}

// Phase 2 Types
export interface TeamMember {
  id: string;
  team_id: string;
  user_id: string;
  role: string;
  role_title?: string;
  joined_at: string;
  user: User;
}

export interface Team {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  members: TeamMember[];
}

export interface Invitation {
  id: string;
  project_id: string;
  team_id: string;
  sender_id: string;
  recipient_id?: string;
  type: "invite" | "join_request";
  role_name?: string;
  message?: string;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
  updated_at: string;
  sender: User;
  recipient?: User;
}

export interface Milestone {
  id: string;
  project_id: string;
  title: string;
  description?: string;
  deadline?: string;
  order_index: number;
  status: "pending" | "in_progress" | "completed";
  created_at: string;
  updated_at: string;
}

export interface TaskComment {
  id: string;
  task_id: string;
  user_id: string;
  content: string;
  created_at: string;
  updated_at: string;
  user: User;
}

export interface TaskDependency {
  id: string;
  task_id: string;
  depends_on_task_id: string;
  depends_on_task?: Task;
}

export interface Task {
  id: string;
  project_id: string;
  milestone_id?: string;
  creator_id: string;
  assignee_id?: string;
  title: string;
  description?: string;
  status: "backlog" | "todo" | "in_progress" | "review" | "completed";
  priority: "low" | "medium" | "high" | "urgent";
  deadline?: string;
  estimated_hours?: number;
  order_index: number;
  created_at: string;
  updated_at: string;
  assignee?: User;
  creator: User;
  comments_count: number;
  dependencies?: TaskDependency[];
  milestone?: Milestone;
  comments?: TaskComment[];
}

export interface Message {
  id: string;
  project_id: string;
  user_id: string;
  content: string;
  mentions: string[];
  is_pinned: boolean;
  created_at: string;
  user: User;
}

export interface FileAttachment {
  id: string;
  project_id: string;
  uploader_id: string;
  file_name: string;
  file_url: string;
  file_size_bytes: number;
  content_type: string;
  created_at: string;
  uploader: User;
}

export interface Notification {
  id: string;
  user_id: string;
  actor_id?: string;
  title: string;
  message: string;
  type: string;
  link?: string;
  is_read: boolean;
  created_at: string;
  actor?: User;
}

export interface ActivityLog {
  id: string;
  project_id: string;
  user_id?: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  description: string;
  extra_data: Record<string, any>;
  created_at: string;
  user?: User;
}

// Phase 3: AI Interfaces
export interface RoleNeed {
  role_name: string;
  capacity: number;
  skills_required: string[];
  responsibilities: string;
}

export interface MilestonePlan {
  week_number: number;
  title: string;
  deliverables: string[];
}

export interface ProjectProposal {
  title: string;
  problem_statement: string;
  objectives: string[];
  technologies: string[];
  roles_needed: RoleNeed[];
  architecture: string;
  datasets: string[];
  risks: string[];
  metrics: string[];
  timeline_weeks: MilestonePlan[];
}

export interface MilestoneTaskItem {
  title: string;
  description: string;
  priority: string;
  estimated_hours: number;
  recommended_skills: string[];
}

export interface MilestoneItem {
  title: string;
  description: string;
  target_week: number;
  deliverables: string[];
  suggested_tasks: MilestoneTaskItem[];
}

export interface MilestoneDecomposition {
  project_title: string;
  overview: string;
  total_weeks: number;
  milestones: MilestoneItem[];
}

export interface SubTaskItem {
  title: string;
  description: string;
  priority: string;
  estimated_hours: number;
  required_skills: string[];
  suggested_role: string;
  dependencies: string[];
}

export interface TaskBreakdown {
  original_task_title: string;
  analysis: string;
  estimated_total_hours: number;
  subtasks: SubTaskItem[];
  potential_risks: string[];
  duplicate_or_conflict_warnings: string[];
}

export interface ActionSuggestion {
  action_type: string;
  label: string;
  detail?: string;
  payload: Record<string, any>;
}

export interface CopilotResponse {
  answer: string;
  suggested_actions: ActionSuggestion[];
  relevant_skills: string[];
}

export interface CandidateMatch {
  user_id: string;
  name: string;
  email: string;
  avatar_url?: string;
  college?: string;
  branch?: string;
  year?: string;
  match_score: number;
  skill_score: number;
  interest_score: number;
  availability_score: number;
  matching_skills: string[];
  missing_skills: string[];
  preferred_roles: string[];
  availability_hours: number;
  explanation: string;
}

export interface TeammateRecommendationResponse {
  project_id: string;
  project_title: string;
  recommendations: CandidateMatch[];
  total_analyzed: number;
}

// Phase 4 Types: Document & RAG Knowledge Vault
export interface DocumentItem {
  id: string;
  project_id: string;
  uploader_id: string;
  title: string;
  file_name: string;
  file_url: string;
  file_type: string;
  file_size_bytes: number;
  total_pages: number;
  total_chunks: number;
  status: "pending" | "processing" | "indexed" | "failed";
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunkItem {
  id: string;
  document_id: string;
  project_id: string;
  chunk_index: number;
  content: string;
  page_number: number;
  token_count: number;
  metadata_json?: Record<string, any>;
  created_at: string;
}

export interface CitationItem {
  index: number;
  document_id: string;
  document_title: string;
  page_number: number;
  chunk_id: string;
  snippet: string;
  score: number;
}

export interface RAGQueryRequest {
  query: string;
  top_k?: number;
  document_ids?: string[];
  stream?: boolean;
}

export interface RAGQueryResponse {
  query: string;
  answer: string;
  groundedness_score: number;
  citations: CitationItem[];
  retrieved_chunks: DocumentChunkItem[];
}

export interface DocumentUploadResponse {
  document: DocumentItem;
  message: string;
}

// Phase 5 Types: ML Intelligence, Matching v2/v3, Deadline Risk, Skill Graph
export interface CandidateMatchV2 {
  user_id: string;
  name: string;
  email: string;
  avatar_url?: string;
  college?: string;
  branch?: string;
  year?: string;
  match_score: number;
  ml_rank_score: number;
  acceptance_probability: number;
  skill_complementarity: number;
  interest_similarity: number;
  availability_score: number;
  experience_score: number;
  role_compatibility: number;
  past_collab_score: number;
  covered_gap_skills: string[];
  missing_project_skills: string[];
  preferred_roles: string[];
  availability_hours: number;
  feature_importance: Record<string, number>;
  explanation: string;
}

export interface TeammateMatchV2Response {
  project_id: string;
  project_title: string;
  recommendations: CandidateMatchV2[];
  total_analyzed: number;
}

export interface DeadlineRiskReport {
  project_id: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
  completion_rate: number;
  remaining_tasks: number;
  total_tasks: number;
  blocked_tasks: number;
  days_left: number;
  team_size: number;
  current_velocity_per_week: number;
  required_velocity_per_week: number;
  projected_delay_days: number;
  bottlenecks: string[];
  mitigation_suggestions: string[];
  feature_importance: Record<string, number>;
}

export interface FreeResource {
  title: string;
  url: string;
  provider: string;
  type: string;
}

export interface LearningStep {
  step_number: number;
  skill_name: string;
  category: string;
  difficulty: string;
  estimated_hours: number;
  is_direct_requirement: boolean;
  prerequisites: string[];
  free_resources: FreeResource[];
}

export interface SkillGapAnalysis {
  project_id: string;
  required_skills: string[];
  team_owned_skills: string[];
  missing_skills: string[];
  coverage_percentage: number;
  total_learning_hours: number;
  recommended_learning_path: LearningStep[];
}

export interface RecommendationFeedbackCreate {
  candidate_id: string;
  action: "accepted" | "invited" | "dismissed" | "viewed";
  match_score: number;
  ml_rank_score: number;
  feature_vector_json?: Record<string, any>;
}

export interface RecommendationFeedbackResponse {
  id: string;
  project_id: string;
  reviewer_id: string;
  candidate_id: string;
  action: string;
  match_score: number;
  ml_rank_score: number;
  created_at: string;
}

// Phase 7 Types: Voice Meeting Assistant, Decision Memory Graph, Multi-Agent Orchestrator, Code Assistant & Readiness
export interface MeetingActionItem {
  id: string;
  meeting_id: string;
  project_id: string;
  title: string;
  description: string;
  suggested_assignee?: string;
  priority: string;
  estimated_hours: number;
  is_converted: boolean;
  converted_task_id?: string;
  created_at: string;
}

export interface MeetingNoteItem {
  id: string;
  project_id: string;
  organizer_id: string;
  title: string;
  executive_summary: string;
  key_topics_json: string[];
  overall_sentiment: string;
  action_items: MeetingActionItem[];
  created_at: string;
}

export interface ConvertActionItemsResponse {
  converted_count: number;
  created_tasks: Task[];
}

export interface ProjectDecisionItem {
  id: string;
  project_id: string;
  recorder_id: string;
  what: string;
  why: string;
  who: string;
  alternatives_json: string[];
  tags_json: string[];
  linked_task_id?: string;
  linked_document_id?: string;
  created_at: string;
}

export interface DecisionQueryResponse {
  query: string;
  answer: string;
  confidence_score: number;
  matched_decisions: {
    id: string;
    project_id: string;
    what: string;
    why: string;
    who: string;
    when: string;
    alternatives_considered: string[];
    tags: string[];
    score: number;
  }[];
}

export interface AgentInsight {
  agent_name: string;
  role: string;
  summary: string;
  findings: string[];
}

export interface OrchestratorResponse {
  query: string;
  executive_synthesis: string;
  participating_agents: string[];
  agent_insights: AgentInsight[];
  recommended_next_actions: string[];
}

export interface CodeReviewItem {
  category: string;
  severity: string;
  line_number?: number;
  issue: string;
  recommendation: string;
}

export interface CodeReviewResponse {
  score: number;
  summary: string;
  review_items: CodeReviewItem[];
  suggested_refactor?: string;
}

export interface GeneratedTestsResult {
  framework: string;
  test_code: string;
  test_cases_covered: string[];
}

export interface ProjectReadinessReport {
  readiness_score: number;
  letter_grade: string;
  architecture_score: number;
  code_quality_score: number;
  test_coverage_score: number;
  documentation_score: number;
  summary: string;
  passed_checks: string[];
  critical_findings: string[];
  actionable_roadmap: string[];
}

export function getAuthToken(): string | null {


  if (typeof window === "undefined") return null;
  return localStorage.getItem("collabai_access_token");
}

export function setAuthTokens(accessToken: string, refreshToken: string) {
  if (typeof window === "undefined") return;
  localStorage.setItem("collabai_access_token", accessToken);
  localStorage.setItem("collabai_refresh_token", refreshToken);
}

export function clearAuthTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("collabai_access_token");
  localStorage.removeItem("collabai_refresh_token");
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    ...(options.headers || {}),
  };

  if (!(options.body instanceof FormData)) {
    (headers as Record<string, string>)["Content-Type"] = "application/json";
  }

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = "API request failed";
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errorDetail;
    } catch {
      // fallback
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Auth
  register: (body: { email: string; password: string; full_name: string }) =>
    request<{ access_token: string; refresh_token: string; user: User }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  login: (body: { email: string; password: string }) =>
    request<{ access_token: string; refresh_token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getMe: () => request<User>("/auth/me"),

  // Users & Profiles
  getMyProfile: () => request<StudentProfileDetail>("/users/me/profile"),
  updateProfile: (body: Partial<Profile>) =>
    request<Profile>("/users/me/profile", {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  addOrUpdateSkill: (body: { skill_id: string; proficiency_level: number }) =>
    request<UserSkill>("/users/me/skills", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Skills
  listSkills: (category?: string) =>
    request<Skill[]>(`/skills/${category ? `?category=${category}` : ""}`),

  // Projects
  listProjects: (params?: { q?: string; status?: string; page?: number; page_size?: number }) => {
    const qParams = new URLSearchParams();
    if (params?.q) qParams.set("q", params.q);
    if (params?.status) qParams.set("status", params.status);
    if (params?.page) qParams.set("page", params.page.toString());
    if (params?.page_size) qParams.set("page_size", params.page_size.toString());
    return request<{ items: Project[]; total: number; page: number; page_size: number }>(
      `/projects/?${qParams.toString()}`
    );
  },
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (body: any) =>
    request<Project>("/projects/", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  // Phase 2: Teams & Invitations
  getTeam: (projectId: string) => request<Team>(`/projects/${projectId}/team`),
  inviteMember: (projectId: string, body: { recipient_id: string; role_name?: string; message?: string }) =>
    request<Invitation>(`/projects/${projectId}/team/invite`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  sendJoinRequest: (projectId: string, body: { role_name?: string; message?: string }) =>
    request<Invitation>(`/projects/${projectId}/team/join-request`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listProjectInvitations: (projectId: string) => request<Invitation[]>(`/projects/${projectId}/team/invitations`),
  respondToInvitation: (invitationId: string, status: "accepted" | "rejected") =>
    request<Invitation>(`/teams/invitations/${invitationId}/respond`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    }),
  listMyInvitations: () => request<Invitation[]>("/users/me/invitations"),

  // Phase 2: Milestones & Tasks
  getMilestones: (projectId: string) => request<Milestone[]>(`/projects/${projectId}/milestones`),
  createMilestone: (projectId: string, body: Partial<Milestone>) =>
    request<Milestone>(`/projects/${projectId}/milestones`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateMilestone: (projectId: string, milestoneId: string, body: Partial<Milestone>) =>
    request<Milestone>(`/projects/${projectId}/milestones/${milestoneId}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  getTasks: (projectId: string) => request<Task[]>(`/projects/${projectId}/tasks`),
  createTask: (projectId: string, body: Partial<Task> & { dependency_ids?: string[] }) =>
    request<Task>(`/projects/${projectId}/tasks`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getTaskDetail: (taskId: string) => request<Task>(`/tasks/${taskId}`),
  updateTask: (taskId: string, body: Partial<Task>) =>
    request<Task>(`/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
  moveTask: (taskId: string, body: { status: string; order_index: number }) =>
    request<Task>(`/tasks/${taskId}/move`, {
      method: "PATCH",
      body: JSON.stringify(body),
    }),
  addTaskComment: (taskId: string, content: string) =>
    request<TaskComment>(`/tasks/${taskId}/comments`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  // Phase 2: Real-Time Chat & Files
  getMessages: (projectId: string) => request<Message[]>(`/projects/${projectId}/messages`),
  postMessage: (projectId: string, content: string, isPinned = false) =>
    request<Message>(`/projects/${projectId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content, is_pinned: isPinned }),
    }),
  getFiles: (projectId: string) => request<FileAttachment[]>(`/projects/${projectId}/files`),
  uploadFile: (projectId: string, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return request<FileAttachment>(`/projects/${projectId}/files/upload`, {
      method: "POST",
      body: formData,
    });
  },

  // Phase 2: Notifications & Activities
  getNotifications: () => request<Notification[]>("/notifications"),
  getUnreadCount: () => request<{ unread_count: number }>("/notifications/unread-count"),
  markNotificationRead: (notificationId: string) =>
    request<{ success: boolean }>(`/notifications/${notificationId}/read`, {
      method: "PATCH",
    }),
  markAllNotificationsRead: () =>
    request<{ count: number }>("/notifications/mark-all-read", {
      method: "POST",
    }),
  getActivityFeed: (projectId: string) => request<ActivityLog[]>(`/projects/${projectId}/activity-feed`),

  // Phase 3: AI Capabilities
  generateProject: (idea: string, constraints = "") =>
    request<ProjectProposal>("/ai/generate-project", {
      method: "POST",
      body: JSON.stringify({ idea, constraints }),
    }),

  planMilestones: (projectId: string, timelineWeeks = 8) =>
    request<MilestoneDecomposition>(`/ai/projects/${projectId}/plan-milestones`, {
      method: "POST",
      body: JSON.stringify({ timeline_weeks: timelineWeeks }),
    }),

  applyMilestones: (projectId: string, milestones: MilestoneItem[]) =>
    request<Milestone[]>(`/ai/projects/${projectId}/apply-milestones`, {
      method: "POST",
      body: JSON.stringify({ milestones }),
    }),

  decomposeTask: (taskId: string, additionalContext = "") =>
    request<TaskBreakdown>(`/ai/tasks/${taskId}/decompose`, {
      method: "POST",
      body: JSON.stringify({ additional_context: additionalContext }),
    }),

  applyDecomposition: (taskId: string, subtasks: SubTaskItem[], milestoneId?: string) =>
    request<Task[]>(`/ai/tasks/${taskId}/apply-decomposition`, {
      method: "POST",
      body: JSON.stringify({ milestone_id: milestoneId, subtasks }),
    }),

  recommendTeammates: (projectId: string) =>
    request<TeammateRecommendationResponse>(`/ai/projects/${projectId}/recommend-teammates`),

  copilotChat: (projectId: string, message: string, chatHistory: { role: string; content: string }[] = []) =>
    request<CopilotResponse>("/ai/copilot/chat", {
      method: "POST",
      body: JSON.stringify({ project_id: projectId, message, chat_history: chatHistory }),
    }),

  // Phase 4: RAG Knowledge Vault & Research
  uploadDocument: (projectId: string, file: File, title?: string) => {
    const formData = new FormData();
    formData.append("file", file);
    if (title) formData.append("title", title);
    return request<DocumentUploadResponse>(`/projects/${projectId}/documents/upload`, {
      method: "POST",
      body: formData,
    });
  },

  getProjectDocuments: (projectId: string) =>
    request<DocumentItem[]>(`/projects/${projectId}/documents`),

  getDocument: (projectId: string, docId: string) =>
    request<DocumentItem>(`/projects/${projectId}/documents/${docId}`),

  getDocumentChunks: (projectId: string, docId: string) =>
    request<DocumentChunkItem[]>(`/projects/${projectId}/documents/${docId}/chunks`),

  deleteDocument: (projectId: string, docId: string) =>
    request<void>(`/projects/${projectId}/documents/${docId}`, {
      method: "DELETE",
    }),

  queryRAG: (projectId: string, data: RAGQueryRequest) =>
    request<RAGQueryResponse>(`/projects/${projectId}/rag/query`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Phase 5: ML Intelligence, Matching v2/v3, Deadline Risk, Skill Graph
  getTeammateRecommendationsV2: (projectId: string) =>
    request<TeammateMatchV2Response>(`/projects/${projectId}/intelligence/teammates`),

  getDeadlineRisk: (projectId: string) =>
    request<DeadlineRiskReport>(`/projects/${projectId}/intelligence/deadline-risk`),

  getSkillGap: (projectId: string) =>
    request<SkillGapAnalysis>(`/projects/${projectId}/intelligence/skill-gap`),

  logRecommendationFeedback: (projectId: string, data: RecommendationFeedbackCreate) =>
    request<RecommendationFeedbackResponse>(`/projects/${projectId}/intelligence/feedback`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Phase 7: Advanced AI - Meetings, Decision Graph, Orchestrator, Code Assistant & Readiness
  analyzeMeeting: (projectId: string, transcriptText: string, meetingTitle?: string) =>
    request<MeetingNoteItem>(`/projects/${projectId}/meetings/analyze`, {
      method: "POST",
      body: JSON.stringify({ transcript_text: transcriptText, meeting_title: meetingTitle }),
    }),

  getProjectMeetings: (projectId: string) =>
    request<MeetingNoteItem[]>(`/projects/${projectId}/meetings`),

  convertMeetingActionItems: (projectId: string, actionItemIds: string[], targetMilestoneId?: string) =>
    request<ConvertActionItemsResponse>(`/projects/${projectId}/meetings/convert-tasks`, {
      method: "POST",
      body: JSON.stringify({ action_item_ids: actionItemIds, target_milestone_id: targetMilestoneId }),
    }),

  createDecision: (
    projectId: string,
    data: {
      what: string;
      why: string;
      who?: string;
      alternatives?: string[];
      tags?: string[];
      linked_task_id?: string;
      linked_document_id?: string;
    }
  ) =>
    request<ProjectDecisionItem>(`/projects/${projectId}/decisions`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getProjectDecisions: (projectId: string) =>
    request<ProjectDecisionItem[]>(`/projects/${projectId}/decisions`),

  queryDecisionMemory: (projectId: string, query: string) =>
    request<DecisionQueryResponse>(`/projects/${projectId}/decisions/query`, {
      method: "POST",
      body: JSON.stringify({ query }),
    }),

  runMultiAgentOrchestrator: (projectId: string, query: string) =>
    request<OrchestratorResponse>(`/projects/${projectId}/orchestrator/run`, {
      method: "POST",
      body: JSON.stringify({ query }),
    }),

  reviewCode: (projectId: string, code: string, fileName?: string, language?: string) =>
    request<CodeReviewResponse>(`/projects/${projectId}/code/review`, {
      method: "POST",
      body: JSON.stringify({ code, file_name: fileName, language }),
    }),

  generateTests: (projectId: string, code: string, fileName?: string, framework?: string) =>
    request<GeneratedTestsResult>(`/projects/${projectId}/code/tests`, {
      method: "POST",
      body: JSON.stringify({ code, file_name: fileName, framework }),
    }),

  auditProjectReadiness: (projectId: string) =>
    request<ProjectReadinessReport>(`/projects/${projectId}/readiness-audit`),

  getPitchDeck: (projectId: string) =>
    request<any>(`/projects/${projectId}/pitch-deck`),

  getPortfolioExport: (projectId: string) =>
    request<any>(`/projects/${projectId}/portfolio-export`),

  getVelocity: (projectId: string) =>
    request<any>(`/projects/${projectId}/velocity`),

  getJudgeEvaluation: (projectId: string, refresh: boolean = false) =>
    request<any>(`/projects/${projectId}/judge-eval${refresh ? "?refresh=true" : ""}`),

  getJudgeSummary: (projectId: string) =>
    request<any>(`/projects/${projectId}/judge-eval/summary`),

  getArchitectureBlueprint: (projectId: string, refresh: boolean = false) =>
    request<any>(`/projects/${projectId}/architecture-blueprint${refresh ? "?refresh=true" : ""}`),

  exportArchitectureBlueprint: (projectId: string) =>
    request<any>(`/projects/${projectId}/architecture-blueprint/export`),
};





