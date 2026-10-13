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
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

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
};
