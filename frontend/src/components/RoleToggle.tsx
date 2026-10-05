"use client";

import React from "react";
import { GraduationCap, ShieldCheck } from "lucide-react";
import { UserRole } from "@/types/chat";
import { cn } from "@/lib/utils";
import { StudentIDPicker } from "./StudentIDPicker";

interface RoleToggleProps {
  currentRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  userId: string;
  onStudentIdChange?: (id: string) => void;
  availableStudentIds?: string[];
  showIdPicker?: boolean;
}

export function RoleToggle({
  currentRole,
  onRoleChange,
  userId,
  onStudentIdChange,
  availableStudentIds,
  showIdPicker = true,
}: RoleToggleProps) {
  const isStudent = currentRole === "student";

  return (
    <div className="flex items-center gap-2">
      {/* Role Switcher Pill */}
      <div className="bg-white p-0.5 sm:p-1 rounded-xl border border-stone-300 flex items-center shadow-xs">
        <button
          type="button"
          onClick={() => onRoleChange("student")}
          aria-label="Switch to Student role"
          className={cn(
            "flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer select-none",
            isStudent
              ? "bg-amber-900 text-white shadow-xs"
              : "text-stone-500 hover:text-stone-800 hover:bg-stone-100"
          )}
        >
          <GraduationCap className="w-3.5 h-3.5 shrink-0" />
          <span>Student</span>
        </button>

        <button
          type="button"
          onClick={() => onRoleChange("staff")}
          aria-label="Switch to Staff role"
          className={cn(
            "flex items-center gap-1 sm:gap-1.5 px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-xs font-semibold transition-all duration-150 cursor-pointer select-none",
            !isStudent
              ? "bg-[#0F1F38] text-white shadow-xs"
              : "text-stone-500 hover:text-stone-800 hover:bg-stone-100"
          )}
        >
          <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
          <span className="hidden sm:inline">Staff / Faculty</span>
          <span className="sm:hidden">Staff</span>
        </button>
      </div>

      {/* User ID Section: Searchable Combobox for Student, Static Chip for Staff */}
      {showIdPicker && (
        <div className="hidden md:flex items-center">
          {isStudent ? (
            <StudentIDPicker
              value={userId}
              onChange={(newId) => onStudentIdChange?.(newId)}
              availableIds={availableStudentIds}
            />
          ) : (
            <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-stone-50 border border-stone-300 text-xs font-mono text-stone-600 shadow-xs">
              <ShieldCheck className="w-3.5 h-3.5 text-[#0F1F38] shrink-0" />
              <span className="text-stone-400">ID:</span>
              <span className="text-stone-800 font-semibold">{userId}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
