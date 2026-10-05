import React, { useState } from 'react';
import { ArrowRight, GraduationCap, Briefcase, Search, CheckCircle2 } from 'lucide-react';
import { UserRole } from '@/types/chat';
import { StudentIDPicker } from './StudentIDPicker';
import { DEFAULT_STUDENT_ID, SAMPLE_STUDENT_IDS } from '@/lib/constants';

interface HeroSectionProps {
    onSelectRole: (role: UserRole, studentId?: string) => void;
    onRunQuickQuery: (query: string, role: UserRole, studentId?: string) => void;
    studentId?: string;
    onStudentIdChange?: (id: string) => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({
    onSelectRole,
    onRunQuickQuery,
    studentId = DEFAULT_STUDENT_ID,
    onStudentIdChange,
}) => {
    const [customInput, setCustomInput] = useState('');
    const [activeRolePreview, setActiveRolePreview] = useState<UserRole>('student');
    const [selectedStudentId, setSelectedStudentId] = useState<string>(studentId);

    const handleStudentIdChange = (newId: string) => {
        setSelectedStudentId(newId);
        onStudentIdChange?.(newId);
    };

    const studentExamples = [
        'What is my current attendance?',
        'Which company roles match my skills best?',
        'What are my technical skills and placement status?',
        'What does Module 3 of DBMS cover?',
    ];

    const staffExamples = [
        'Suggest students for Google SDE role',
        'Suggest students for Zoho Full Stack Developer',
        'Who matches Microsoft Data Scientist opening?',
        'What is the policy for relative grading and exam cutoffs?',
    ];

    const handleSearchSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (customInput.trim()) {
            onRunQuickQuery(
                customInput.trim(),
                activeRolePreview,
                activeRolePreview === 'student' ? selectedStudentId : undefined
            );
        }
    };

