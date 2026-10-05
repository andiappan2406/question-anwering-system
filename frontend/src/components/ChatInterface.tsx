"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Sparkles,
  GraduationCap,
  ShieldCheck,
  Bot,
  Copy,
  Check,
  Zap,
  Database,
  Search,
  Cpu,
  ArrowUpRight,
  FileCheck2,
  Lock,
} from "lucide-react";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { SourceCitationChip } from "./SourceCitationChip";
import { VoiceMicButton } from "./VoiceMicButton";
import { Message, RoutingPath, UserRole } from "@/types/chat";
import { cn } from "@/lib/utils";

type ContentBlock =
  | { type: "p"; text: string }
  | { type: "ul"; items: string[] }
  | { type: "ol"; items: string[] };

function parseContentToBlocks(content: string): ContentBlock[] {
  const lines = content.split("\n");
  const blocks: ContentBlock[] = [];
  let pendingList: { type: "ul" | "ol"; items: string[] } | null = null;

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      if (pendingList) {
        blocks.push(pendingList);
        pendingList = null;
      }
      continue;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      const itemText = trimmed.slice(2).trim();
      if (!pendingList || pendingList.type !== "ul") {
        if (pendingList) blocks.push(pendingList);
        pendingList = { type: "ul", items: [itemText] };
      } else {
        pendingList.items.push(itemText);
      }
      continue;
    }

    const orderedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (orderedMatch) {
      const itemText = orderedMatch[2].trim();
      if (!pendingList || pendingList.type !== "ol") {
        if (pendingList) blocks.push(pendingList);
        pendingList = { type: "ol", items: [itemText] };
      } else {
        pendingList.items.push(itemText);
      }
      continue;
    }

    if (pendingList) {
      blocks.push(pendingList);
      pendingList = null;
    }
    blocks.push({ type: "p", text: line });
  }

  if (pendingList) {
    blocks.push(pendingList);
  }

  return blocks;
}

function FormattedMessageContent({ content }: { content: string }) {
  const blocks = parseContentToBlocks(content);

  const renderInline = (text: string): React.ReactNode[] => {
    const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
    return parts.map((part, idx) => {
      if (part.startsWith("**") && part.endsWith("**") && part.length > 4) {
        return (
          <strong key={idx} className="font-semibold text-stone-900">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith("*") && part.endsWith("*") && part.length > 2) {
        return (
          <em key={idx} className="italic text-stone-700">
            {part.slice(1, -1)}
          </em>
        );
      }
      if (part.startsWith("`") && part.endsWith("`") && part.length > 2) {
        return (
          <code
            key={idx}
            className="px-1.5 py-0.5 rounded bg-stone-100 text-amber-900 font-mono text-xs border border-stone-200"
          >
            {part.slice(1, -1)}
          </code>
        );
      }
      return part;
    });
  };

  return (
    <div className="space-y-1.5">
      {blocks.map((block, idx) => {
        if (block.type === "ul") {
          return (
            <ul key={idx} className="space-y-1 my-2 text-stone-800 list-disc pl-5">
              {block.items.map((item, i) => (
                <li key={i} className="leading-relaxed">
                  {renderInline(item)}
                </li>
              ))}
            </ul>
          );
        }
        if (block.type === "ol") {
          return (
            <ol key={idx} className="space-y-1 my-2 text-stone-800 list-decimal pl-5">
              {block.items.map((item, i) => (
                <li key={i} className="leading-relaxed">
                  {renderInline(item)}
                </li>
              ))}
            </ol>
          );
        }
        return (
          <p key={idx} className="leading-relaxed">
            {renderInline(block.text)}
          </p>
        );
      })}
    </div>
  );
}

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
  currentRole: UserRole;
  userId: string;
  onSelectTrace: (msg: Message) => void;
  useLlm?: boolean;
  onToggleLlm?: () => void;
}

