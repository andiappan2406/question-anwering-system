"use client";

import React, { useState } from "react";
import {
  Zap,
  Database,
  Search,
  Cpu,
  Clock,
  Code2,
  Table,
  CheckCircle2,
  Layers,
  Sparkles,
  X,
  Copy,
  Check,
  Activity,
} from "lucide-react";
import { RoutingPath, RoutingTrace } from "@/types/chat";
import { cn } from "@/lib/utils";

interface RoutingTracePanelProps {
  trace?: RoutingTrace | null;
  isOpen: boolean;
  onToggle: () => void;
  className?: string;
  useLlm?: boolean;
  onToggleLlm?: () => void;
}

export function RoutingTracePanel({
  trace,
  isOpen,
  onToggle,
  className,
  useLlm = true,
  onToggleLlm,
}: RoutingTracePanelProps) {
  const [activeTab, setActiveTab] = useState<"visual" | "json">("visual");
  const [copiedQuery, setCopiedQuery] = useState(false);

  const paths: {
    id: RoutingPath;
    name: string;
    icon: React.ElementType;
    tag: string;
    description: string;
    accent: {
      activeBorder: string;
      activeBg: string;
      activeText: string;
      glow: string;
      badge: string;
      dot: string;
    };
  }[] = [
      {
        id: "cache",
        name: "Cache Path",
        icon: Zap,
        tag: "L1 Semantic Cache",
        description: "Sub-10ms instant response via Redis semantic hashing",
        accent: {
          activeBorder: "border-[#4B6455]",
          activeBg: "bg-[#EEF2E6]",
          activeText: "text-[#3F5B3D]",
          glow: "shadow-xs",
          badge: "bg-[#EEF2E6] text-[#3F5B3D] border-[#B9CBAE]",
          dot: "#4B6455",
        },
      },
      {
        id: "sql",
        name: "SQL Path",
        icon: Database,
        tag: "Relational DB",
        description: "Text-to-SQL compiler querying transactional records",
        accent: {
          activeBorder: "border-[#0F1F38]",
          activeBg: "bg-[#EAF0F7]",
          activeText: "text-[#0F1F38]",
          glow: "shadow-xs",
          badge: "bg-[#EAF0F7] text-[#0F1F38] border-[#B9CEE3]",
          dot: "#0F1F38",
        },
      },
      {
        id: "vector",
        name: "Vector Path",
        icon: Search,
        tag: "Hybrid Vector DB",
        description: "Dense embedding similarity search over institutional docs",
        accent: {
          activeBorder: "border-[#5B3A52]",
          activeBg: "bg-[#F3ECEF]",
          activeText: "text-[#5B3A52]",
          glow: "shadow-xs",
          badge: "bg-[#F3ECEF] text-[#5B3A52] border-[#D9C2D4]",
          dot: "#5B3A52",
        },
      },
      {
        id: "llm",
        name: "LLM Path",
        icon: Cpu,
        tag: "Generative Model",
        description: "Open reasoning synthesis with guarded institutional system prompt",
        accent: {
          activeBorder: "border-[#3F3B36]",
          activeBg: "bg-[#EFEDE9]",
          activeText: "text-[#3F3B36]",
          glow: "shadow-xs",
          badge: "bg-[#EFEDE9] text-[#3F3B36] border-[#D6D0C8]",
          dot: "#3F3B36",
        },
      },
    ];

  const currentPath = trace?.path || "cache";
  const activePathConfig = paths.find((p) => p.id === currentPath) || paths[0];

  const handleCopySql = () => {
    if (trace?.sqlQuery) {
      navigator.clipboard.writeText(trace.sqlQuery);
      setCopiedQuery(true);
      setTimeout(() => setCopiedQuery(false), 2000);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Mobile Backdrop Overlay (< lg) */}
      <div
        className="fixed inset-0 bg-stone-900/40 backdrop-blur-xs z-40 lg:hidden animate-in fade-in duration-200"
        onClick={onToggle}
        aria-hidden="true"
      />

      {/* Slide-over Panel (Full-screen on mobile, sidebar on desktop) */}
      <aside
        aria-label="Routing Trace Panel"
        className={cn(
          "fixed inset-y-0 right-0 w-full sm:w-[420px] lg:static lg:w-96 xl:w-[420px] shrink-0 border-l border-stone-200 bg-[#F5F1EA] lg:bg-[#F5F1EA]/95 backdrop-blur-2xl flex flex-col h-full z-50 lg:z-30 shadow-2xl lg:shadow-none animate-in slide-in-from-right duration-250",
          className
        )}
      >
        {/* Panel Header */}
        <div className="p-3.5 sm:p-4 border-b border-stone-200 flex items-center justify-between shrink-0 bg-[#F5F1EA]">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-50 text-amber-900 border border-amber-300 shadow-xs">
              <Activity className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-serif text-sm font-semibold text-stone-900 flex items-center gap-1.5">
                Routing Trace
                <span className="text-[10px] px-1.5 py-0.5 rounded-md bg-amber-50 text-amber-900 border border-amber-300 font-mono">
                  Live
                </span>
              </h2>
              <p className="text-[11px] text-stone-600">Execution path of last query</p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Visual / JSON toggle */}
            <div className="bg-white p-0.5 rounded-lg border border-stone-300 flex text-[10px] shadow-xs">
              <button
                type="button"
                onClick={() => setActiveTab("visual")}
                className={cn(
                  "px-2 py-1 rounded-md font-medium transition-colors cursor-pointer",
                  activeTab === "visual"
                    ? "bg-stone-900 text-white shadow-xs"
                    : "text-stone-500 hover:text-stone-800"
                )}
              >
                Visual
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("json")}
                className={cn(
                  "px-2 py-1 rounded-md font-medium transition-colors cursor-pointer",
                  activeTab === "json"
                    ? "bg-stone-900 text-white shadow-xs"
                    : "text-stone-500 hover:text-stone-800"
                )}
              >
                JSON
              </button>
            </div>

            {/* Close Button */}
            <button
              type="button"
              onClick={onToggle}
              className="p-1.5 rounded-lg text-stone-500 hover:text-stone-900 hover:bg-stone-200/70 transition-colors ml-1 cursor-pointer"
              aria-label="Close routing trace panel"
              title="Close panel"
            >
              <X className="w-5 h-5 sm:w-4 sm:h-4" />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 sm:space-y-5">
          {!trace ? (
            <div className="h-full min-h-[300px] flex flex-col items-center justify-center text-center p-6 text-stone-400 space-y-3">
              <div className="p-3 rounded-2xl bg-white border border-stone-200 shadow-xs">
                <Activity className="w-6 h-6 text-stone-400" />
              </div>
              <div>
                <p className="text-sm font-medium text-stone-600">No Trace Recorded Yet</p>
                <p className="text-xs text-stone-500 mt-1 max-w-xs">
                  Ask a question to observe routing across Cache, SQL, Vector, or LLM pipelines.
                </p>
              </div>
            </div>
          ) : activeTab === "json" ? (
            /* JSON Inspection View */
            <div className="space-y-2">
              <div className="flex items-center justify-between text-xs text-stone-500">
                <span className="font-mono text-[11px]">raw_trace_payload.json</span>
                <button
                  type="button"
                  onClick={() => navigator.clipboard.writeText(JSON.stringify(trace, null, 2))}
                  className="text-amber-900 hover:text-amber-700 text-[11px] flex items-center gap-1 cursor-pointer font-medium"
                >
                  <Copy className="w-3 h-3" />
                  Copy JSON
                </button>
              </div>
              <pre className="p-3 rounded-xl bg-stone-900 border border-stone-700 text-[11px] font-mono text-[#8FB08A] overflow-x-auto max-h-[550px] leading-relaxed select-all shadow-xs">
                {JSON.stringify(trace, null, 2)}
              </pre>
            </div>
          ) : (
            /* Visual Pipeline Flow */
            <>
              {/* Top Summary Bar */}
              <div className="p-3.5 rounded-xl bg-white border border-stone-200 shadow-xs flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-wider text-stone-500">
                    Resolved Route
                  </span>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span
                      className={cn(
                        "text-xs font-semibold px-2 py-0.5 rounded-md border uppercase tracking-wider font-mono",
                        activePathConfig.accent.badge
                      )}
                    >
                      {activePathConfig.id}
                    </span>
                    <span className="text-xs text-stone-800 font-medium">
                      {activePathConfig.name}
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold tracking-wider text-stone-500">
                    Latency
                  </span>
                  <div className="flex items-center gap-1.5 mt-0.5 justify-end text-xs font-mono font-semibold text-stone-800">
                    <Clock className="w-3.5 h-3.5 text-amber-800" />
                    <span>{trace.latencyMs} ms</span>
                  </div>
                </div>
              </div>

              {/* Interactive Neural LLM Mode Control Bar */}
              <div className="p-3 rounded-xl bg-amber-50/70 border border-amber-200/90 shadow-xs space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-amber-100 text-amber-900 border border-amber-200">
                      <Cpu className={cn("w-4 h-4", useLlm ? "animate-pulse text-amber-800" : "text-stone-400")} />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-stone-900 flex items-center gap-1.5">
                        <span>Generative LLM Engine</span>
                        <span className={cn("text-[9px] px-1.5 py-0.2 rounded font-mono font-semibold uppercase", useLlm ? "bg-emerald-100 text-emerald-800 border border-emerald-300" : "bg-stone-200 text-stone-600")}>
                          {useLlm ? "Enabled" : "Disabled"}
                        </span>
                      </div>
                      <p className="text-[10px] text-stone-500 mt-0.5">
                        {useLlm
                          ? "SLM/LLM synthesizes natural responses from grounded citations."
                          : "Verbatim extracts & raw SQL records only (no LLM inference)."}
                      </p>
                    </div>
                  </div>

                  {onToggleLlm && (
                    <button
                      type="button"
                      onClick={onToggleLlm}
                      className={cn(
                        "px-3 py-1 rounded-lg text-xs font-semibold border cursor-pointer select-none transition-all shadow-xs",
                        useLlm
                          ? "bg-amber-800 hover:bg-amber-900 text-white border-amber-950"
                          : "bg-white hover:bg-stone-100 text-stone-700 border-stone-300"
                      )}
                    >
                      {useLlm ? "Turn OFF" : "Turn ON"}
                    </button>
                  )}
                </div>
              </div>

              {/* Path Selection Architecture Grid */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-stone-700">
                    Routing Graph Selection
                  </span>
                  <span className="text-[10px] text-stone-500">Click any path for details</span>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  {paths.map((p) => {
                    const isLlmPath = p.id === "llm";
                    const isActive = currentPath === p.id;
                    const Icon = p.icon;

                    return (
                      <button
                        type="button"
                        key={p.id}
                        onClick={() => {
                          if (isLlmPath && onToggleLlm) {
                            onToggleLlm();
                          }
                        }}
                        title={isLlmPath ? `Click to toggle LLM synthesis ${useLlm ? "OFF" : "ON"}` : `${p.name}: ${p.description}`}
                        className={cn(
                          "relative p-3 rounded-xl border transition-all duration-150 flex flex-col justify-between shadow-xs text-left cursor-pointer",
                          isActive
                            ? cn("bg-white", p.accent.activeBorder, p.accent.glow, "ring-1", p.accent.activeBorder)
                            : isLlmPath && useLlm
                            ? "bg-amber-50/50 border-amber-300 hover:bg-amber-50"
                            : "bg-white/60 border-stone-200 opacity-70 hover:opacity-100 hover:border-stone-400"
                        )}
                      >
                        <div className="flex items-center justify-between">
                          <div
                            className={cn(
                              "p-1.5 rounded-lg border",
                              isActive
                                ? cn(p.accent.activeBg, p.accent.activeBorder, p.accent.activeText)
                                : isLlmPath && useLlm
                                ? "bg-amber-100 text-amber-900 border-amber-300"
                                : "bg-stone-100 text-stone-400 border-transparent"
                            )}
                          >
                            <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                          </div>
                          {isActive && (
                            <span
                              className="w-2 h-2 rounded-full animate-ping"
                              style={{ backgroundColor: p.accent.dot }}
                            />
                          )}
                          {isLlmPath && (
                            <span className={cn("text-[9px] font-mono px-1 py-0.2 rounded font-semibold", useLlm ? "bg-amber-200 text-amber-900" : "bg-stone-100 text-stone-400")}>
                              {useLlm ? "ACTIVE" : "CLICK"}
                            </span>
                          )}
                        </div>

                        <div className="mt-2">
                          <div
                            className={cn(
                              "text-xs font-bold",
                              isActive || (isLlmPath && useLlm) ? "text-stone-900" : "text-stone-500"
                            )}
                          >
                            {p.name}
                          </div>
                          <div className="text-[10px] text-stone-500 truncate mt-0.5">
                            {isLlmPath ? (useLlm ? "Neural Synthesis ON" : "Generative Model (Click)") : p.tag}
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Decision Reasoning */}
              <div className="p-3.5 rounded-xl bg-white border border-stone-200 shadow-xs space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-stone-700">
                  <Sparkles className="w-3.5 h-3.5 text-amber-800" />
                  <span>Decision Reasoning</span>
                </div>
                <p className="text-xs text-stone-700 leading-relaxed font-sans">
                  {trace.decisionReason}
                </p>
              </div>

              {/* Path Specific Metrics / Payloads */}
              {currentPath === "cache" && (
                <div className="p-3.5 rounded-xl bg-[#EEF2E6] border border-[#B9CBAE] shadow-xs space-y-2">
                  <div className="flex items-center justify-between text-xs text-[#3F5B3D] font-semibold">
                    <div className="flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5" />
                      <span>L1 Semantic Cache Hit</span>
                    </div>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#DCE6D5] text-[#3F5B3D] font-mono">
                      HIT
                    </span>
                  </div>
                  <div className="text-[11px] font-mono text-stone-700 break-all space-y-1">
                    <p className="text-stone-500">
                      Key: <span className="text-[#3F5B3D]">{trace.cacheKey}</span>
                    </p>
                    <p className="text-stone-500">
                      Timestamp: <span className="text-stone-700">{trace.cachedAt}</span>
                    </p>
                  </div>
                </div>
              )}

              {currentPath === "sql" && (
                <div className="p-3.5 rounded-xl bg-[#EAF0F7] border border-[#B9CEE3] shadow-xs space-y-2.5">
                  <div className="flex items-center justify-between text-xs text-[#0F1F38] font-semibold">
                    <div className="flex items-center gap-1.5">
                      <Code2 className="w-3.5 h-3.5" />
                      <span>Compiled SQL Query</span>
                    </div>
                    <button
                      type="button"
                      onClick={handleCopySql}
                      className="p-1 rounded hover:bg-[#D6E2EE] text-[#0F1F38] transition-colors cursor-pointer"
                      title="Copy SQL Query"
                    >
                      {copiedQuery ? <Check className="w-3 h-3 text-[#3F5B3D]" /> : <Copy className="w-3 h-3" />}
                    </button>
                  </div>

                  {trace.sqlQuery && (
                    <pre className="p-2.5 rounded-lg bg-stone-900 border border-[#B9CEE3] text-[11px] font-mono text-[#A9C4DE] overflow-x-auto leading-relaxed shadow-xs">
                      {trace.sqlQuery}
                    </pre>
                  )}

                  {trace.tablesAccessed && (
                    <div className="flex items-center gap-1.5 text-[11px] text-stone-600">
                      <Table className="w-3 h-3 text-[#0F1F38]" />
                      <span>Tables:</span>
                      <div className="flex flex-wrap gap-1">
                        {trace.tablesAccessed.map((tbl) => (
                          <span
                            key={tbl}
                            className="px-1.5 py-0.2 rounded bg-stone-100 text-stone-700 font-mono text-[10px]"
                          >
                            {tbl}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {currentPath === "vector" && (
                <div className="p-3.5 rounded-xl bg-[#F3ECEF] border border-[#D9C2D4] shadow-xs space-y-2">
                  <div className="flex items-center justify-between text-xs text-[#5B3A52] font-semibold">
                    <div className="flex items-center gap-1.5">
                      <Search className="w-3.5 h-3.5" />
                      <span>Hybrid Vector Search</span>
                    </div>
                    <span className="text-[10px] font-mono text-[#5B3A52]">
                      Top-K: {trace.topK || 3}
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                    <div className="p-2 rounded-lg bg-white border border-stone-200 shadow-xs">
                      <span className="text-stone-500 block text-[10px]">Index:</span>
                      <span className="text-[#5B3A52] truncate block">{trace.indexName}</span>
                    </div>
                    <div className="p-2 rounded-lg bg-white border border-stone-200 shadow-xs">
                      <span className="text-stone-500 block text-[10px]">Cosine Similarity:</span>
                      <span className="text-[#3F5B3D] font-bold">
                        {trace.vectorSimilarity ? (trace.vectorSimilarity * 100).toFixed(1) + "%" : "N/A"}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {currentPath === "llm" && (
                <div className="p-3.5 rounded-xl bg-[#EFEDE9] border border-[#D6D0C8] shadow-xs space-y-2">
                  <div className="flex items-center justify-between text-xs text-[#3F3B36] font-semibold">
                    <div className="flex items-center gap-1.5">
                      <Cpu className="w-3.5 h-3.5" />
                      <span>LLM Synthesis &amp; Fallback</span>
                    </div>
                    <span className="text-[10px] font-mono text-[#5C574F]">
                      {trace.model || "gpt-4o-mini"}
                    </span>
                  </div>
                  {trace.tokensUsed && (
                    <div className="grid grid-cols-3 gap-1.5 text-center font-mono text-[10px]">
                      <div className="p-1.5 rounded bg-stone-900 border border-stone-700 shadow-xs">
                        <span className="text-stone-400 block">Prompt</span>
                        <span className="text-stone-100 font-semibold">{trace.tokensUsed.prompt}</span>
                      </div>
                      <div className="p-1.5 rounded bg-stone-900 border border-stone-700 shadow-xs">
                        <span className="text-stone-400 block">Completion</span>
                        <span className="text-stone-100 font-semibold">{trace.tokensUsed.completion}</span>
                      </div>
                      <div className="p-1.5 rounded bg-stone-900 border border-stone-700 shadow-xs">
                        <span className="text-stone-400 block">Total</span>
                        <span className="text-amber-500 font-bold">{trace.tokensUsed.total}</span>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Waterfall Execution Steps */}
              {trace.steps && trace.steps.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-stone-700">
                    <div className="flex items-center gap-1.5">
                      <Layers className="w-3.5 h-3.5 text-amber-800" />
                      <span>Execution Waterfall</span>
                    </div>
                    <span className="text-[10px] text-stone-500 font-mono">
                      {trace.steps.length} stages
                    </span>
                  </div>

                  <div className="space-y-1.5">
                    {trace.steps.map((step, idx) => (
                      <div
                        key={idx}
                        className="p-2.5 rounded-lg bg-white border border-stone-200 flex items-center justify-between text-xs shadow-xs"
                      >
                        <div className="flex items-center gap-2 min-w-0">
                          <CheckCircle2
                            className={cn(
                              "w-3.5 h-3.5 shrink-0",
                              step.status === "completed"
                                ? "text-[#3F5B3D]"
                                : step.status === "fallback"
                                  ? "text-amber-700"
                                  : "text-stone-400"
                            )}
                          />
                          <div className="min-w-0">
                            <span className="font-medium text-stone-800 block truncate">
                              {step.name}
                            </span>
                            {step.details && (
                              <span className="text-[10px] text-stone-500 block truncate">
                                {step.details}
                              </span>
                            )}
                          </div>
                        </div>

                        <span className="font-mono text-[10px] text-stone-500 shrink-0 ml-2">
                          {step.latencyMs}ms
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </aside>
    </>
  );
}
