"use client";

import React, { useState } from "react";
import {
  ChevronDown,
  Copy,
  Check,
  Layers,
  Database,
  BookOpen,
} from "lucide-react";
import { SourceCitation } from "@/types/chat";
import { cn } from "@/lib/utils";

interface SourceCitationChipProps {
  sources: SourceCitation[];
  className?: string;
}

export function SourceCitationChip({ sources, className }: SourceCitationChipProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (!sources || sources.length === 0) return null;

  const handleCopySnippet = (snippet: string, recordId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(snippet);
    setCopiedId(recordId);
    setTimeout(() => setCopiedId(null), 1800);
  };

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  return (
    <div className={cn("mt-3 pt-3 border-t border-stone-100 space-y-2", className)}>
      <div className="flex items-center gap-2 text-xs font-medium text-stone-500">
        <Layers className="w-3.5 h-3.5 text-amber-800" />
        <span>Source Citations ({sources.length}):</span>
      </div>

      <div className="flex flex-col gap-2">
        {sources.map((source, index) => {
          const isExpanded = expandedIndex === index;
          const isCopied = copiedId === source.record_id;

          return (
            <div
              key={`${source.record_id}-${index}`}
              className={cn(
                "rounded-xl border transition-all duration-200 overflow-hidden",
                isExpanded
                  ? "bg-white border-amber-300 shadow-sm"
                  : "bg-stone-50 border-stone-200 hover:border-stone-300 hover:bg-white"
              )}
            >
              {/* Chip header / Trigger */}
              <button
                type="button"
                onClick={() => toggleExpand(index)}
                className="w-full px-3 py-2 text-left flex items-center justify-between gap-3 text-xs cursor-pointer select-none transition-colors"
                aria-expanded={isExpanded}
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div className="p-1 rounded-md bg-amber-50 text-amber-900 shrink-0">
                    {source.record_id.startsWith("sql") || source.record_id.startsWith("student") ? (
                      <Database className="w-3.5 h-3.5" />
                    ) : (
                      <BookOpen className="w-3.5 h-3.5" />
                    )}
                  </div>
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="font-mono text-amber-900 font-semibold text-[11px] px-1.5 py-0.5 rounded bg-amber-50 border border-amber-200 shrink-0">
                      {source.record_id}
                    </span>
                    {source.title && (
                      <span className="text-stone-700 truncate text-[11px] font-medium hidden sm:inline">
                        {source.title}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  {source.score !== undefined && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-stone-100 text-stone-600 font-mono">
                      {(source.score * 100).toFixed(0)}% match
                    </span>
                  )}
                  <div
                    className={cn(
                      "p-1 rounded-md text-stone-500 transition-transform duration-200",
                      isExpanded && "rotate-180 text-amber-800"
                    )}
                  >
                    <ChevronDown className="w-3.5 h-3.5" />
                  </div>
                </div>
              </button>

              {/* Expandable Snippet Body */}
              {isExpanded && (
                <div className="px-3 pb-3 pt-1 border-t border-stone-100 space-y-2.5 animate-in slide-in-from-top-1 duration-150">
                  {source.title && (
                    <div className="text-[11px] font-semibold text-stone-800 sm:hidden">
                      {source.title}
                    </div>
                  )}

                  <div className="relative group/snippet rounded-lg p-2.5 bg-stone-50 border border-stone-200 text-xs text-stone-700 leading-relaxed font-sans font-normal">
                    <p className="font-serif italic text-stone-700">&ldquo;{source.snippet}&rdquo;</p>

                    <button
                      type="button"
                      onClick={(e) => handleCopySnippet(source.snippet, source.record_id, e)}
                      title="Copy citation snippet"
                      className="absolute top-2 right-2 p-1.5 rounded-md bg-white hover:bg-stone-100 text-stone-500 hover:text-stone-800 transition-colors shadow-sm border border-stone-200 cursor-pointer"
                    >
                      {isCopied ? (
                        <Check className="w-3.5 h-3.5 text-emerald-700" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>

                  <div className="flex items-center justify-between text-[10px] text-stone-500 pt-1">
                    <div className="flex items-center gap-1.5">
                      <span className="text-stone-400">Collection:</span>
                      <span className="text-amber-800 font-mono">
                        {source.collection || "institutional_records"}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 font-mono text-stone-400">
                      <span>record_id:</span>
                      <span className="text-stone-700 font-semibold">{source.record_id}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

