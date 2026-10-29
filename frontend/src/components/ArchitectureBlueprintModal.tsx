"use client";

import { useState } from "react";
import {
  X,
  Network,
  Layers,
  Cpu,
  Database,
  Server,
  Globe,
  ShieldCheck,
  Copy,
  Check,
  Download,
  RefreshCw,
  Clock,
  ArrowRight,
  Code2,
  Sparkles,
  Lock,
  Workflow,
} from "lucide-react";

export interface ArchitectureComponent {
  name: string;
  category: string;
  tech_stack: string;
  description: string;
  latency_budget_ms: number;
  responsibilities: string[];
}

export interface ArchitectureDataFlow {
  flow_name: string;
  step_number: number;
  source_component: string;
  target_component: string;
  protocol: string;
  payload_summary: string;
}

export interface SystemArchitectureBlueprint {
  project_title: string;
  architecture_pattern: string;
  executive_summary: string;
  components: ArchitectureComponent[];
  data_flows: ArchitectureDataFlow[];
  mermaid_diagram: string;
  mermaid_sequence: string;
  security_isolation_notes: string[];
  scaling_bottlenecks_and_mitigations: string[];
}

interface ArchitectureBlueprintModalProps {
  isOpen: boolean;
  onClose: () => void;
  blueprint: SystemArchitectureBlueprint | null;
  loading: boolean;
  onRefresh: () => void;
}