    return (
        <section className="relative overflow-hidden border-b border-stone-200/90 bg-[#FAF8F5] pt-8 pb-14 sm:pt-12 sm:pb-20 lg:pt-16 lg:pb-24">
            {/* Subtle paper dot grid background */}
            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(#d6cebe_1px,transparent_1px)] [background-size:24px_24px] opacity-25" />

            <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                {/* Responsive grid: stacks cleanly to 1 column on mobile (< 1024px), 2 columns on desktop */}
                <div className="grid grid-cols-1 items-center gap-10 lg:grid-cols-12 lg:gap-8">
                    {/* Left Column: Headline, Role Cards, Search */}
                    <div className="lg:col-span-7">
                        <div className="mb-3.5 sm:mb-4 flex flex-wrap items-center gap-1.5 sm:gap-2 text-[11px] sm:text-xs font-semibold uppercase tracking-widest text-amber-900">
                            <span className="inline-block h-1.5 w-1.5 rounded-full bg-amber-800" />
                            <span>Institutional Knowledge System</span>
                            <span className="text-stone-400" aria-hidden="true">·</span>
                            <span className="text-stone-600">Self-Hosted Campus Deployment</span>
                        </div>

                        <h1 className="font-serif text-3xl sm:text-5xl lg:text-6xl font-semibold leading-[1.14] tracking-tight text-stone-900 [text-wrap:balance]">
                            Instant, grounded answers across courses, policies, and academic records.
                        </h1>

                        <p className="mt-4 sm:mt-5 max-w-2xl font-sans text-sm sm:text-base lg:text-lg leading-relaxed text-stone-700">
                            Built exclusively for AMYPO. Every answer is synthesized with exact source citations directly on self-hosted campus hardware — <strong className="font-semibold text-stone-900">no external cloud APIs, no data leaving campus, completely confidential.</strong>
                        </p>

                        {/* Role Selection Cards */}
                        <div className="mt-7 sm:mt-8">
                            <div className="mb-3 flex items-center justify-between text-xs font-medium uppercase tracking-wider text-stone-500">
                                <span>Select your institutional role to enter</span>
                                {activeRolePreview === 'student' && (
                                    <span className="hidden sm:inline font-mono text-[11px] text-amber-900 font-semibold lowercase">
                                        Active ID: #{selectedStudentId}
                                    </span>
                                )}
                            </div>

                            <div className="grid grid-cols-1 gap-3.5 sm:grid-cols-2">
                                {/* Student Role Card */}
                                <div
                                    onMouseEnter={() => setActiveRolePreview('student')}
                                    className="group relative flex flex-col justify-between rounded-2xl border-2 border-stone-300 bg-white p-4 sm:p-5 text-left shadow-xs transition-all duration-200 hover:border-amber-800 hover:shadow-md"
                                >
                                    <div className="flex w-full items-center justify-between">
                                        <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-amber-50 text-amber-900 ring-1 ring-amber-200/80">
                                            <GraduationCap className="h-5 w-5" />
                                        </span>
                                        <button
                                            type="button"
                                            suppressHydrationWarning
                                            onClick={() => onSelectRole('student', selectedStudentId)}
                                            className="text-xs font-semibold text-amber-900 group-hover:translate-x-0.5 transition-transform flex items-center gap-1 cursor-pointer py-1 px-2 rounded-lg hover:bg-amber-50"
                                        >
                                            Launch <ArrowRight className="h-3.5 w-3.5" />
                                        </button>
                                    </div>

                                    <div className="mt-3.5 sm:mt-4">
                                        <button
                                            type="button"
                                            suppressHydrationWarning
                                            onClick={() => onSelectRole('student', selectedStudentId)}
                                            className="font-serif text-lg font-semibold text-stone-900 group-hover:text-amber-950 text-left cursor-pointer"
                                        >
                                            Continue as Student
                                        </button>
                                        <p className="mt-1 text-xs text-stone-600 leading-snug">
                                            Attendance, grades, course content, FAQs, and campus policies.
                                        </p>
                                    </div>

                                    {/* Student ID Combobox directly in the card */}
                                    <div className="mt-3 pt-3 border-t border-stone-200/80 flex items-center justify-between gap-2">
                                        <span className="text-[11px] text-stone-500 font-sans">
                                            Student record:
                                        </span>
                                        <StudentIDPicker
                                            value={selectedStudentId}
                                            onChange={handleStudentIdChange}
                                            availableIds={SAMPLE_STUDENT_IDS}
                                            compact={true}
                                        />
                                    </div>
                                </div>

                                {/* Staff Role Card */}
                                <div
                                    onMouseEnter={() => setActiveRolePreview('staff')}
                                    className="group relative flex flex-col justify-between rounded-2xl border-2 border-stone-300 bg-white p-4 sm:p-5 text-left shadow-xs transition-all duration-200 hover:border-[#0F1F38] hover:shadow-md"
                                >
                                    <div className="flex w-full items-center justify-between">
                                        <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-[#0F1F38] ring-1 ring-blue-200/80">
                                            <Briefcase className="h-5 w-5" />
                                        </span>
                                        <button
                                            type="button"
                                            suppressHydrationWarning
                                            onClick={() => onSelectRole('staff')}
                                            className="text-xs font-semibold text-[#0F1F38] group-hover:translate-x-0.5 transition-transform flex items-center gap-1 cursor-pointer py-1 px-2 rounded-lg hover:bg-blue-50"
                                        >
                                            Launch <ArrowRight className="h-3.5 w-3.5" />
                                        </button>
                                    </div>

                                    <div className="mt-3.5 sm:mt-4">
                                        <button
                                            type="button"
                                            suppressHydrationWarning
                                            onClick={() => onSelectRole('staff')}
                                            className="font-serif text-lg font-semibold text-stone-900 group-hover:text-[#0F1F38] text-left cursor-pointer"
                                        >
                                            Continue as Staff / Faculty
                                        </button>
                                        <p className="mt-1 text-xs text-stone-600 leading-snug">
                                            Institutional policies, academic regulations, and procedural documentation.
                                        </p>
                                    </div>

                                    <div className="mt-3 pt-3 border-t border-stone-200/80">
                                        <div className="flex items-center justify-between gap-2 text-[11px] text-stone-500">
                                            <span>Staff Context:</span>
                                            <span className="font-mono text-[10px] font-semibold text-stone-700 bg-stone-100 px-2 py-0.5 rounded border border-stone-200">
                                                Policy Documentation
                                            </span>
                                        </div>
                                        <p className="mt-2 text-[11px] text-stone-500 leading-snug">
                                            Staff role currently supports policy and documentation queries. Personal staff records (leave, attendance) are not yet available in this dataset.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Search Input Box */}
                        <form onSubmit={handleSearchSubmit} className="mt-6 sm:mt-7">
                            <div className="relative flex items-center rounded-xl border border-stone-300 bg-white p-1 sm:p-1.5 shadow-xs focus-within:border-stone-500 focus-within:ring-2 focus-within:ring-stone-200 transition-all">
                                <Search className="ml-2.5 sm:ml-3 h-4 w-4 text-stone-400 shrink-0" />
                                <input
                                    type="text"
                                    suppressHydrationWarning
                                    value={customInput}
                                    onChange={(e) => setCustomInput(e.target.value)}
                                    placeholder={
                                        activeRolePreview === 'student'
                                            ? `Ask as Student #${selectedStudentId} (e.g., "What is my attendance?")...`
                                            : 'Ask an institutional policy question (e.g., "What is the policy for relative grading?")...'
                                    }
                                    className="w-full min-w-0 bg-transparent px-2.5 sm:px-3 py-1.5 sm:py-2 text-xs sm:text-sm text-stone-900 placeholder:text-stone-400 focus:outline-none"
                                />
                                <button
                                    type="submit"
                                    suppressHydrationWarning
                                    className="inline-flex items-center gap-1 sm:gap-1.5 rounded-lg bg-stone-900 px-3 sm:px-4 py-1.5 sm:py-2 text-xs font-medium text-white transition hover:bg-stone-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-stone-600 whitespace-nowrap cursor-pointer shrink-0 shadow-xs"
                                >
                                    <span>Ask</span>
                                    <ArrowRight className="h-3.5 w-3.5" />
                                </button>
                            </div>
                        </form>

                        {/* Quick Inquiries Pills with Polished Editorial Hover State */}
                        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-stone-600">
                            <span className="font-semibold text-stone-800 text-[11px] sm:text-xs">
                                Quick inquiries:
                            </span>
                            {(activeRolePreview === 'student' ? studentExamples : staffExamples).map(
                                (q, idx) => (
                                    <button
                                        key={idx}
                                        type="button"
                                        suppressHydrationWarning
                                        onClick={() =>
                                            onRunQuickQuery(
                                                q,
                                                activeRolePreview,
                                                activeRolePreview === 'student' ? selectedStudentId : undefined
                                            )
                                        }
                                        className="cursor-pointer text-left text-stone-700 bg-white hover:bg-amber-50 hover:text-amber-950 px-2.5 py-1 rounded-lg border border-stone-200/90 hover:border-amber-300 text-[11px] sm:text-xs transition-all duration-150 shadow-xs hover:shadow-sm select-none"
                                    >
                                        &ldquo;{q}&rdquo;
                                    </button>
                                )
                            )}
                        </div>
                    </div>

                    {/* Right Column: Institutional Archival Card (Stacks below on mobile) */}
                    <div className="lg:col-span-5">
                        <div className="relative mx-auto max-w-md rounded-2xl border border-stone-300/80 bg-[#F5F1EA] p-5 sm:p-6 shadow-xs">
                            <div className="flex items-center gap-3.5 sm:gap-4 border-b border-stone-300/70 pb-4 sm:pb-5">
                                <div className="relative h-14 w-14 sm:h-16 sm:w-16 shrink-0 overflow-hidden rounded-full border-2 border-stone-300 bg-stone-100 shadow-inner">
                                    <img
                                        src="/images/amypo_academic_crest_1790436276512.jpg"
                                        alt="Amypo Institutional Academic Crest Insignia"
                                        className="h-full w-full object-cover"
                                        onError={(e) => {
                                            (e.currentTarget as HTMLElement).style.display = 'none';
                                        }}
                                    />
                                </div>
                                <div>
                                    <div className="text-[10px] sm:text-xs font-semibold uppercase tracking-wider text-stone-500">
                                        College Archival Authority
                                    </div>
                                    <div className="font-serif text-lg sm:text-xl font-bold text-stone-900">
                                        Amypo Q&A System
                                    </div>
                                    <div className="text-[11px] sm:text-xs text-stone-600">
                                        Version 1.0 · Self-Hosted Local LLM
                                    </div>
                                </div>
                            </div>

                            <div className="mt-4 sm:mt-5 space-y-3 sm:space-y-3.5 text-xs text-stone-700">
                                <div className="flex items-start gap-2.5">
                                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-700" />
                                    <div>
                                        <span className="font-semibold text-stone-900">Honest When Uncertain:</span>
                                        {' '}The system says &quot;I don&apos;t know&quot; rather than guessing when it lacks a grounded source.
                                    </div>
                                </div>
                                <div className="flex items-start gap-2.5">
                                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-700" />
                                    <div>
                                        <span className="font-semibold text-stone-900">Source Citations Attached:</span>
                                        {' '}Every response includes the exact record it was drawn from, for verification.
                                    </div>
                                </div>
                                <div className="flex items-start gap-2.5">
                                    <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-700" />
                                    <div>
                                        <span className="font-semibold text-stone-900">Zero Cloud Dependency:</span>
                                        {' '}All models and data run entirely on local, self-hosted infrastructure.
                                    </div>
                                </div>
                            </div>

                            <div className="mt-4 text-center font-serif text-xs text-stone-500 italic">
                                Grounded, verifiable answers — built for AMYPO.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
};