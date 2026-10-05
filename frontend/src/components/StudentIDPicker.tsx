"use client";

import React, { useState, useRef, useEffect } from "react";
import { Search, ChevronDown, Check, UserCheck, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { DEFAULT_STUDENT_ID, SAMPLE_STUDENT_IDS } from "@/lib/constants";

export interface StudentIDPickerProps {
  value: string;
  onChange: (id: string) => void;
  availableIds?: string[];
  className?: string;
  compact?: boolean;
}

export function StudentIDPicker({
  value,
  onChange,
  availableIds = SAMPLE_STUDENT_IDS,
  className,
  compact = false,
}: StudentIDPickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightedIndex, setHighlightedIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  // Filter IDs based on search query
  const filteredIds = availableIds.filter((id) =>
    id.toLowerCase().includes(searchQuery.trim().toLowerCase())
  );

  const isCustomInput =
    searchQuery.trim().length > 0 &&
    !filteredIds.some((id) => id.toLowerCase() === searchQuery.trim().toLowerCase());

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  // Focus search input when popover opens
  useEffect(() => {
    if (isOpen) {
      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  const handleOpenToggle = () => {
    if (!isOpen) {
      setSearchQuery("");
      setHighlightedIndex(0);
    }
    setIsOpen((prev) => !prev);
  };

  const handleSelectId = (id: string) => {
    onChange(id);
    setIsOpen(false);
    setSearchQuery("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) {
      if (e.key === "Enter" || e.key === " " || e.key === "ArrowDown") {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    const totalItems = filteredIds.length + (isCustomInput ? 1 : 0);

    if (e.key === "Escape") {
      e.preventDefault();
      setIsOpen(false);
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev + 1 < totalItems ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev - 1 >= 0 ? prev - 1 : totalItems - 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (isCustomInput && highlightedIndex === filteredIds.length) {
        handleSelectId(searchQuery.trim());
      } else if (filteredIds[highlightedIndex]) {
        handleSelectId(filteredIds[highlightedIndex]);
      } else if (searchQuery.trim()) {
        handleSelectId(searchQuery.trim());
      }
    }
  };

  return (
    <div ref={containerRef} className={cn("relative inline-block text-left", className)}>
      {/* Combobox Trigger Button */}
      <button
        type="button"
        suppressHydrationWarning
        onClick={handleOpenToggle}
        onKeyDown={handleKeyDown}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={`Student ID Picker, current value ${value || DEFAULT_STUDENT_ID}`}
        className={cn(
          "group flex items-center justify-between gap-1.5 rounded-xl border border-stone-300 bg-white text-stone-800 transition-all duration-150 shadow-xs hover:border-amber-700/70 hover:shadow-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-800/40 select-none cursor-pointer",
          compact ? "px-2 py-1 text-xs" : "px-2.5 py-1.5 text-xs"
        )}
      >
        <div className="flex items-center gap-1.5 min-w-0">
          <UserCheck className="w-3.5 h-3.5 text-amber-900 shrink-0" />
          <span className="text-stone-500 font-normal">ID:</span>
          <span className="font-mono font-semibold text-stone-900 truncate">
            {value || DEFAULT_STUDENT_ID}
          </span>
        </div>
        <ChevronDown
          className={cn(
            "w-3.5 h-3.5 text-stone-400 transition-transform duration-200 shrink-0 group-hover:text-amber-900",
            isOpen && "rotate-180 text-amber-900"
          )}
        />
      </button>

      {/* Dropdown Popover */}
      {isOpen && (
        <div
          role="dialog"
          aria-label="Select Student ID"
          className="absolute left-0 mt-1.5 w-60 sm:w-64 rounded-xl border border-stone-300 bg-white shadow-xl z-50 overflow-hidden animate-in fade-in-95 zoom-in-95 duration-150"
        >
          {/* Search Input Box */}
          <div className="p-2 border-b border-stone-200 bg-stone-50/80">
            <div className="relative flex items-center">
              <Search className="absolute left-2.5 w-3.5 h-3.5 text-stone-400 pointer-events-none" />
              <input
                ref={inputRef}
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setHighlightedIndex(0);
                }}
                onKeyDown={handleKeyDown}
                placeholder="Search or enter student ID..."
                className="w-full pl-8 pr-7 py-1.5 text-xs font-mono bg-white border border-stone-300 rounded-lg text-stone-900 placeholder:text-stone-400 placeholder:font-sans focus:outline-none focus:border-amber-800 focus:ring-1 focus:ring-amber-800/30"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => {
                    setSearchQuery("");
                    inputRef.current?.focus();
                  }}
                  className="absolute right-2 p-0.5 rounded text-stone-400 hover:text-stone-700"
                >
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>
            <div className="mt-1 px-1 flex items-center justify-between text-[10px] text-stone-500 font-sans">
              <span>OULAD dataset IDs</span>
              <span className="font-mono">{filteredIds.length} found</span>
            </div>
          </div>

          {/* List of IDs */}
          <div
            ref={listRef}
            role="listbox"
            tabIndex={-1}
            className="max-h-52 overflow-y-auto p-1 space-y-0.5"
          >
            {filteredIds.map((id, index) => {
              const isSelected = id === value;
              const isHighlighted = highlightedIndex === index;

              return (
                <div
                  key={id}
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => handleSelectId(id)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={cn(
                    "flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs cursor-pointer transition-colors duration-100",
                    isSelected
                      ? "bg-amber-50 text-amber-950 font-semibold"
                      : isHighlighted
                        ? "bg-stone-100 text-stone-900"
                        : "text-stone-700 hover:bg-stone-50"
                  )}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="font-mono font-medium">{id}</span>
                    {id === DEFAULT_STUDENT_ID && (
                      <span className="text-[9px] px-1 py-0.2 rounded bg-amber-100/80 text-amber-900 font-sans border border-amber-200">
                        Default
                      </span>
                    )}
                  </div>
                  {isSelected && (
                    <Check className="w-3.5 h-3.5 text-amber-900 shrink-0" />
                  )}
                </div>
              );
            })}

            {/* Custom ID Entry option when typed value isn't in static list */}
            {isCustomInput && (
              <div
                role="option"
                aria-selected={value === searchQuery.trim()}
                onClick={() => handleSelectId(searchQuery.trim())}
                onMouseEnter={() => setHighlightedIndex(filteredIds.length)}
                className={cn(
                  "flex items-center justify-between px-2.5 py-2 rounded-lg text-xs cursor-pointer border-t border-stone-200 mt-1 transition-colors",
                  highlightedIndex === filteredIds.length
                    ? "bg-amber-50 text-amber-950"
                    : "hover:bg-amber-50/60 text-stone-800"
                )}
              >
                <div className="flex flex-col min-w-0">
                  <span className="text-[10px] text-stone-500 font-sans">
                    Use custom student ID:
                  </span>
                  <span className="font-mono font-bold text-amber-900 truncate">
                    &quot;{searchQuery.trim()}&quot;
                  </span>
                </div>
                <span className="text-[10px] font-sans px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-200 font-medium shrink-0">
                  Apply
                </span>
              </div>
            )}

            {filteredIds.length === 0 && !isCustomInput && (
              <div className="p-3 text-center text-xs text-stone-500 font-sans">
                No matching student IDs
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}


