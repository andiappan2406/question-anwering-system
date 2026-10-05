"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Activity,
  Trash2,
  Zap,
  Database,
  Search,
  Cpu,
  GraduationCap,
  ShieldCheck,
  Briefcase,
} from "lucide-react";
import { RoleToggle } from "./RoleToggle";
import { StudentIDPicker } from "./StudentIDPicker";
import { DatabaseHealthStatus, RoutingPath, UserRole } from "@/types/chat";
import { cn } from "@/lib/utils";


interface HeaderProps {
  currentRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  userId: string;
  onStudentIdChange?: (id: string) => void;
  availableStudentIds?: string[];
  lastRoutingPath?: RoutingPath | null;
  lastLatencyMs?: number | null;
  isTraceOpen: boolean;
  onToggleTrace: () => void;
  onClearChat: () => void;
  messageCount: number;
  useLlm?: boolean;
  onToggleLlm?: () => void;
  onOpenPlacementMatcher?: () => void;
}

export function Header({
  currentRole,
  onRoleChange,
  userId,
  onStudentIdChange,
  availableStudentIds,
  lastRoutingPath,
  lastLatencyMs,
  isTraceOpen,
  onToggleTrace,
  onClearChat,
  messageCount,
  useLlm = true,
  onToggleLlm,
  onOpenPlacementMatcher,
}: HeaderProps) {
  const getPathBadge = (path: RoutingPath) => {
    switch (path) {
      case "cache":
        return {
          icon: Zap,
          label: "Cache",
          classes: "bg-emerald-50 text-emerald-800 border-emerald-300",
        };
      case "sql":
        return {
          icon: Database,
          label: "SQL DB",
          classes: "bg-blue-50 text-[#0F1F38] border-blue-200",
        };
      case "vector":
        return {
          icon: Search,
          label: "Vector",
          classes: "bg-violet-50 text-violet-800 border-violet-300",
        };
      case "llm":
        return {
          icon: Cpu,
          label: "LLM",
          classes: "bg-amber-50 text-amber-900 border-amber-300",
        };
      default:
        return null;
    }
  };

  const pathBadge = lastRoutingPath ? getPathBadge(lastRoutingPath) : null;
  const isStudent = currentRole === "student";

  const [dbStatus, setDbStatus] = useState<DatabaseHealthStatus | null>(null);
  const [showDbDetails, setShowDbDetails] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    const fetchDbStatus = async () => {
      try {
        const res = await fetch("/api/v1/database/status");
        if (res.ok) {
          const data = await res.json();
          if (isMounted) setDbStatus(data);
        }
      } catch {
        // Backend may still be initializing
      }
    };
    fetchDbStatus();
    const interval = setInterval(fetchDbStatus, 20000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-stone-200 bg-[#FAF8F5]/95 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-3 sm:px-6">
        {/* Main Row */}
        <div className="h-14 sm:h-16 flex items-center justify-between gap-2 sm:gap-4">
          {/* Branding */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            <div className="relative flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-amber-50 shadow-xs border border-stone-300">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-amber-900" />
              <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 sm:w-2.5 sm:h-2.5 rounded-full bg-emerald-600 border-2 border-[#FAF8F5]" />
            </div>
            <div>
              <div className="flex items-center gap-1.5 sm:gap-2">
                <span className="font-serif font-bold text-sm sm:text-base tracking-tight text-stone-900 flex items-center gap-1">
                  Amypo <span className="text-amber-900 font-medium">Q&A</span>
                </span>
                <span className="text-[9px] sm:text-[10px] font-mono font-medium px-1.5 py-0.2 rounded bg-amber-50 text-amber-900 border border-amber-300 hidden sm:inline-block">
                  v1.0
                </span>
              </div>
              <p className="text-[11px] text-stone-600 hidden md:block">
                Multi-Route Institutional Intelligence &amp; Verification
              </p>
            </div>
          </div>

          {/* Center: Role Switcher & Student ID Picker (Tablet/Desktop) */}
          <div className="flex items-center justify-center">
            <RoleToggle
              currentRole={currentRole}
              onRoleChange={onRoleChange}
              userId={userId}
              onStudentIdChange={onStudentIdChange}
              availableStudentIds={availableStudentIds}
              showIdPicker={true}
            />
          </div>

          {/* Right Actions: Database Status, Routing Trace Toggle, LLM Switch & Clear */}
          <div className="flex items-center gap-1.5 sm:gap-2 shrink-0">
            {/* Live Versatile Database Indicator */}
            <div className="relative hidden lg:flex items-center">
              <button
                type="button"
                onClick={() => setShowDbDetails(!showDbDetails)}
                title={
                  dbStatus?.connected
                    ? `Active DB: ${dbStatus.engine} (${dbStatus.total_records} records, ${dbStatus.latency_ms}ms)`
                    : "Connecting to Database..."
                }
                className={cn(
                  "flex items-center gap-1.5 px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl border text-xs font-medium shadow-xs transition-all cursor-pointer select-none",
                  dbStatus?.connected
                    ? "bg-emerald-50/80 text-emerald-950 border-emerald-300 hover:bg-emerald-100/70"
                    : "bg-white text-stone-600 border-stone-300 hover:bg-stone-50"
                )}
              >
                <div className="relative flex items-center justify-center">
                  <Database className={cn("w-3.5 h-3.5", dbStatus?.connected ? "text-emerald-700" : "text-stone-500")} />
                  <span
                    className={cn(
                      "absolute -bottom-0.5 -right-0.5 w-1.5 h-1.5 rounded-full",
                      dbStatus?.connected ? "bg-emerald-500 animate-pulse" : "bg-amber-400"
                    )}
                  />
                </div>
                <span className="font-mono text-[10px] sm:text-[11px] font-semibold text-stone-800">
                  {dbStatus?.is_cloud_hosted ? "Supabase Postgres" : (dbStatus?.dialect || "PostgreSQL")}
                </span>
                {dbStatus?.connected && (
                  <span className="text-[10px] font-mono text-emerald-700 font-medium">
                    {Math.round(dbStatus.latency_ms)}ms
                  </span>
                )}
              </button>

              {/* Dropdown details popup */}
              {showDbDetails && dbStatus && (
                <div className="absolute right-0 top-full mt-2 w-72 rounded-2xl bg-white border border-stone-200 shadow-xl p-3 z-50 text-xs text-stone-700">
                  <div className="flex items-center justify-between pb-2 border-b border-stone-100">
                    <span className="font-bold text-stone-900 flex items-center gap-1.5">
                      <Database className="w-3.5 h-3.5 text-emerald-600" />
                      Active Database
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase">
                      {dbStatus.dialect}
                    </span>
                  </div>
                  <div className="mt-2 space-y-1.5 font-mono text-[11px]">
                    <div className="flex justify-between text-stone-600">
                      <span>Engine:</span>
                      <span className="font-medium text-stone-900 truncate max-w-[170px]" title={dbStatus.engine}>
                        {dbStatus.engine}
                      </span>
                    </div>
                    <div className="flex justify-between text-stone-600">
                      <span>Host:</span>
                      <span className="font-medium text-stone-900 truncate max-w-[170px]" title={dbStatus.host || ""}>
                        {dbStatus.host || "Local"}
                      </span>
                    </div>
                    <div className="flex justify-between text-stone-600">
                      <span>Database:</span>
                      <span className="font-medium text-stone-900">{dbStatus.database_name}</span>
                    </div>
                    <div className="flex justify-between text-stone-600">
                      <span>Latency:</span>
                      <span className="font-medium text-emerald-600">{dbStatus.latency_ms} ms</span>
                    </div>
                    <div className="flex justify-between text-stone-600">
                      <span>Total Records:</span>
                      <span className="font-semibold text-stone-900">{dbStatus.total_records} rows</span>
                    </div>
                    <div className="pt-1.5 border-t border-stone-100 text-[10px] text-stone-500">
                      Active tables: {dbStatus.active_tables.slice(0, 4).join(", ")} + {dbStatus.active_tables.length - 4} more
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Smart Role Matcher & Student Recommender Button */}
            {onOpenPlacementMatcher && (
              <button
                type="button"
                onClick={onOpenPlacementMatcher}
                aria-label="Open Smart Role Matcher & Candidate Suggestion"
                title="Open Smart Placement Matcher & Skill-to-Role Candidate Suggestion"
                className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-xl border border-amber-300 bg-amber-50 hover:bg-amber-100 text-amber-950 text-xs font-semibold shadow-xs transition-all duration-150 cursor-pointer select-none"
              >
                <Briefcase className="w-3.5 h-3.5 text-amber-800 shrink-0" />
                <span className="hidden sm:inline">Role Matcher</span>
                <span className="px-1.5 py-0.2 rounded-full text-[9px] bg-amber-200 text-amber-900 font-bold uppercase tracking-wider">
                  Match
                </span>
              </button>
            )}

            {/* LLM Synthesis Toggle Button */}
            {onToggleLlm && (
              <button
                type="button"
                onClick={onToggleLlm}
                aria-label="Toggle Neural LLM Generative Synthesis"
                title={`Generative LLM is currently ${useLlm ? "ON (generates synthesized answers)" : "OFF (verbatim citations)"}. Click to toggle.`}
                className={cn(
                  "flex items-center gap-1.5 px-2 sm:px-2.5 py-1 sm:py-1.5 rounded-xl border text-xs font-medium transition-all duration-150 cursor-pointer select-none shadow-xs",
                  useLlm
                    ? "bg-amber-100/90 text-amber-950 border-amber-400 ring-2 ring-amber-200"
                    : "bg-white text-stone-500 hover:text-stone-800 border-stone-300 hover:border-stone-400"
                )}
              >
                <Cpu className={cn("w-3.5 h-3.5 shrink-0", useLlm ? "text-amber-800 animate-pulse" : "text-stone-400")} />
                <span className="font-mono text-[11px] font-semibold flex items-center gap-1">
                  <span>LLM</span>
                  <span className={cn("text-[9px] px-1 py-0.2 rounded font-bold uppercase", useLlm ? "bg-amber-800 text-white" : "bg-stone-200 text-stone-600")}>
                    {useLlm ? "ON" : "OFF"}
                  </span>
                </span>
              </button>
            )}

            {/* Last Route Pill & Side Panel Toggle */}
            <button
              type="button"
              onClick={onToggleTrace}
              aria-label="Toggle Routing Trace panel"
              title="Toggle Routing Trace panel"
              className={cn(
                "flex items-center gap-1.5 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-xl border text-xs font-medium transition-all duration-150 cursor-pointer select-none",
                isTraceOpen
                  ? "bg-amber-50 text-amber-900 border-amber-400 shadow-xs"
                  : "bg-white text-stone-600 hover:text-stone-900 border-stone-300 hover:border-stone-400 shadow-xs"
              )}
            >
              <Activity className={cn("w-3.5 h-3.5 shrink-0", isTraceOpen ? "text-amber-900" : "text-amber-800")} />
              <span className="hidden sm:inline">Trace</span>

              {pathBadge && (
                <span
                  className={cn(
                    "hidden lg:flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono border",
                    pathBadge.classes
                  )}
                >
                  <pathBadge.icon className="w-2.5 h-2.5" />
                  <span>{pathBadge.label}</span>
                  {lastLatencyMs !== undefined && lastLatencyMs !== null && (
                    <span className="opacity-75">{lastLatencyMs}ms</span>
                  )}
                </span>
              )}
            </button>

            {/* Clear conversation button */}
            {messageCount > 0 && (
              <button
                type="button"
                onClick={onClearChat}
                aria-label="Clear chat messages"
                title="Reset conversation"
                className="p-1.5 sm:p-2 rounded-xl text-stone-500 hover:text-[#7A3B36] hover:bg-[#F5E9E8] border border-transparent hover:border-[#E0BEB9] transition-all cursor-pointer shadow-xs"
              >
                <Trash2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Mobile Sub-Bar (< md): Searchable Student ID Picker or Staff ID Badge */}
        <div className="md:hidden pb-2.5 pt-0.5 border-t border-stone-200/60 flex items-center justify-between gap-2 text-xs">
          <div className="flex items-center gap-1.5 text-stone-500 text-[11px]">
            {isStudent ? (
              <GraduationCap className="w-3.5 h-3.5 text-amber-900" />
            ) : (
              <ShieldCheck className="w-3.5 h-3.5 text-[#0F1F38]" />
            )}
            <span>Active Persona:</span>
          </div>

          <div className="flex items-center gap-2">
            {isStudent ? (
              <StudentIDPicker
                value={userId}
                onChange={(newId) => onStudentIdChange?.(newId)}
                availableIds={availableStudentIds}
                compact={true}
              />
            ) : (
              <span className="px-2 py-1 rounded-lg bg-stone-100 border border-stone-300 font-mono text-[11px] font-semibold text-stone-800">
                {userId}
              </span>
            )}

            {pathBadge && (
              <span
                className={cn(
                  "flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-mono border",
                  pathBadge.classes
                )}
              >
                <pathBadge.icon className="w-2.5 h-2.5" />
                <span>{pathBadge.label}</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
