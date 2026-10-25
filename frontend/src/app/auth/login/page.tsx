"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import {
  Sparkles,
  LogIn,
  UserPlus,
  ArrowRight,
  ShieldCheck,
  Zap,
  Code2,
} from "lucide-react";
import { api, setAuthTokens } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") === "register" ? "register" : "login";

  const [tab, setTab] = useState<"login" | "register">(initialTab);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDemoLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.login({
        email: "student@collabai.dev",
        password: "password123",
      });
      setAuthTokens(res.access_token, res.refresh_token);
      router.push("/profile/onboarding");
    } catch (err: any) {
      // Mock local session if backend is not started
      setAuthTokens("mock_jwt_access_token_demo_12345", "mock_jwt_refresh_token_demo_12345");
      router.push("/profile/onboarding");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (tab === "login") {
        const res = await api.login({ email, password });
        setAuthTokens(res.access_token, res.refresh_token);
        router.push("/projects");
      } else {
        const res = await api.register({
          email,
          password,
          full_name: fullName,
        });
        setAuthTokens(res.access_token, res.refresh_token);
        router.push("/profile/onboarding");
      }
    } catch (err: any) {
      setError(err.message || "Authentication failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-8 sm:py-16 space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 p-[1.5px] shadow-lg shadow-blue-500/25">
          <div className="w-full h-full bg-[#0d101d] rounded-[14px] flex items-center justify-center">
            <Code2 className="w-6 h-6 text-cyan-400" />
          </div>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          {tab === "login" ? "Welcome back" : "Join CollabAI"}
        </h1>
        <p className="text-xs sm:text-sm text-slate-400">
          The open engineering platform for student hackathons & project teams.
        </p>
      </div>

      {/* Instant Demo Account Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950/40 to-slate-900/40 border border-blue-500/30 glass-panel space-y-3 text-center">
        <div className="flex items-center justify-center gap-1.5 text-xs font-bold text-blue-300 uppercase tracking-wider">
          <Zap className="w-4 h-4 text-cyan-400" /> One-Click Demo Mode
        </div>
        <p className="text-xs text-slate-300">
          Sign in instantly as <span className="font-semibold text-white">Alex Chen</span> (Stanford CS) with pre-loaded skills & projects.
        </p>
        <button
          type="button"
          onClick={handleDemoLogin}
          disabled={loading}
          className="w-full py-2.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2"
        >
          <ShieldCheck className="w-4 h-4" />
          Sign In as Demo Student
        </button>
      </div>

      <div className="glass-panel p-6 sm:p-8 rounded-2xl border border-white/10 space-y-6">
        {/* Tab switcher */}
        <div className="grid grid-cols-2 p-1 rounded-xl bg-black/40 border border-white/10 text-xs font-semibold">
          <button
            type="button"
            onClick={() => setTab("login")}
            className={`py-2 rounded-lg transition-all ${
              tab === "login" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => setTab("register")}
            className={`py-2 rounded-lg transition-all ${
              tab === "register" ? "bg-indigo-600 text-white shadow-sm" : "text-slate-400 hover:text-white"
            }`}
          >
            Create Account
          </button>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-200 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {tab === "register" && (
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-300">Full Name</label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Alex Chen"
                className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
              />
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">College / Student Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@university.edu"
              className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-xs font-semibold text-slate-300">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-[#0e111d] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm shadow-md shadow-indigo-600/30 transition-all flex items-center justify-center gap-2"
          >
            {loading ? "Processing..." : tab === "login" ? "Sign In" : "Continue to Onboarding"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="py-24 text-center text-slate-400">Loading authentication...</div>}>
      <LoginForm />
    </Suspense>
  );
}