export function ChatInterface({
  messages,
  isLoading,
  onSendMessage,
  currentRole,
  userId,
  onSelectTrace,
  useLlm = true,
  onToggleLlm,
}: ChatInterfaceProps) {
  const [input, setInput] = useState("");
  const [copiedMsgId, setCopiedMsgId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto scroll to bottom on message update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    setInput((prev) => (prev ? `${prev} ${transcript}` : transcript));
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  const handleCopyText = (content: string, id: string) => {
    navigator.clipboard.writeText(content);
    setCopiedMsgId(id);
    setTimeout(() => setCopiedMsgId(null), 2000);
  };

  // Tightened suggestion prompts tailored by role and route
  const studentSuggestions = [
    {
      label: "Hostel Check-in & Curfew",
      question: "What are the hostel check-in timings and curfew rules?",
      route: "cache",
      badge: "Cache",
      icon: Zap,
    },
    {
      label: "My CSE301 Attendance",
      question: "What is my current attendance percentage in CSE301?",
      route: "sql",
      badge: "SQL DB",
      icon: Database,
    },
    {
      label: "Grading Curve & Cutoffs",
      question: "What is the policy for relative grading and exam cutoffs?",
      route: "vector",
      badge: "Vector",
      icon: Search,
    },
    {
      label: "Capstone Project Guidance",
      question: "Suggest novel ideas for a distributed systems capstone project",
      route: "llm",
      badge: "LLM Fallback",
      icon: Cpu,
    },
  ];

  const staffSuggestions = [
    {
      label: "Faculty Campus Entry Policy",
      question: "What are the campus entry timings and RFID gate policies for faculty?",
      route: "cache",
      badge: "Cache",
      icon: Zap,
    },
    {
      label: "Examination Conduct Rules",
      question: "What are the examination conduct rules for invigilating faculty?",
      route: "vector",
      badge: "Vector",
      icon: Search,
    },
    {
      label: "Grade Moderation Regulations",
      question: "Explain the academic regulations for grade moderation and exam submission deadlines",
      route: "vector",
      badge: "Vector",
      icon: Search,
    },
    {
      label: "Curriculum Revision Rationale",
      question: "Draft a concise rationale for introducing quantum cryptography in the CS curriculum",
      route: "llm",
      badge: "LLM Fallback",
      icon: Cpu,
    },
  ];
  const suggestions = currentRole === "student" ? studentSuggestions : staffSuggestions;

  const getPathIcon = (path: RoutingPath) => {
    switch (path) {
      case "cache":
        return <Zap className="w-3 h-3 text-[#3F5B3D]" />;
      case "sql":
        return <Database className="w-3 h-3 text-[#0F1F38]" />;
      case "vector":
        return <Search className="w-3 h-3 text-[#5B3A52]" />;
      case "llm":
        return <Cpu className="w-3 h-3 text-[#3F3B36]" />;
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#FAF8F5]">
      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto px-3 sm:px-6 py-4 sm:py-6 space-y-4 sm:space-y-6">
        {messages.length === 0 ? (
          /* Empty State / Scannable Onboarding (< 5 seconds) */
          <div className="max-w-3xl mx-auto h-full flex flex-col justify-center items-center text-center py-6 sm:py-10 animate-in fade-in duration-200">
            {/* Header Kicker — matches landing page style */}
            <div className="mb-3 flex flex-wrap items-center justify-center gap-1.5 sm:gap-2 text-[11px] sm:text-xs font-semibold uppercase tracking-widest text-amber-900">
              <span className="inline-block h-1.5 w-1.5 rounded-full bg-amber-800" />
              <span>Institutional Intelligence</span>
              <span className="text-stone-400" aria-hidden="true">·</span>
              <span className="text-stone-600">Self-Hosted Session</span>
            </div>

            <h2 className="font-serif text-2xl sm:text-4xl font-semibold tracking-tight text-stone-900 mb-2 [text-wrap:balance]">
              Amypo Institutional Assistant
            </h2>
            <p className="text-xs sm:text-sm text-stone-600 max-w-lg mb-6 leading-relaxed">
              Instant, verified answers for your courses, records, and policies. Validated via multi-path routing with citations and confidence scoring.
            </p>
            {currentRole === "staff" && (
              <p className="text-[11px] text-stone-500 max-w-lg -mt-4 mb-6 italic">
                Staff role currently supports policy and documentation queries only. Personal staff records are not yet available in this dataset.
              </p>
            )}

            {/* 3 Scannable Visual Pillars */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3 w-full max-w-2xl mb-7 text-left">
              <div className="p-3 rounded-xl bg-white border border-stone-200 shadow-xs flex items-start gap-2.5">
                <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-800 border border-emerald-200 shrink-0">
                  <Zap className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-stone-900">Multi-Route Engine</div>
                  <div className="text-[11px] text-stone-500 leading-tight mt-0.5">
                    Cache (&lt;10ms), SQL DB, Vector Docs &amp; LLM
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-white border border-stone-200 shadow-xs flex items-start gap-2.5">
                <div className="p-1.5 rounded-lg bg-blue-50 text-blue-900 border border-blue-200 shrink-0">
                  <FileCheck2 className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-stone-900">Source Citations</div>
                  <div className="text-[11px] text-stone-500 leading-tight mt-0.5">
                    Grounded with verifiable academic records
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-white border border-stone-200 shadow-xs flex items-start gap-2.5">
                <div className="p-1.5 rounded-lg bg-amber-50 text-amber-900 border border-amber-200 shrink-0">
                  <Lock className="w-4 h-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-stone-900">Campus Private</div>
                  <div className="text-[11px] text-stone-500 leading-tight mt-0.5">
                    100% self-hosted — zero external cloud leaks
                  </div>
                </div>
              </div>
            </div>

            {/* Prompt Starter Pills with Route Badges */}
            <div className="w-full max-w-2xl space-y-2 text-left">
              <div className="flex items-center justify-between px-1">
                <span className="text-xs font-semibold uppercase tracking-wider text-stone-500">
                  Sample Inquiries by Pipeline
                </span>
                <span className="text-[11px] font-mono text-stone-500">
                  Session: <span className="font-semibold text-stone-800">#{userId}</span>
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-2.5">
                {suggestions.map((item, index) => {
                  const Icon = item.icon;
                  return (
                    <button
                      key={index}
                      type="button"
                      onClick={() => onSendMessage(item.question)}
                      className="p-3 rounded-xl bg-white hover:bg-stone-50 border border-stone-300 hover:border-amber-800 text-left transition-all duration-150 group cursor-pointer shadow-xs hover:shadow-sm"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="text-xs font-semibold text-stone-800 group-hover:text-amber-900 transition-colors">
                          {item.label}
                        </span>
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-stone-100 text-stone-600 group-hover:bg-amber-50 group-hover:text-amber-900 transition-colors flex items-center gap-1 border border-stone-200 shrink-0">
                          <Icon className="w-2.5 h-2.5" />
                          {item.badge}
                        </span>
                      </div>
                      <p className="text-[11px] text-stone-600 line-clamp-2 leading-relaxed">
                        {item.question}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          /* Message Stream */
          <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
            {messages.map((message) => {
              const isUser = message.role === "user";

              return (
                <div
                  key={message.id}
                  className={cn(
                    "flex gap-2.5 sm:gap-4 transition-all duration-200 animate-message-fade-in",
                    isUser ? "justify-end" : "justify-start"
                  )}
                >
                  {/* Assistant Avatar */}
                  {!isUser && (
                    <div className="shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-amber-50 flex items-center justify-center text-amber-900 shadow-xs border border-stone-300 mt-1">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  {/* Message Bubble Container */}
                  <div
                    className={cn(
                      "flex flex-col max-w-[92%] sm:max-w-[82%]",
                      isUser ? "items-end" : "items-start"
                    )}
                  >
                    {/* User Bubble */}
                    {isUser ? (
                      <div className="rounded-2xl rounded-tr-sm px-3.5 sm:px-4 py-2.5 sm:py-3 bg-[#1C1917] text-white shadow-xs text-xs sm:text-sm leading-relaxed break-words">
                        <p className="whitespace-pre-wrap">{message.content}</p>
                        <div className="mt-1 flex items-center justify-end gap-1.5 text-[10px] text-stone-300 font-mono">
                          <span suppressHydrationWarning>{message.timestamp}</span>
                        </div>
                      </div>
                    ) : (
                      /* Assistant Bubble */
                      <div className="w-full rounded-2xl rounded-tl-sm p-3.5 sm:p-5 bg-white border border-stone-200 shadow-xs space-y-3 text-stone-800 break-words">
                        {/* Top Metadata Header: Confidence Badge + Route Pill */}
                        <div className="flex flex-wrap items-center justify-between gap-1.5 sm:gap-2 pb-2.5 border-b border-stone-100">
                          <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                            {message.confidence !== undefined && (
                              <ConfidenceBadge confidence={message.confidence} />
                            )}

                            {message.trace?.path && (
                              <button
                                type="button"
                                onClick={() => onSelectTrace(message)}
                                title="Click to inspect routing trace"
                                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-mono font-medium bg-stone-100 hover:bg-amber-50 text-stone-700 hover:text-amber-900 border border-stone-200 hover:border-amber-300 transition-colors cursor-pointer shadow-xs"
                              >
                                {getPathIcon(message.trace.path)}
                                <span className="uppercase">{message.trace.path}</span>
                                {message.trace.latencyMs && (
                                  <span className="text-[10px] text-stone-500">
                                    • {message.trace.latencyMs}ms
                                  </span>
                                )}
                                <ArrowUpRight className="w-3 h-3 ml-0.5 opacity-60" />
                              </button>
                            )}
                          </div>

                          <div className="flex items-center gap-2 text-xs text-stone-500">
                            <span className="text-[10px] font-mono opacity-70" suppressHydrationWarning>
                              {message.timestamp}
                            </span>
                            <button
                              type="button"
                              onClick={() => handleCopyText(message.content, message.id)}
                              className="p-1 rounded-md hover:bg-stone-100 text-stone-500 hover:text-stone-800 transition-colors cursor-pointer"
                              title="Copy answer"
                              aria-label="Copy answer to clipboard"
                            >
                              {copiedMsgId === message.id ? (
                                <Check className="w-3.5 h-3.5 text-emerald-700" />
                              ) : (
                                <Copy className="w-3.5 h-3.5" />
                              )}
                            </button>
                          </div>
                        </div>

                        {/* Answer Body with Formatted Markdown Styling */}
                        <div className="text-xs sm:text-[14.5px] leading-relaxed text-stone-800 font-sans">
                          <FormattedMessageContent content={message.content} />
                        </div>

                        {/* Expandable Source Citation Chip */}
                        {message.sources && message.sources.length > 0 && (
                          <SourceCitationChip sources={message.sources} />
                        )}
                      </div>
                    )}
                  </div>

                  {/* User Avatar */}
                  {isUser && (
                    <div className="shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-stone-100 flex items-center justify-center text-stone-700 border border-stone-300 mt-1 shadow-xs">
                      {currentRole === "student" ? (
                        <GraduationCap className="w-4 h-4 text-amber-900" />
                      ) : (
                        <ShieldCheck className="w-4 h-4 text-[#0F1F38]" />
                      )}
                    </div>
                  )}
                </div>
              );
            })}

            {/* Loading Indicator */}
            {isLoading && (
              <div className="flex gap-2.5 sm:gap-4 items-start animate-message-fade-in">
                <div className="shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-amber-50 text-amber-900 flex items-center justify-center border border-stone-300 shadow-xs">
                  <Bot className="w-4 h-4 animate-spin" />
                </div>
                <div className="p-3 sm:p-4 rounded-2xl rounded-tl-sm bg-white border border-stone-200 text-xs text-stone-600 flex items-center gap-3 shadow-xs">
                  <div className="flex gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-amber-800 animate-bounce [animation-delay:-0.3s]" />
                    <span className="w-2 h-2 rounded-full bg-amber-800 animate-bounce [animation-delay:-0.15s]" />
                    <span className="w-2 h-2 rounded-full bg-amber-800 animate-bounce" />
                  </div>
                  <span className="text-[11px] sm:text-xs">Resolving routing path &amp; citations...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Composer Area */}
      <div className="p-3 sm:p-5 border-t border-stone-200 bg-[#FAF8F5]/95 backdrop-blur-xl shrink-0">
        <div className="max-w-4xl mx-auto space-y-1.5 sm:space-y-2">
          <form
            onSubmit={handleSubmit}
            className="relative flex items-end gap-1.5 sm:gap-2 p-1.5 sm:p-2 rounded-2xl bg-white border border-stone-300 focus-within:border-stone-500 focus-within:ring-2 focus-within:ring-stone-200 transition-all shadow-xs"
          >
            {/* Auto-expanding Textarea */}
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = "auto";
                e.target.style.height = `${Math.min(e.target.scrollHeight, 180)}px`;
              }}
              onKeyDown={handleKeyDown}
              placeholder={`Ask as ${currentRole === "student" ? `Student #${userId}` : "Staff"}... (Enter to send)`}
              rows={1}
              suppressHydrationWarning
              className="flex-1 max-h-36 bg-transparent text-xs sm:text-sm text-stone-900 placeholder:text-stone-400 px-2 sm:px-3 py-1.5 sm:py-2 outline-none resize-none leading-relaxed min-w-0"
            />

            <div className="flex items-center gap-1 sm:gap-1.5 pb-0.5 shrink-0">
              {/* Voice Mic Button */}
              <VoiceMicButton
                onTranscript={handleVoiceTranscript}
                disabled={isLoading}
              />

              {/* Submit Button */}
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                aria-label="Send message"
                suppressHydrationWarning
                className={cn(
                  "p-2 sm:p-2.5 rounded-xl transition-all duration-150 flex items-center justify-center cursor-pointer select-none shadow-xs",
                  input.trim() && !isLoading
                    ? "bg-stone-900 hover:bg-stone-800 text-white"
                    : "bg-stone-100 text-stone-400 border border-stone-200 cursor-not-allowed"
                )}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Quick status line & LLM Toggle */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-1.5 text-[10px] sm:text-[11px] text-stone-500 px-1 font-mono">
            <div className="flex items-center gap-1.5 sm:gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600" />
              <span>Self-Hosted Local Engine</span>
              <span className="hidden sm:inline opacity-70">• FastEmbed + FAISS + Supabase PostgreSQL</span>
            </div>

            {onToggleLlm && (
              <button
                type="button"
                onClick={onToggleLlm}
                title={`Click to switch between Neural Generative Mode and Direct Verbatim Extraction (currently ${useLlm ? "ON" : "OFF"})`}
                className={cn(
                  "flex items-center gap-1.5 px-2 py-0.5 rounded-md border text-[11px] font-sans font-medium transition-all cursor-pointer select-none shadow-xs",
                  useLlm
                    ? "bg-amber-100 text-amber-950 border-amber-300 hover:bg-amber-200 ring-1 ring-amber-300"
                    : "bg-white text-stone-600 border-stone-300 hover:bg-stone-100"
                )}
              >
                <Cpu className={cn("w-3 h-3", useLlm ? "text-amber-800 animate-pulse" : "text-stone-400")} />
                <span>LLM Synthesizer:</span>
                <span className={cn("px-1 py-0.2 rounded text-[10px] font-bold font-mono", useLlm ? "bg-amber-800 text-white" : "bg-stone-200 text-stone-700")}>
                  {useLlm ? "ACTIVE" : "OFF"}
                </span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


