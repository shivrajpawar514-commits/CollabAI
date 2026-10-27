"use client";

import { useState } from "react";
import { X, Copy, Check, Download, FileText, Sparkles, ExternalLink } from "lucide-react";

export interface ProjectPortfolioExport {
  project_title: string;
  one_liner: string;
  problem_statement: string;
  solution_overview: string;
  tech_stack_highlights: string[];
  architecture_decisions: string[];
  milestone_timeline: string[];
  devpost_markdown: string;
}

interface PortfolioExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  portfolio: ProjectPortfolioExport | null;
  loading: boolean;
}

export default function PortfolioExportModal({
  isOpen,
  onClose,
  portfolio,
  loading,
}: PortfolioExportModalProps) {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!portfolio) return;
    navigator.clipboard.writeText(portfolio.devpost_markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!portfolio) return;
    const blob = new Blob([portfolio.devpost_markdown], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${portfolio.project_title.toLowerCase().replace(/\s+/g, "-")}-README.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-3xl bg-[#0b0e1b] border border-white/15 rounded-2xl overflow-hidden flex flex-col max-h-[85vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Devpost & GitHub Portfolio Exporter
              </h2>
              <p className="text-xs text-slate-400">
                Single-click clean markdown formatted for project showcases
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              disabled={loading || !portfolio}
              className="px-3 py-1.5 text-xs font-medium rounded-lg bg-white/[0.05] border border-white/10 hover:bg-white/[0.1] text-slate-300 hover:text-white transition flex items-center gap-1.5"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? "Copied" : "Copy Markdown"}
            </button>
            <button
              onClick={handleDownload}
              disabled={loading || !portfolio}
              className="px-3 py-1.5 text-xs font-medium rounded-lg bg-blue-500/20 border border-blue-500/30 hover:bg-blue-500/30 text-blue-300 transition flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              Download (.md)
            </button>
            <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05]">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Markdown Preview */}
        {loading ? (
          <div className="p-16 flex flex-col items-center justify-center space-y-4">
            <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-slate-300 font-medium">Assembling project portfolio & accomplishments...</p>
          </div>
        ) : portfolio ? (
          <div className="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs text-slate-300 bg-[#070911]">
            <pre className="p-4 rounded-xl bg-black/40 border border-white/[0.06] whitespace-pre-wrap leading-relaxed">
              {portfolio.devpost_markdown}
            </pre>
          </div>
        ) : (
          <div className="p-12 text-center text-slate-400 text-sm">No export data available.</div>
        )}

        {/* Footer */}
        <div className="px-6 py-3 border-t border-white/10 bg-white/[0.02] flex items-center justify-between text-xs text-slate-400">
          <span>Ready for GitHub README.md or Devpost Submission</span>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
