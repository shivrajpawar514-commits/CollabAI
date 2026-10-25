import Link from "next/link";
import { Shield, Lock, FileCheck, Database, ArrowLeft, CheckCircle2 } from "lucide-react";

export const metadata = {
  title: "Privacy Policy: CollabAI",
  description: "Privacy policy and data governance practices for CollabAI.",
};

export default function PrivacyPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto py-10 space-y-10">
      {/* Header */}
      <div className="space-y-4">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </Link>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight">Privacy Policy</h1>
            <p className="text-sm text-slate-400">Effective Date: October 18, 2026</p>
          </div>
        </div>
      </div>

      {/* Main Content Card */}
      <div className="glass-panel p-8 rounded-xl border border-white/10 space-y-8 text-sm text-slate-300 leading-relaxed">
        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Lock className="w-4 h-4 text-cyan-400" />
            1. Core Principle: Zero Tracking & Data Ownership
          </h2>
          <p>
            CollabAI is an open-source student project collaboration platform designed with a strict privacy-first architecture. We do not sell your personal data, we do not operate third-party tracking or advertising cookies, and we do not monetize student project intellectual property.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-400" />
            2. Information We Collect
          </h2>
          <p>
            When utilizing CollabAI for academic teamwork, we store only the data required to facilitate team matching and workspace orchestration:
          </p>
          <ul className="space-y-2 pl-4">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
              <span><strong>Account Information:</strong> Full name, university email address, GitHub username, and chosen avatar URL.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
              <span><strong>Technical Profile:</strong> Self-reported engineering skills, primary programming languages, weekly time availability, and project interests.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
              <span><strong>Workspace Deliverables:</strong> Project milestones, Kanban task statuses, meeting summaries, and Architectural Decision Records (ADRs).</span>
            </li>
          </ul>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileCheck className="w-4 h-4 text-emerald-400" />
            3. AI & LLM Processing
          </h2>
          <p>
            Project decomposition, task estimation, and research summarization requests are processed through configured inference providers (e.g., Gemini API, Groq, or local Ollama instances). Your project briefs and meeting transcripts are transmitted strictly for real-time task generation and are never used to train public foundational models.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">4. Local Storage & Security</h2>
          <p>
            Authentication credentials and session tokens are preserved strictly within your browser&apos;s local storage. All network communication between the Next.js client and FastAPI backend is conducted over authenticated TLS connections.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">5. Data Retention & Deletion Rights</h2>
          <p>
            You retain absolute ownership of all code, documentation, and metadata uploaded to your team workspaces. You may request full deletion of your user account, profile, and associated project milestones at any time via the project settings or by clearing your local workspace state.
          </p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-white">6. Updates & Inquiries</h2>
          <p>
            Any amendments to this policy will be committed directly to the open-source repository change log. If you have questions regarding data governance, contact the engineering team at <span className="text-cyan-400 font-mono">privacy@collabai.dev</span>.
          </p>
        </section>
      </div>
    </div>
  );
}
