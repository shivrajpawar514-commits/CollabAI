"use client";

import { useState, useEffect, useRef } from "react";
import {
  BookOpen,
  UploadCloud,
  FileText,
  Sparkles,
  Trash2,
  Search,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Layers,
  Loader2,
  ShieldCheck,
  Eye,
  RefreshCw,
  X,
  FileCode,
  FileSpreadsheet,
  CornerDownLeft,
  ChevronRight,
  Quote,
} from "lucide-react";
import {
  api,
  DocumentItem,
  DocumentChunkItem,
  CitationItem,
  RAGQueryResponse,
} from "@/lib/api";

interface ResearchTabProps {
  projectId: string;
  projectTitle: string;
}

interface QnAPair {
  id: string;
  query: string;
  answer: string;
  groundedness_score: number;
  citations: CitationItem[];
  retrieved_chunks: DocumentChunkItem[];
  created_at: string;
}

export default function ResearchTab({ projectId, projectTitle }: ResearchTabProps) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [customTitle, setCustomTitle] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Q&A State
  const [query, setQuery] = useState("");
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([]);
  const [asking, setAsking] = useState(false);
  const [history, setHistory] = useState<QnAPair[]>([]);
  const [activeCitation, setActiveCitation] = useState<CitationItem | null>(null);

  // Chunk Inspector Modal State
  const [inspectDoc, setInspectDoc] = useState<DocumentItem | null>(null);
  const [chunks, setChunks] = useState<DocumentChunkItem[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  // Fetch documents on mount
  const fetchDocuments = async () => {
    try {
      setLoadingDocs(true);
      const docs = await api.getProjectDocuments(projectId);
      setDocuments(docs);
    } catch (err: any) {
      console.error("Failed to load project documents:", err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [projectId]);

  // Handle File Upload
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);
      setUploadError(null);
      await api.uploadDocument(projectId, file, customTitle || undefined);
      setCustomTitle("");
      if (fileInputRef.current) fileInputRef.current.value = "";
      await fetchDocuments();
    } catch (err: any) {
      setUploadError(err.message || "Failed to upload and index document.");
    } finally {
      setUploading(false);
    }
  };

  // Handle Document Delete
  const handleDeleteDoc = async (docId: string, title: string) => {
    if (!confirm(`Are you sure you want to remove '${title}' and purge its vector index?`)) return;
    try {
      await api.deleteDocument(projectId, docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      if (selectedDocIds.includes(docId)) {
        setSelectedDocIds((prev) => prev.filter((id) => id !== docId));
      }
    } catch (err: any) {
      alert("Failed to delete document: " + err.message);
    }
  };

  // Open Chunk Inspector
  const handleOpenChunks = async (doc: DocumentItem) => {
    setInspectDoc(doc);
    try {
      setLoadingChunks(true);
      const docChunks = await api.getDocumentChunks(projectId, doc.id);
      setChunks(docChunks);
    } catch (err: any) {
      alert("Failed to load chunks: " + err.message);
    } finally {
      setLoadingChunks(false);
    }
  };

  // Run RAG Query
  const handleAsk = async (customQuery?: string) => {
    const q = (customQuery || query).trim();
    if (!q || asking) return;

    try {
      setAsking(true);
      const res = await api.queryRAG(projectId, {
        query: q,
        top_k: 5,
        document_ids: selectedDocIds.length > 0 ? selectedDocIds : undefined,
      });

      const newEntry: QnAPair = {
        id: Math.random().toString(36).substring(7),
        query: res.query,
        answer: res.answer,
        groundedness_score: res.groundedness_score,
        citations: res.citations,
        retrieved_chunks: res.retrieved_chunks,
        created_at: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setHistory((prev) => [newEntry, ...prev]);
      if (!customQuery) setQuery("");
    } catch (err: any) {
      alert("AI Research query failed: " + err.message);
    } finally {
      setAsking(false);
    }
  };

  // Computed stats
  const totalPages = documents.reduce((acc, d) => acc + (d.total_pages || 0), 0);
  const totalChunks = documents.reduce((acc, d) => acc + (d.total_chunks || 0), 0);
  const indexedCount = documents.filter((d) => d.status === "indexed").length;

  return (
    <div className="space-y-6">
      {/* Top Banner & Overview */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900/40 border border-indigo-500/20 p-6 backdrop-blur-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                <BookOpen className="w-4 h-4" />
              </span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                AI Research & Knowledge Vault (RAG)
              </h2>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Phase 4
              </span>
            </div>
            <p className="text-xs text-slate-400 max-w-2xl leading-relaxed">
              Upload project research papers, technical architecture briefs, API docs, and markdown notes.
              Ask complex engineering questions with hybrid dense vector search, BM25 keyword matching, and verifiable inline citations.
            </p>
          </div>

          {/* Quick Metrics */}
          <div className="flex items-center gap-3">
            <div className="px-3.5 py-2 rounded-xl bg-white/[0.03] border border-white/10 text-center">
              <div className="text-base font-bold text-white">{documents.length}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-400">Documents</div>
            </div>
            <div className="px-3.5 py-2 rounded-xl bg-white/[0.03] border border-white/10 text-center">
              <div className="text-base font-bold text-cyan-400">{totalPages}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-400">Pages</div>
            </div>
            <div className="px-3.5 py-2 rounded-xl bg-white/[0.03] border border-white/10 text-center">
              <div className="text-base font-bold text-indigo-400">{totalChunks}</div>
              <div className="text-[10px] uppercase tracking-wider text-slate-400">Vectors</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Knowledge Vault & Document Manager (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Upload Area */}
          <div className="rounded-2xl bg-white/[0.02] border border-white/10 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <UploadCloud className="w-4 h-4 text-indigo-400" />
                Upload Document
              </h3>
              <span className="text-[10px] text-slate-500">PDF, MD, Code, TXT</span>
            </div>

            <div className="space-y-2">
              <input
                type="text"
                placeholder="Optional display title (e.g. System Design Spec)"
                value={customTitle}
                onChange={(e) => setCustomTitle(e.target.value)}
                disabled={uploading}
                className="w-full px-3 py-2 text-xs rounded-xl bg-white/[0.03] border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
              />

              <label
                className={`relative flex flex-col items-center justify-center p-5 border-2 border-dashed rounded-xl cursor-pointer transition-all ${
                  uploading
                    ? "border-indigo-500/40 bg-indigo-500/[0.05]"
                    : "border-white/10 hover:border-indigo-500/40 hover:bg-white/[0.02]"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.md,.markdown,.txt,.py,.ts,.tsx,.js,.json"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                />

                {uploading ? (
                  <div className="flex flex-col items-center gap-2 text-center">
                    <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
                    <span className="text-xs font-semibold text-indigo-300">
                      Parsing & embedding document...
                    </span>
                    <span className="text-[10px] text-slate-400">
                      Generating 384-dimensional dense semantic vectors
                    </span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center gap-1.5 text-center">
                    <div className="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-1">
                      <UploadCloud className="w-4 h-4" />
                    </div>
                    <span className="text-xs font-medium text-slate-200">
                      Click to choose or drag & drop file
                    </span>
                    <span className="text-[10px] text-slate-500">
                      Automatic section chunking & recursive overlap
                    </span>
                  </div>
                )}
              </label>

              {uploadError && (
                <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{uploadError}</span>
                </div>
              )}
            </div>
          </div>

          {/* Document Library List */}
          <div className="rounded-2xl bg-white/[0.02] border border-white/10 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Indexed Vault ({documents.length})
                </h3>
              </div>
              <button
                onClick={fetchDocuments}
                className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                title="Refresh Documents"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            {loadingDocs ? (
              <div className="py-8 flex flex-col items-center gap-2 text-slate-400">
                <Loader2 className="w-5 h-5 animate-spin text-indigo-400" />
                <span className="text-xs">Loading Knowledge Vault...</span>
              </div>
            ) : documents.length === 0 ? (
              <div className="py-8 px-4 rounded-xl border border-white/[0.05] bg-white/[0.01] text-center space-y-2">
                <BookOpen className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400 font-medium">No documents in vault yet</p>
                <p className="text-[11px] text-slate-500">
                  Upload a PDF or markdown file above to enable grounded RAG answering.
                </p>
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[480px] overflow-y-auto pr-1">
                {documents.map((doc) => {
                  const isSelected = selectedDocIds.includes(doc.id);
                  const isPdf = doc.file_type === "pdf";
                  const isCode = ["py", "ts", "js", "json"].includes(doc.file_type);

                  return (
                    <div
                      key={doc.id}
                      className={`group p-3 rounded-xl border transition-all ${
                        isSelected
                          ? "bg-indigo-950/30 border-indigo-500/40"
                          : "bg-white/[0.02] border-white/5 hover:border-white/15 hover:bg-white/[0.04]"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-start gap-2.5 min-w-0">
                          <div className="mt-0.5 p-1.5 rounded-lg bg-white/5 text-slate-300">
                            {isPdf ? (
                              <FileText className="w-4 h-4 text-rose-400" />
                            ) : isCode ? (
                              <FileCode className="w-4 h-4 text-amber-400" />
                            ) : (
                              <FileSpreadsheet className="w-4 h-4 text-indigo-400" />
                            )}
                          </div>
                          <div className="min-w-0">
                            <h4 className="text-xs font-semibold text-white truncate group-hover:text-indigo-300 transition-colors">
                              {doc.title}
                            </h4>
                            <p className="text-[10px] text-slate-400 truncate font-mono">
                              {doc.file_name}
                            </p>
                            <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                              <span
                                className={`px-2 py-0.5 rounded-md text-[9px] font-semibold border ${
                                  doc.status === "indexed"
                                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                    : doc.status === "processing"
                                    ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                    : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                                }`}
                              >
                                {doc.status.toUpperCase()}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                {doc.total_pages} {doc.total_pages === 1 ? "page" : "pages"}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                {doc.total_chunks} chunks
                              </span>
                              <span className="text-[10px] text-slate-500">
                                {(doc.file_size_bytes / 1024).toFixed(1)} KB
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => handleOpenChunks(doc)}
                            className="p-1.5 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                            title="Inspect Chunks"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDeleteDoc(doc.id, doc.title)}
                            className="p-1.5 rounded-lg hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                            title="Delete Document"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      {/* Filter Toggle */}
                      <div className="mt-2.5 pt-2 border-t border-white/5 flex items-center justify-between">
                        <label className="flex items-center gap-1.5 text-[10px] text-slate-400 cursor-pointer select-none">
                          <input
                            type="checkbox"
                            checked={isSelected}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setSelectedDocIds((prev) => [...prev, doc.id]);
                              } else {
                                setSelectedDocIds((prev) => prev.filter((id) => id !== doc.id));
                              }
                            }}
                            className="w-3 h-3 rounded bg-white/10 border-white/20 text-indigo-500 focus:ring-0"
                          />
                          <span>Focus search on this document</span>
                        </label>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: AI Research Assistant & Citations Engine (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Query Box */}
          <div className="rounded-2xl bg-white/[0.02] border border-white/10 p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Research Copilot Q&A
                </h3>
              </div>
              {selectedDocIds.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-indigo-300 bg-indigo-500/10 px-2 py-0.5 rounded-full border border-indigo-500/20">
                    Targeting {selectedDocIds.length} doc{selectedDocIds.length > 1 ? "s" : ""}
                  </span>
                  <button
                    onClick={() => setSelectedDocIds([])}
                    className="text-[10px] text-slate-400 hover:text-white"
                  >
                    Clear Filter
                  </button>
                </div>
              )}
            </div>

            {/* Quick Prompts */}
            <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
              {[
                "Summarize core architecture",
                "Key technical dependencies & risks",
                "Database schema & data models",
                "Deployment & API specifications",
              ].map((s) => (
                <button
                  key={s}
                  onClick={() => handleAsk(s)}
                  disabled={asking || documents.length === 0}
                  className="px-2.5 py-1 rounded-lg text-[11px] whitespace-nowrap bg-white/[0.03] hover:bg-white/[0.08] text-slate-300 border border-white/5 transition-all hover:border-indigo-500/30 disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>

            {/* Input field */}
            <div className="relative">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                    handleAsk();
                  }
                }}
                disabled={asking || documents.length === 0}
                placeholder={
                  documents.length === 0
                    ? "Upload documents first to start asking research questions..."
                    : "Ask any technical, algorithmic, or architectural question grounded in your documents (Cmd + Enter to submit)..."
                }
                rows={3}
                className="w-full px-3.5 py-2.5 text-xs rounded-xl bg-white/[0.03] border border-white/10 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 resize-none"
              />

              <div className="mt-2 flex items-center justify-between">
                <span className="text-[10px] text-slate-500">
                  Hybrid Dense (Cosine) + Sparse (BM25) Retrieval
                </span>
                <button
                  onClick={() => handleAsk()}
                  disabled={asking || !query.trim() || documents.length === 0}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/25 disabled:opacity-50 transition-all"
                >
                  {asking ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Retrieving & Answering...
                    </>
                  ) : (
                    <>
                      <Search className="w-3.5 h-3.5" />
                      Ask Assistant
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Results History */}
          <div className="space-y-4">
            {history.length === 0 && (
              <div className="rounded-2xl border border-white/[0.05] bg-white/[0.01] p-8 text-center space-y-3">
                <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-white">Grounded Research Copilot</h4>
                  <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                    Every answer is strictly cross-referenced against your project documents.
                    Inspect the source passages, page numbers, and exact quotes directly below.
                  </p>
                </div>
              </div>
            )}

            {history.map((entry) => (
              <div
                key={entry.id}
                className="rounded-2xl bg-white/[0.02] border border-white/10 p-5 space-y-4 backdrop-blur-xl"
              >
                {/* Query Title & Meta */}
                <div className="flex items-start justify-between gap-3 border-b border-white/5 pb-3">
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                      Research Query
                    </span>
                    <h4 className="text-sm font-bold text-white leading-snug">{entry.query}</h4>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold border flex items-center gap-1.5 ${
                        entry.groundedness_score >= 0.8
                          ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                          : entry.groundedness_score >= 0.5
                          ? "bg-cyan-500/10 text-cyan-400 border-cyan-500/20"
                          : "bg-amber-500/10 text-amber-400 border-amber-500/20"
                      }`}
                    >
                      <ShieldCheck className="w-3 h-3" />
                      {Math.round(entry.groundedness_score * 100)}% Grounded
                    </span>
                    <span className="text-[10px] text-slate-500">{entry.created_at}</span>
                  </div>
                </div>

                {/* Answer Content */}
                <div className="prose prose-invert prose-xs max-w-none text-slate-300 leading-relaxed space-y-2 whitespace-pre-wrap">
                  {entry.answer}
                </div>

                {/* Citations Tray */}
                {entry.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-white/5 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                        <Quote className="w-3 h-3 text-cyan-400" />
                        Verified In-Text Citations ({entry.citations.length})
                      </span>
                      <span className="text-[10px] text-slate-500">
                        Click any citation to inspect the source quote
                      </span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {entry.citations.map((c) => (
                        <div
                          key={c.index}
                          onClick={() => setActiveCitation(c)}
                          className="p-2.5 rounded-xl bg-white/[0.03] border border-white/5 hover:border-cyan-500/30 hover:bg-cyan-950/20 cursor-pointer transition-all space-y-1 group"
                        >
                          <div className="flex items-center justify-between">
                            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                              [{c.index}]
                            </span>
                            <span className="text-[10px] font-semibold text-emerald-400">
                              {(c.score * 100).toFixed(0)}% Match
                            </span>
                          </div>
                          <div className="text-xs font-medium text-white truncate group-hover:text-cyan-300 transition-colors">
                            {c.document_title}
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-slate-400">
                            <span>Page {c.page_number}</span>
                            <span className="text-[9px] text-slate-500 group-hover:text-cyan-400 flex items-center gap-0.5">
                              View excerpt <ChevronRight className="w-2.5 h-2.5" />
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Citation Popover Modal */}
      {activeCitation && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-2xl bg-slate-900 border border-white/10 p-6 space-y-4 shadow-2xl">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Source [{activeCitation.index}]
                  </span>
                  <span className="text-xs font-semibold text-emerald-400">
                    {Math.round(activeCitation.score * 100)}% Hybrid Relevance Score
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white">{activeCitation.document_title}</h3>
                <p className="text-xs text-slate-400">Page {activeCitation.page_number}</p>
              </div>
              <button
                onClick={() => setActiveCitation(null)}
                className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 rounded-xl bg-white/[0.03] border border-white/5 space-y-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Ground-Truth Verbatim Excerpt
              </span>
              <p className="text-xs text-slate-200 leading-relaxed font-mono whitespace-pre-wrap">
                "{activeCitation.snippet}"
              </p>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setActiveCitation(null)}
                className="px-4 py-1.5 rounded-xl text-xs font-semibold bg-white/10 hover:bg-white/15 text-white"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Chunk Inspector Modal */}
      {inspectDoc && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-3xl max-h-[85vh] rounded-2xl bg-slate-900 border border-white/10 p-6 flex flex-col space-y-4 shadow-2xl">
            <div className="flex items-start justify-between border-b border-white/10 pb-4">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-base font-bold text-white">
                    Vector Chunk Inspector: {inspectDoc.title}
                  </h3>
                </div>
                <p className="text-xs text-slate-400">
                  {inspectDoc.total_chunks} total chunks &bull; {inspectDoc.total_pages} extracted pages &bull; 384-dimensional dense vectors
                </p>
              </div>
              <button
                onClick={() => {
                  setInspectDoc(null);
                  setChunks([]);
                }}
                className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {loadingChunks ? (
                <div className="py-16 flex flex-col items-center gap-2 text-slate-400">
                  <Loader2 className="w-6 h-6 animate-spin text-cyan-400" />
                  <span className="text-xs">Loading vector chunks from database...</span>
                </div>
              ) : chunks.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-500">
                  No chunks generated for this document.
                </div>
              ) : (
                chunks.map((chk) => (
                  <div
                    key={chk.id}
                    className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 space-y-2 hover:border-white/10 transition-colors"
                  >
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-mono font-bold">
                          Chunk #{chk.chunk_index + 1}
                        </span>
                        <span>Page {chk.page_number}</span>
                        {chk.metadata_json?.heading && (
                          <span className="text-slate-300 font-medium">
                            &bull; {chk.metadata_json.heading}
                          </span>
                        )}
                      </div>
                      <span className="text-slate-500 font-mono">
                        {chk.token_count} words
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 font-mono leading-relaxed whitespace-pre-wrap bg-black/20 p-2.5 rounded-lg border border-white/5">
                      {chk.content}
                    </p>
                  </div>
                ))
              )}
            </div>

            <div className="pt-3 border-t border-white/10 flex justify-between items-center text-xs text-slate-500">
              <span>Chunks are stored with pgvector / SQLite dense arrays</span>
              <button
                onClick={() => {
                  setInspectDoc(null);
                  setChunks([]);
                }}
                className="px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-white font-semibold transition-colors"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