export default function ArchitectureBlueprintModal({
  isOpen,
  onClose,
  blueprint,
  loading,
  onRefresh,
}: ArchitectureBlueprintModalProps) {
  const [activeTab, setActiveTab] = useState<"diagram" | "components" | "flows">("diagram");
  const [diagramMode, setDiagramMode] = useState<"graph" | "sequence">("graph");
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const currentMermaid =
    diagramMode === "graph"
      ? blueprint?.mermaid_diagram || ""
      : blueprint?.mermaid_sequence || "";

  const handleCopyMermaid = () => {
    if (!currentMermaid) return;
    navigator.clipboard.writeText(currentMermaid);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadSpec = () => {
    if (!blueprint) return;
    let md = `# ${blueprint.project_title} — System Architecture & Technical Specification\n\n`;
    md += `> **Architecture Pattern**: ${blueprint.architecture_pattern}\n\n`;
    md += `## 🏛️ Executive Overview\n${blueprint.executive_summary}\n\n---\n\n`;
    md += `## 📐 System Architecture Diagram\n\`\`\`mermaid\n${blueprint.mermaid_diagram}\n\`\`\`\n\n---\n\n`;
    md += `## ⚡ Core Interaction Sequence\n\`\`\`mermaid\n${blueprint.mermaid_sequence}\n\`\`\`\n\n---\n\n`;
    md += `## 🧩 Subsystem Matrix\n\n`;
    md += `| Component | Category | Tech Stack | SLA Budget | Responsibilities |\n`;
    md += `| :--- | :---: | :--- | :---: | :--- |\n`;
    for (const comp of blueprint.components) {
      md += `| **${comp.name}** | \`${comp.category}\` | ${comp.tech_stack} | ${comp.latency_budget_ms} ms | ${comp.responsibilities.join("; ")} |\n`;
    }
    md += `\n---\n\n## 🔒 Security & Isolation Policies\n`;
    for (const note of blueprint.security_isolation_notes) {
      md += `- [x] ${note}\n`;
    }
    md += `\n## 📈 Scalability Mitigations\n`;
    for (const mit of blueprint.scaling_bottlenecks_and_mitigations) {
      md += `- **Scale Factor**: ${mit}\n`;
    }

    const blob = new Blob([md], { type: "text/markdown;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${blueprint.project_title.toLowerCase().replace(/\s+/g, "-")}-ARCHITECTURE.md`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case "frontend":
        return <Globe className="w-4 h-4 text-sky-400" />;
      case "backend":
      case "api":
        return <Server className="w-4 h-4 text-indigo-400" />;
      case "database":
        return <Database className="w-4 h-4 text-emerald-400" />;
      case "ai_engine":
        return <Cpu className="w-4 h-4 text-purple-400" />;
      case "messaging":
        return <Workflow className="w-4 h-4 text-amber-400" />;
      default:
        return <Layers className="w-4 h-4 text-cyan-400" />;
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
      <div className="glass-panel w-full max-w-4xl bg-[#080b16] border border-white/15 rounded-2xl overflow-hidden flex flex-col max-h-[90vh] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/[0.02]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
              <Network className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-tight">
                  System Architecture Blueprint
                </h2>
                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-cyan-500/10 border border-cyan-500/30 text-cyan-300">
                  Live Topology
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Mermaid diagram generation, component SLAs, data flow pipelines & security isolation
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handleCopyMermaid}
              className="px-3 py-1.5 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-slate-300 text-xs font-medium transition-all flex items-center gap-1.5"
              title="Copy current Mermaid diagram code"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? "Copied!" : "Copy Mermaid"}
            </button>
            <button
              onClick={handleDownloadSpec}
              className="px-3 py-1.5 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/30 text-cyan-300 text-xs font-semibold transition-all flex items-center gap-1.5"
              title="Download architecture specification as Markdown"
            >
              <Download className="w-3.5 h-3.5" />
              Export .md
            </button>
            <button
              onClick={onRefresh}
              disabled={loading}
              className="w-8 h-8 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-slate-400 hover:text-white flex items-center justify-center transition-colors disabled:opacity-50"
              title="Re-synthesize architecture"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-slate-400 hover:text-white flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Pattern & Sub-Navigation Banner */}
        <div className="px-6 py-3.5 border-b border-white/10 bg-gradient-to-r from-cyan-500/[0.05] via-indigo-500/[0.03] to-transparent flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-400">Pattern:</span>
            <span className="text-xs font-semibold text-cyan-300 bg-cyan-500/10 border border-cyan-500/30 px-2.5 py-0.5 rounded-md">
              {blueprint?.architecture_pattern || "Event-Driven Micro-Monolith"}
            </span>
          </div>

          <div className="flex items-center gap-1.5 bg-white/[0.03] border border-white/10 p-1 rounded-xl">
            {[
              { id: "diagram", label: "Mermaid Diagrams", icon: Code2 },
              { id: "components", label: "Components & SLAs", icon: Layers },
              { id: "flows", label: "Data Flows & Security", icon: ShieldCheck },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm"
                      : "text-slate-400 hover:text-white hover:bg-white/[0.04]"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Main Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3">
              <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-xs text-slate-400">Synthesizing System Architecture Blueprint & Topology...</p>
            </div>
          ) : (
            <>
              {/* TAB 1: MERMAID DIAGRAMS */}
              {activeTab === "diagram" && (
                <div className="space-y-4">
                  {/* Mode switch */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => setDiagramMode("graph")}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                          diagramMode === "graph"
                            ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                            : "bg-white/[0.05] text-slate-400 hover:text-white"
                        }`}
                      >
                        System Topology (Graph TD)
                      </button>
                      <button
                        onClick={() => setDiagramMode("sequence")}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                          diagramMode === "sequence"
                            ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/30"
                            : "bg-white/[0.05] text-slate-400 hover:text-white"
                        }`}
                      >
                        Interaction Pipeline (Sequence Diagram)
                      </button>
                    </div>

                    <span className="text-[11px] text-slate-400 font-mono">
                      Render Ready: Mermaid v10+
                    </span>
                  </div>

                  {/* Mermaid Code Display Block */}
                  <div className="relative rounded-xl bg-[#05070f] border border-white/10 p-4 font-mono text-xs overflow-x-auto text-slate-300">
                    <pre className="whitespace-pre">{currentMermaid}</pre>
                  </div>

                  {/* Overview Card */}
                  <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-1.5">
                    <h4 className="text-xs font-bold text-white flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                      Executive Architectural Rationale
                    </h4>
                    <p className="text-xs text-slate-300 leading-relaxed">
                      {blueprint?.executive_summary}
                    </p>
                  </div>
                </div>
              )}

              {/* TAB 2: COMPONENTS & SLAS */}
              {activeTab === "components" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {(blueprint?.components || []).map((comp, idx) => (
                    <div
                      key={idx}
                      className="p-4 rounded-xl bg-white/[0.02] border border-white/10 hover:border-white/20 transition-all space-y-3"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <div className="w-7 h-7 rounded-lg bg-white/[0.04] border border-white/10 flex items-center justify-center">
                            {getCategoryIcon(comp.category)}
                          </div>
                          <div>
                            <h4 className="text-xs font-bold text-white tracking-tight">{comp.name}</h4>
                            <span className="text-[10px] text-slate-400 uppercase font-mono tracking-wider">
                              {comp.category}
                            </span>
                          </div>
                        </div>

                        <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {comp.latency_budget_ms} ms SLA
                        </span>
                      </div>

                      <div className="p-2 rounded-lg bg-black/30 border border-white/[0.05] text-[11px] text-cyan-200/90 font-mono">
                        {comp.tech_stack}
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed">{comp.description}</p>

                      <div className="space-y-1 pt-1 border-t border-white/[0.06]">
                        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                          Key Responsibilities:
                        </p>
                        {comp.responsibilities.map((r, rIdx) => (
                          <div key={rIdx} className="flex items-start gap-1.5 text-xs text-slate-300">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 mt-1.5 shrink-0" />
                            <span>{r}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* TAB 3: DATA FLOWS & SECURITY */}
              {activeTab === "flows" && (
                <div className="space-y-6">
                  {/* Sequence Flows */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                      <Workflow className="w-4 h-4 text-cyan-400" />
                      Critical Interaction Flows (End-to-End)
                    </h4>
                    <div className="space-y-2">
                      {(blueprint?.data_flows || []).map((flow, fIdx) => (
                        <div
                          key={fIdx}
                          className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 hover:border-white/20 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                        >
                          <div className="flex items-start gap-2.5">
                            <span className="w-5 h-5 rounded-md bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-mono font-bold flex items-center justify-center shrink-0 mt-0.5">
                              {flow.step_number}
                            </span>
                            <div>
                              <p className="font-bold text-white">{flow.flow_name}</p>
                              <p className="text-[11px] text-slate-400 mt-0.5">{flow.payload_summary}</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-300 bg-white/[0.05] border border-white/10">
                              {flow.source_component.split(" ")[0]}
                            </span>
                            <ArrowRight className="w-3 h-3 text-cyan-400" />
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-300 bg-white/[0.05] border border-white/10">
                              {flow.target_component.split(" ")[0]}
                            </span>
                            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold text-cyan-300 bg-cyan-500/10 border border-cyan-500/30">
                              {flow.protocol}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Security Policies */}
                  <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-3">
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                      <Lock className="w-4 h-4 text-emerald-400" />
                      Security & Isolation Posture
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {(blueprint?.security_isolation_notes || []).map((note, nIdx) => (
                        <div key={nIdx} className="flex items-start gap-2 text-xs text-slate-300">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                          <span>{note}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Scaling Mitigations */}
                  <div className="p-4 rounded-xl bg-white/[0.02] border border-white/10 space-y-3">
                    <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                      <Layers className="w-4 h-4 text-amber-400" />
                      Scaling Bottlenecks & Architectural Mitigations
                    </h4>
                    <div className="space-y-2">
                      {(blueprint?.scaling_bottlenecks_and_mitigations || []).map((mit, mIdx) => (
                        <div key={mIdx} className="p-2.5 rounded-lg bg-black/30 border border-white/[0.05] text-xs text-slate-300">
                          {mit}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3.5 border-t border-white/10 bg-white/[0.01] flex items-center justify-between text-xs text-slate-400">
          <span>
            {blueprint?.project_title || "Project"} • Architecture specification ready for production due diligence
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs shadow-md transition-all"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
