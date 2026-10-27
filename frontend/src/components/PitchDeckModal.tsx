"use client";

import { useState } from "react";
import {
  X,
  ChevronLeft,
  ChevronRight,
  Download,
  Copy,
  Check,
  Presentation,
  Volume2,
  Sparkles,
  Layers,
  ArrowRight,
} from "lucide-react";

export interface PitchDeckSlide {
  slide_number: number;
  title: string;
  subtitle?: string;
  key_points: string[];
  visual_suggestion: string;
  presenter_notes: string;
}

export interface HackathonPitchDeck {
  project_title: string;
  tagline: string;
  target_hackathon_track: string;
  slides: PitchDeckSlide[];
  executive_pitch_30s: string;
  key_metrics_summary: string[];
}

interface PitchDeckModalProps {
  isOpen: boolean;
  onClose: () => void;
  deck: HackathonPitchDeck | null;
  loading: boolean;
}

export default function PitchDeckModal({
  isOpen,
  onClose,
  deck,
  loading,
}: PitchDeckModalProps) {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [copied, setCopied] = useState(false);
  const [showNotes, setShowNotes] = useState(true);

  if (!isOpen) return null;

  const slides = deck?.slides || [];
  const currentSlide = slides[currentSlideIndex];

  const handleCopyMarkdown = () => {
    if (!deck) return;
    let md = `# ${deck.project_title} — Hackathon Pitch Deck\n`;
    md += `> ${deck.tagline}\n\n`;
    md += `**Target Track:** ${deck.target_hackathon_track}\n\n`;
    md += `### 30-Second Elevator Pitch\n${deck.executive_pitch_30s}\n\n---\n\n`;

    slides.forEach((s) => {
      md += `## Slide ${s.slide_number}: ${s.title}\n`;
      if (s.subtitle) md += `*${s.subtitle}*\n\n`;
      s.key_points.forEach((p) => {
        md += `- ${p}\n`;
      });
      md += `\n**Visual Suggestion:** ${s.visual_suggestion}\n\n`;
      md += `**Speaker Notes:** ${s.presenter_notes}\n\n---\n\n`;
    });

    navigator.clipboard.writeText(md);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    if (!deck) return;
    let md = `# ${deck.project_title} — Hackathon Pitch Deck\n`;
    md += `> ${deck.tagline}\n\n`;
    slides.forEach((s) => {
      md += `## Slide ${s.slide_number}: ${s.title}\n`;
      if (s.subtitle) md += `*${s.subtitle}*\n\n`;
      s.key_points.forEach((p) => {
        md += `- ${p}\n`;
      });
      md += `\n**Visual:** ${s.visual_suggestion}\n`;
      md += `**Script:** ${s.presenter_notes}\n\n---\n\n`;
    });

    const blob = new Blob([md], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${deck.project_title.toLowerCase().replace(/\s+/g, "-")}-pitch-deck.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel w-full max-w-4xl bg-[#0b0e1b] border border-white/15 rounded-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center">
              <Presentation className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Hackathon Pitch Deck Generator
                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  7 Slides
                </span>
              </h2>
              <p className="text-xs text-slate-400">{deck?.project_title || "Synthesizing presentation..."}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopyMarkdown}
              disabled={loading || !deck}
              className="px-3 py-1.5 text-xs font-medium rounded-lg bg-white/[0.05] border border-white/10 hover:bg-white/[0.1] text-slate-300 hover:text-white transition flex items-center gap-1.5"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? "Copied" : "Copy (.md)"}
            </button>
            <button
              onClick={handleDownload}
              disabled={loading || !deck}
              className="px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500/20 border border-emerald-500/30 hover:bg-emerald-500/30 text-emerald-300 transition flex items-center gap-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              Download
            </button>
            <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/[0.05]">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content Body */}
        {loading ? (
          <div className="p-16 flex flex-col items-center justify-center space-y-4">
            <div className="w-8 h-8 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-slate-300 font-medium">Generating structured pitch slides with AI...</p>
            <p className="text-xs text-slate-500">Synthesizing architecture decisions, tasks, and problem statement</p>
          </div>
        ) : currentSlide ? (
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {/* Slide Stage Card */}
            <div className="p-8 rounded-xl bg-gradient-to-b from-white/[0.03] to-transparent border border-white/10 space-y-6 relative overflow-hidden">
              <div className="flex items-center justify-between text-xs text-slate-400 border-b border-white/[0.06] pb-3">
                <span className="font-semibold text-emerald-400 uppercase tracking-wider">
                  Slide {currentSlide.slide_number} of {slides.length}
                </span>
                <span className="text-[11px] text-slate-500">Target Time: 45s</span>
              </div>

              <div className="space-y-2">
                <h3 className="text-2xl font-extrabold text-white tracking-tight">{currentSlide.title}</h3>
                {currentSlide.subtitle && <p className="text-sm text-slate-400 font-medium">{currentSlide.subtitle}</p>}
              </div>

              {/* Bullet points */}
              <div className="space-y-3 pt-2">
                {currentSlide.key_points.map((pt, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <div className="w-5 h-5 rounded bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-[11px] font-bold text-emerald-400">{idx + 1}</span>
                    </div>
                    <p className="text-sm text-slate-200 leading-relaxed">{pt}</p>
                  </div>
                ))}
              </div>

              {/* Visual recommendation */}
              <div className="p-3.5 rounded-lg bg-blue-500/[0.06] border border-blue-500/20 flex items-start gap-3">
                <Layers className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-blue-300">Recommended Visual / Slide Asset:</p>
                  <p className="text-xs text-slate-300">{currentSlide.visual_suggestion}</p>
                </div>
              </div>
            </div>

            {/* Presenter Notes */}
            <div className="p-5 rounded-xl bg-white/[0.02] border border-white/[0.08] space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                  <Volume2 className="w-4 h-4 text-cyan-400" />
                  Presenter Script (Speaking Notes)
                </div>
                <button
                  onClick={() => setShowNotes(!showNotes)}
                  className="text-[11px] text-slate-500 hover:text-slate-300"
                >
                  {showNotes ? "Collapse" : "Expand"}
                </button>
              </div>
              {showNotes && (
                <p className="text-xs text-slate-400 italic bg-black/30 p-3 rounded-lg border border-white/[0.04] leading-relaxed">
                  "{currentSlide.presenter_notes}"
                </p>
              )}
            </div>
          </div>
        ) : (
          <div className="p-12 text-center text-slate-400 text-sm">No slides available.</div>
        )}

        {/* Footer Navigation */}
        <div className="flex items-center justify-between px-6 py-4 border-t border-white/10 bg-white/[0.02]">
          <button
            onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
            disabled={currentSlideIndex === 0}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-white/[0.05] border border-white/10 hover:bg-white/[0.1] text-slate-300 hover:text-white disabled:opacity-40 transition flex items-center gap-1.5"
          >
            <ChevronLeft className="w-4 h-4" />
            Previous
          </button>

          {/* Dots Indicator */}
          <div className="flex items-center gap-1.5">
            {slides.map((_, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentSlideIndex(idx)}
                className={`h-2 rounded-full transition-all ${
                  idx === currentSlideIndex ? "w-6 bg-emerald-400" : "w-2 bg-white/20 hover:bg-white/40"
                }`}
              />
            ))}
          </div>

          <button
            onClick={() => setCurrentSlideIndex(Math.min(slides.length - 1, currentSlideIndex + 1))}
            disabled={currentSlideIndex === slides.length - 1}
            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-white/[0.05] border border-white/10 hover:bg-white/[0.1] text-slate-300 hover:text-white disabled:opacity-40 transition flex items-center gap-1.5"
          >
            Next
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
