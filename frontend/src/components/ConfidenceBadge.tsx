"use client";

import React, { useState } from "react";
import { ShieldCheck, AlertCircle, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  confidence: number; // 0.0 to 1.0
  className?: string;
  showTooltip?: boolean;
}

export function ConfidenceBadge({
  confidence,
  className,
  showTooltip = true,
}: ConfidenceBadgeProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Confidence thresholds:
  // Sage (high) > 0.7
  // Amber (moderate) 0.3 - 0.7
  // Wine (low) < 0.3
  const isHigh = confidence > 0.7;
  const isMedium = confidence >= 0.3 && confidence <= 0.7;
  const isLow = confidence < 0.3;

  const percentage = Math.round(confidence * 100);

  let variantStyles = {
    badge: "bg-[#EEF2E6] text-[#3F5B3D] border-[#B9CBAE] hover:border-[#9EB593]",
    dot: "bg-[#4B6455]",
    label: "High Confidence",
    description: "Verified with high certainty against authoritative records or primary indices.",
    icon: ShieldCheck,
  };

  if (isMedium) {
    variantStyles = {
      badge: "bg-amber-50 text-amber-900 border-amber-300 hover:border-amber-400",
      dot: "bg-amber-700",
      label: "Moderate Confidence",
      description: "Inferred or semantically retrieved. Contains relevant guidelines, though some nuances may vary.",
      icon: AlertCircle,
    };
  } else if (isLow) {
    variantStyles = {
      badge: "bg-[#F5E9E8] text-[#7A3B36] border-[#E0BEB9] hover:border-[#D3A29B]",
      dot: "bg-[#8C4640]",
      label: "Low Confidence",
      description: "Direct match not found; synthesized via generative fallback. We recommend confirming with staff.",
      icon: AlertTriangle,
    };
  }

  const Icon = variantStyles.icon;

  return (
    <div className="relative inline-flex items-center">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        aria-label={`${variantStyles.label}: ${percentage}%`}
        className={cn(
          "group inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border backdrop-blur-md transition-all duration-200 cursor-pointer shadow-sm select-none",
          variantStyles.badge,
          className
        )}
      >
        <span className={cn("w-1.5 h-1.5 rounded-full shrink-0 animate-pulse", variantStyles.dot)} />
        <Icon className="w-3.5 h-3.5 shrink-0" />
        <span className="font-semibold tracking-wide">{percentage}%</span>
        <span className="text-[11px] opacity-80 hidden sm:inline">{variantStyles.label}</span>
      </button>

      {/* Floating explanatory tooltip */}
      {showTooltip && isOpen && (
        <div
          role="tooltip"
          className="absolute bottom-full left-0 mb-2 z-50 w-64 p-3 rounded-xl bg-stone-900/95 border border-stone-700 text-stone-100 text-xs shadow-2xl backdrop-blur-xl animate-in fade-in zoom-in-95 duration-150 pointer-events-none"
        >
          <div className="flex items-center gap-1.5 font-semibold text-white mb-1">
            <Icon className="w-3.5 h-3.5" />
            <span>
              {variantStyles.label} ({percentage}%)
            </span>
          </div>
          <p className="text-stone-300 text-[11px] leading-relaxed">
            {variantStyles.description}
          </p>
          <div className="mt-2 pt-1.5 border-t border-stone-700 flex items-center justify-between text-[10px] text-stone-400 font-mono">
            <span>Score: {confidence.toFixed(3)}</span>
            <span>
              {isHigh ? "> 0.70" : isMedium ? "0.30 – 0.70" : "< 0.30"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

