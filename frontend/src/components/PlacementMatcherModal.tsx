"use client";

import React, { useState, useEffect } from "react";
import {
  Briefcase,
  CheckCircle2,
  AlertCircle,
  X,
  Sparkles,
  TrendingUp,
  Building2,
  GraduationCap,
  ArrowRight,
  Filter,
  Search,
  UserCheck,
  ShieldAlert,
  Award,
  Layers,
} from "lucide-react";
import { CompanyOpening, MatchedCandidate, RecommendedOpening } from "@/types/chat";
import { SAMPLE_STUDENT_IDS } from "@/lib/constants";

interface PlacementMatcherModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeStudentId: string;
  onStudentIdChange: (id: string) => void;
  onSelectQuery: (query: string) => void;
}

export function PlacementMatcherModal({
  isOpen,
  onClose,
  activeStudentId,
  onStudentIdChange,
  onSelectQuery,
}: PlacementMatcherModalProps) {
  const [activeTab, setActiveTab] = useState<"recruiter" | "student">("recruiter");
  const [openings, setOpenings] = useState<CompanyOpening[]>([]);
  const [selectedOpeningId, setSelectedOpeningId] = useState<string>("OPN-GOOG-01");
  const [matchedCandidates, setMatchedCandidates] = useState<MatchedCandidate[]>([]);
  const [studentRecommendations, setStudentRecommendations] = useState<RecommendedOpening[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [searchFilter, setSearchFilter] = useState<string>("");

  // Fetch all openings on mount
  useEffect(() => {
    if (!isOpen) return;

    async function fetchOpenings() {
      try {
        const res = await fetch("http://localhost:9000/api/v1/placement/openings");
        if (res.ok) {
          const data = await res.json();
          setOpenings(data.openings || []);
          if (data.openings?.length > 0 && !selectedOpeningId) {
            setSelectedOpeningId(data.openings[0].opening_id);
          }
        }
      } catch {
        // Fallback default static corporate openings
        setOpenings([
          {
            opening_id: "OPN-GOOG-01",
            company_name: "Google",
            role_title: "Backend Software Engineer (SDE-1)",
            required_skills: ["Python", "Go", "Distributed Systems", "Data Structures & Algorithms", "SQL", "System Design"],
            preferred_skills: ["Kubernetes", "gRPC", "Redis", "C++"],
            min_cgpa: 8.5,
            min_attendance: 75.0,
            eligible_departments: ["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science"],
            ctc: "24 LPA",
            location: "Bangalore / Hyderabad",
            positions_open: 6,
            deadline: "2026-11-20",
            description: "Build scalable distributed systems, cloud microservices, and high-performance backend pipelines.",
          },
          {
            opening_id: "OPN-MSFT-02",
            company_name: "Microsoft",
            role_title: "Data Scientist / Applied AI Engineer",
            required_skills: ["Python", "Machine Learning", "Deep Learning", "PyTorch", "NLP", "SQL", "Statistics"],
            preferred_skills: ["Transformers", "Vector Databases", "LangChain", "FastAPI"],
            min_cgpa: 8.0,
            min_attendance: 75.0,
            eligible_departments: ["Artificial Intelligence & Data Science", "Computer Science & Engineering", "Information Technology"],
            ctc: "21 LPA",
            location: "Hyderabad / Bangalore",
            positions_open: 5,
            deadline: "2026-11-22",
            description: "Design production ML pipelines, fine-tune transformer models, and deploy intelligent AI capabilities.",
          },
          {
            opening_id: "OPN-AMZN-03",
            company_name: "Amazon",
            role_title: "Cloud Solutions Architect / DevOps Engineer",
            required_skills: ["AWS", "Linux", "Docker", "Kubernetes", "Python", "Networking", "CI/CD"],
            preferred_skills: ["Terraform", "Ansible", "Prometheus", "Bash Scripting"],
            min_cgpa: 7.5,
            min_attendance: 75.0,
            eligible_departments: ["Computer Science & Engineering", "Information Technology", "Electronics & Communication Engineering"],
            ctc: "18 LPA",
            location: "Chennai / Hyderabad",
            positions_open: 8,
            deadline: "2026-11-25",
            description: "Architect mission-critical cloud infrastructure and automated container deployment pipelines.",
          },
          {
            opening_id: "OPN-ZOHO-04",
            company_name: "Zoho Corporation",
            role_title: "Full Stack Web Developer",
            required_skills: ["React", "TypeScript", "Node.js", "FastAPI", "PostgreSQL", "REST APIs", "CSS"],
            preferred_skills: ["Docker", "Tailwind CSS", "Redis", "Python"],
            min_cgpa: 7.0,
            min_attendance: 70.0,
            eligible_departments: ["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science", "Electronics & Communication Engineering"],
            ctc: "10 LPA",
            location: "Chennai / Tenkasi",
            positions_open: 15,
            deadline: "2026-11-30",
            description: "Develop scalable SaaS cloud applications, reactive user interfaces, and robust backend APIs.",
          },
          {
            opening_id: "OPN-BOSCH-05",
            company_name: "Bosch Global Software",
            role_title: "Embedded Systems & IoT Firmware Engineer",
            required_skills: ["Embedded C", "C++", "Microcontrollers", "RTOS", "IoT Protocols", "CAN Bus", "Circuit Design"],
            preferred_skills: ["ARM Cortex-M", "Verilog", "KiCAD", "MQTT"],
            min_cgpa: 7.5,
            min_attendance: 75.0,
            eligible_departments: ["Electronics & Communication Engineering", "Mechanical Engineering"],
            ctc: "12 LPA",
            location: "Coimbatore / Bangalore",
            positions_open: 10,
            deadline: "2026-12-05",
            description: "Develop automotive firmware, vehicle telemetry systems, and sensor interface software.",
          },
          {
            opening_id: "OPN-LT-06",
            company_name: "Larsen & Toubro (L&T)",
            role_title: "Robotics & Industrial Automation Engineer",
            required_skills: ["Robotics", "CAD/CAM", "PLC Programming", "Industrial Automation", "MATLAB", "SolidWorks"],
            preferred_skills: ["AutoCAD", "Finite Element Analysis", "Python"],
            min_cgpa: 7.0,
            min_attendance: 75.0,
            eligible_departments: ["Mechanical Engineering"],
            ctc: "9.5 LPA",
            location: "Chennai / Mumbai",
            positions_open: 8,
            deadline: "2026-12-10",
            description: "Program robotic cells, automate production machinery, and optimize mechatronic assembly lines.",
          },
          {
            opening_id: "OPN-TCS-07",
            company_name: "TCS Digital",
            role_title: "Cybersecurity Analyst & Systems Engineer",
            required_skills: ["Java", "Python", "Cybersecurity", "Network Protocols", "SQL", "Cryptography"],
            preferred_skills: ["Spring Boot", "Linux", "Penetration Testing Basics"],
            min_cgpa: 7.0,
            min_attendance: 70.0,
            eligible_departments: ["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science", "Electronics & Communication Engineering"],
            ctc: "7.5 LPA",
            location: "Chennai / Pan India",
            positions_open: 25,
            deadline: "2026-12-15",
            description: "Engineer resilient enterprise cryptographic solutions and audit cloud network security.",
          },
          {
            opening_id: "OPN-RAZOR-08",
            company_name: "Razorpay",
            role_title: "Frontend Platform Engineer",
            required_skills: ["JavaScript", "TypeScript", "React", "Next.js", "Web Performance", "Tailwind CSS"],
            preferred_skills: ["GraphQL", "Node.js", "WebSockets", "CSS"],
            min_cgpa: 7.5,
            min_attendance: 75.0,
            eligible_departments: ["Computer Science & Engineering", "Information Technology", "Artificial Intelligence & Data Science"],
            ctc: "15 LPA",
            location: "Bangalore",
            positions_open: 6,
            deadline: "2026-11-28",
            description: "Craft blazing fast payment dashboards and checkout modules with sub-second latency.",
          },
        ]);
      }
    }
    fetchOpenings();
  }, [isOpen]);

  // Fetch candidates for selected opening (Recruiter Mode)
  useEffect(() => {
    if (!isOpen || !selectedOpeningId) return;

    async function fetchCandidates() {
      setIsLoading(true);
      try {
        const res = await fetch(
          `http://localhost:9000/api/v1/placement/suggest-students?opening_id=${encodeURIComponent(
            selectedOpeningId
          )}&top_n=6`
        );
        if (res.ok) {
          const data = await res.json();
          setMatchedCandidates(data.matched_students || []);
        }
      } catch {
        // Fallback matched data if backend offline
        if (selectedOpeningId.includes("GOOG")) {
          setMatchedCandidates([
            {
              student_id: "U103",
              name: "Karthik Raja",
              department: "Computer Science & Engineering",
              semester: 5,
              gpa: 9.25,
              attendance_percentage: 92.0,
              email: "karthik.raja@amypo.edu.in",
              match_percentage: 92.0,
              skill_score: 91.5,
              matched_skills: ["Python", "Go", "Distributed Systems", "Data Structures & Algorithms", "SQL", "System Design", "Kubernetes", "gRPC", "C++"],
              matched_required_skills: ["Python", "Go", "Distributed Systems", "Data Structures & Algorithms", "SQL", "System Design"],
              matched_preferred_skills: ["Kubernetes", "gRPC", "C++"],
              missing_skills: ["Redis"],
              missing_required_skills: [],
              missing_preferred_skills: ["Redis"],
              is_fully_eligible: true,
              eligibility_flags: [],
              recommendation_tier: "High Probability Selection",
              recommendation_badge: "Excellent Fit (Top Tier)",
              fit_rationale: "Strong candidate for direct shortlisting. Possesses 6/6 core required skills with high GPA (9.25) and reliable attendance (92.0%). Significantly higher selection probability compared to random allocation.",
              projects: ["Raft Consensus Distributed Key-Value Store", "Multi-Threaded HTTP/2 Proxy in C++"],
              certifications: ["Google Cloud Professional Cloud Architect", "CKA"],
            },
            {
              student_id: "U108",
              name: "Mohammed Farhan",
              department: "Computer Science & Engineering",
              semester: 7,
              gpa: 8.70,
              attendance_percentage: 85.0,
              email: "m.farhan@amypo.edu.in",
              match_percentage: 58.2,
              skill_score: 52.0,
              matched_skills: ["Python", "Go", "Kubernetes"],
              matched_required_skills: ["Python", "Go"],
              matched_preferred_skills: ["Kubernetes"],
              missing_skills: ["Distributed Systems", "Data Structures & Algorithms", "SQL", "System Design"],
              missing_required_skills: ["Distributed Systems", "Data Structures & Algorithms", "SQL", "System Design"],
              missing_preferred_skills: [],
              is_fully_eligible: true,
              eligibility_flags: [],
              recommendation_tier: "Moderate Match",
              recommendation_badge: "Needs Skill Preparation",
              fit_rationale: "Partial match with foundational skills (Python, Go). Missing essential requirements (Distributed Systems, System Design). Eligible for screening tests.",
              projects: ["Multi-Region Kubernetes Infrastructure", "Zero-Downtime Blue-Green Deployment"],
              certifications: ["AWS Solutions Architect", "Terraform Associate"],
            },
          ]);
        } else if (selectedOpeningId.includes("MSFT")) {
          setMatchedCandidates([
            {
              student_id: "U112",
              name: "Aditya Varma",
              department: "Artificial Intelligence & Data Science",
              semester: 5,
              gpa: 8.95,
              attendance_percentage: 88.0,
              email: "aditya.varma@amypo.edu.in",
              match_percentage: 96.2,
              skill_score: 95.0,
              matched_skills: ["Python", "Machine Learning", "Deep Learning", "PyTorch", "NLP", "SQL", "Statistics", "Transformers", "Vector Databases", "LangChain", "FastAPI"],
              matched_required_skills: ["Python", "Machine Learning", "Deep Learning", "PyTorch", "NLP", "SQL", "Statistics"],
              matched_preferred_skills: ["Transformers", "Vector Databases", "LangChain", "FastAPI"],
              missing_skills: [],
              missing_required_skills: [],
              missing_preferred_skills: [],
              is_fully_eligible: true,
              eligibility_flags: [],
              recommendation_tier: "High Probability Selection",
              recommendation_badge: "Excellent Fit (Top Tier)",
              fit_rationale: "Strong candidate for direct shortlisting. Possesses 7/7 core required skills with high GPA (8.95) and verified NLP transformer projects.",
              projects: ["End-to-End Enterprise Neuro-Symbolic RAG QA System", "Multimodal Medical Chest X-Ray Diagnostics Classifier"],
              certifications: ["DeepLearning.AI Specialization", "AWS ML Specialty"],
            },
          ]);
        } else {
          setMatchedCandidates([
            {
              student_id: "U106",
              name: "Sneha Patel",
              department: "Information Technology",
              semester: 3,
              gpa: 9.40,
              attendance_percentage: 94.2,
              email: "sneha.patel@amypo.edu.in",
              match_percentage: 94.8,
              skill_score: 93.0,
              matched_skills: ["React", "TypeScript", "Node.js", "PostgreSQL", "CSS", "Tailwind CSS", "Next.js", "FastAPI"],
              matched_required_skills: ["React", "TypeScript", "Node.js", "PostgreSQL", "CSS"],
              matched_preferred_skills: ["Tailwind CSS", "Docker"],
              missing_skills: ["REST APIs"],
              missing_required_skills: [],
              missing_preferred_skills: [],
              is_fully_eligible: true,
              eligibility_flags: [],
              recommendation_tier: "High Probability Selection",
              recommendation_badge: "Excellent Fit (Top Tier)",
              fit_rationale: "Outstanding alignment. Possesses verified full-stack web and database skills exceeding company benchmarks.",
              projects: ["Real-time Collaborative Code Editor", "Microservices E-Commerce Platform"],
              certifications: ["AWS Certified Developer", "Frontend Masters Certified"],
            },
            {
              student_id: "U101",
              name: "Arun Kumar",
              department: "Computer Science & Engineering",
              semester: 5,
              gpa: 8.40,
              attendance_percentage: 84.5,
              email: "arun.kumar@amypo.edu.in",
              match_percentage: 88.4,
              skill_score: 85.0,
              matched_skills: ["Python", "FastAPI", "React", "PostgreSQL", "REST APIs", "Tailwind CSS", "Docker"],
              matched_required_skills: ["React", "FastAPI", "PostgreSQL", "REST APIs"],
              matched_preferred_skills: ["Tailwind CSS", "Docker", "Python"],
              missing_skills: ["TypeScript", "Node.js"],
              missing_required_skills: ["TypeScript", "Node.js"],
              missing_preferred_skills: [],
              is_fully_eligible: true,
              eligibility_flags: [],
              recommendation_tier: "Strong Match",
              recommendation_badge: "Strong Contender",
              fit_rationale: "Solid technical alignment matching key stack (React, FastAPI, PostgreSQL). Recommended candidate for shortlisting.",
              projects: ["Campus Placement & ERP Portal", "High-Throughput Redis Cache Proxy"],
              certifications: ["Meta Front-End Developer", "PostgreSQL Associate"],
            },
          ]);
        }
      } finally {
        setIsLoading(false);
      }
    }
    fetchCandidates();
  }, [isOpen, selectedOpeningId]);

  // Fetch student personalized recommendations (Student Mode)
  useEffect(() => {
    if (!isOpen || !activeStudentId) return;

    async function fetchStudentRecommendations() {
      setIsLoading(true);
      try {
        const res = await fetch(
          `http://localhost:9000/api/v1/placement/suggest-roles?student_id=${encodeURIComponent(
            activeStudentId
          )}&top_n=5`
        );
        if (res.ok) {
          const data = await res.json();
          setStudentRecommendations(data.recommended_openings || []);
        }
      } catch {
        // Fallback student matches
        setStudentRecommendations([
          {
            opening_id: "OPN-ZOHO-04",
            company_name: "Zoho Corporation",
            role_title: "Full Stack Web Developer",
            ctc: "10 LPA",
            location: "Chennai / Tenkasi",
            deadline: "2026-11-30",
            required_skills: ["React", "TypeScript", "Node.js", "FastAPI", "PostgreSQL", "REST APIs"],
            match_percentage: 94.5,
            recommendation_tier: "High Probability Selection",
            recommendation_badge: "Best Selection Match",
            is_fully_eligible: true,
            eligibility_flags: [],
            matched_skills: ["React", "FastAPI", "PostgreSQL", "REST APIs", "Tailwind CSS"],
            missing_skills: ["TypeScript", "Node.js"],
            fit_rationale: "High selection probability. Your verified projects in full stack web development align with Zoho's technical rounds.",
          },
          {
            opening_id: "OPN-RAZOR-08",
            company_name: "Razorpay",
            role_title: "Frontend Platform Engineer",
            ctc: "15 LPA",
            location: "Bangalore",
            deadline: "2026-11-28",
            required_skills: ["JavaScript", "TypeScript", "React", "Next.js", "Tailwind CSS"],
            match_percentage: 86.0,
            recommendation_tier: "Strong Match",
            recommendation_badge: "Strong Contender",
            is_fully_eligible: true,
            eligibility_flags: [],
            matched_skills: ["React", "Tailwind CSS", "JavaScript"],
            missing_skills: ["TypeScript", "Next.js Performance"],
            fit_rationale: "Strong candidate. Brush up on Next.js hydration and TypeScript before the technical screening.",
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    }
    fetchStudentRecommendations();
  }, [isOpen, activeStudentId]);

  if (!isOpen) return null;

  const currentOpening = openings.find((o) => o.opening_id === selectedOpeningId) || openings[0];

  const filteredOpenings = openings.filter(
    (o) =>
      o.company_name.toLowerCase().includes(searchFilter.toLowerCase()) ||
      o.role_title.toLowerCase().includes(searchFilter.toLowerCase()) ||
      o.required_skills.some((s) => s.toLowerCase().includes(searchFilter.toLowerCase()))
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-3 sm:p-6 overflow-y-auto">
      <div className="relative w-full max-w-5xl bg-[#FAF8F5] rounded-2xl shadow-2xl border border-stone-300 flex flex-col max-h-[92vh] overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Top Header */}
        <div className="px-5 py-4 border-b border-stone-200 bg-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-800">
              <Briefcase className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-stone-900 font-serif">
                  Smart Placement & Skill-to-Role Matcher
                </h2>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300">
                  Anti-Random Selection
                </span>
              </div>
              <p className="text-xs text-stone-500">
                Matches candidates by verified skills and academic thresholds to eliminate random hiring allocations
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-stone-400 hover:text-stone-700 hover:bg-stone-100 transition-colors"
            title="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* View Mode Toggle Tabs */}
        <div className="px-5 pt-3 border-b border-stone-200 bg-stone-50/80 flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setActiveTab("recruiter")}
              className={`px-4 py-2 text-sm font-semibold rounded-t-xl border-b-2 transition-all flex items-center gap-2 ${
                activeTab === "recruiter"
                  ? "border-amber-700 text-amber-900 bg-white shadow-xs"
                  : "border-transparent text-stone-500 hover:text-stone-800"
              }`}
            >
              <Building2 className="w-4 h-4" />
              Recruiter & Placement Cell Mode
              <span className="text-xs px-1.5 py-0.2 rounded bg-amber-100 text-amber-900 font-medium">
                Candidate Suggestion
              </span>
            </button>

            <button
              onClick={() => setActiveTab("student")}
              className={`px-4 py-2 text-sm font-semibold rounded-t-xl border-b-2 transition-all flex items-center gap-2 ${
                activeTab === "student"
                  ? "border-amber-700 text-amber-900 bg-white shadow-xs"
                  : "border-transparent text-stone-500 hover:text-stone-800"
              }`}
            >
              <GraduationCap className="w-4 h-4" />
              Student Mode
              <span className="text-xs px-1.5 py-0.2 rounded bg-emerald-100 text-emerald-900 font-medium">
                Matched Openings
              </span>
            </button>
          </div>

          {/* Student Selector in Student Mode */}
          {activeTab === "student" && (
            <div className="flex items-center gap-2 pb-2">
              <span className="text-xs font-medium text-stone-600">Active Student:</span>
              <select
                value={activeStudentId}
                onChange={(e) => onStudentIdChange(e.target.value)}
                className="text-xs font-semibold px-2.5 py-1.5 rounded-lg border border-stone-300 bg-white text-stone-800 shadow-2xs focus:outline-none focus:ring-1 focus:ring-amber-500"
              >
                {SAMPLE_STUDENT_IDS.map((sid) => (
                  <option key={sid} value={sid}>
                    {sid} ({sid === "U101" ? "Arun Kumar" : sid === "U103" ? "Karthik Raja" : sid === "U106" ? "Sneha Patel" : sid === "U112" ? "Aditya Varma" : sid})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {activeTab === "recruiter" ? (
            /* ─────────────────────────────────────────────────────────────────
               RECRUITER / PLACEMENT COORDINATOR MODE
               ───────────────────────────────────────────────────────────────── */
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
              {/* Left Column: Company Openings Selector */}
              <div className="lg:col-span-4 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-stone-600 uppercase tracking-wider flex items-center gap-1.5">
                    <Building2 className="w-3.5 h-3.5 text-amber-800" />
                    Select Company Opening
                  </h3>
                  <span className="text-xs text-stone-400 font-medium">{openings.length} Active Roles</span>
                </div>

                {/* Filter input */}
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-stone-400" />
                  <input
                    type="text"
                    value={searchFilter}
                    onChange={(e) => setSearchFilter(e.target.value)}
                    placeholder="Search company or skill..."
                    className="w-full text-xs pl-8 pr-3 py-2 rounded-xl border border-stone-200 bg-white text-stone-800 placeholder-stone-400 focus:outline-none focus:ring-1 focus:ring-amber-500"
                  />
                </div>

                {/* Openings list */}
                <div className="space-y-2 max-h-[460px] overflow-y-auto pr-1">
                  {filteredOpenings.map((op) => {
                    const isSelected = op.opening_id === selectedOpeningId;
                    return (
                      <button
                        key={op.opening_id}
                        onClick={() => setSelectedOpeningId(op.opening_id)}
                        className={`w-full text-left p-3 rounded-xl border transition-all ${
                          isSelected
                            ? "border-amber-600 bg-amber-50/60 shadow-xs ring-1 ring-amber-500/30"
                            : "border-stone-200 bg-white hover:border-stone-300 hover:bg-stone-50"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-xs text-stone-900">{op.company_name}</span>
                          <span className="text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                            {op.ctc}
                          </span>
                        </div>
                        <p className="text-xs text-stone-600 font-medium mt-1 truncate">{op.role_title}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {op.required_skills.slice(0, 3).map((sk) => (
                            <span
                              key={sk}
                              className="text-[10px] px-1.5 py-0.2 rounded bg-stone-100 text-stone-600 font-mono"
                            >
                              {sk}
                            </span>
                          ))}
                          {op.required_skills.length > 3 && (
                            <span className="text-[10px] text-stone-400">+{op.required_skills.length - 3}</span>
                          )}
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Right Column: Selected Opening Details & Matched Students */}
              <div className="lg:col-span-8 space-y-4">
                {currentOpening && (
                  <>
                    {/* Role Requirements Banner */}
                    <div className="p-4 rounded-xl bg-white border border-stone-200 shadow-xs space-y-2.5">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div>
                          <span className="text-xs font-bold text-amber-900 tracking-wide uppercase">
                            {currentOpening.company_name}
                          </span>
                          <h3 className="text-base font-bold text-stone-900 font-serif">
                            {currentOpening.role_title}
                          </h3>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-900 font-bold border border-emerald-200">
                            💰 {currentOpening.ctc}
                          </span>
                          <span className="text-xs px-2.5 py-1 rounded-full bg-stone-100 text-stone-700 font-medium">
                            📍 {currentOpening.location}
                          </span>
                        </div>
                      </div>

                      {/* Required Tech Stack */}
                      <div>
                        <span className="text-[11px] font-bold text-stone-500 uppercase tracking-wider">
                          Required Tech Stack:
                        </span>
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {currentOpening.required_skills.map((sk) => (
                            <span
                              key={sk}
                              className="text-xs px-2 py-0.5 rounded-lg bg-amber-50 text-amber-900 font-semibold border border-amber-200"
                            >
                              {sk}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Criteria & Eligibility Cutoffs */}
                      <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-stone-100 text-xs text-stone-600">
                        <span>
                          <strong>Min CGPA:</strong> {currentOpening.min_cgpa}
                        </span>
                        <span>•</span>
                        <span>
                          <strong>Min Attendance:</strong> {currentOpening.min_attendance}%
                        </span>
                        <span>•</span>
                        <span>
                          <strong>Positions:</strong> {currentOpening.positions_open}
                        </span>
                        <span>•</span>
                        <span>
                          <strong>Deadline:</strong> {currentOpening.deadline}
                        </span>
                      </div>
                    </div>

                    {/* Anti-Random Selection Value Callout */}
                    <div className="p-3 rounded-xl bg-gradient-to-r from-emerald-50 to-amber-50 border border-emerald-200/80 flex items-start gap-2.5 text-xs text-stone-700">
                      <Sparkles className="w-4 h-4 text-emerald-700 shrink-0 mt-0.5" />
                      <div>
                        <strong className="text-emerald-900">Why Skill Matching Prevents Wasted Chances:</strong>
                        <p className="mt-0.5 text-stone-600">
                          Traditional random lotteries send candidates to roles they aren&apos;t prepared for, causing immediate rejection.
                          Below candidates are ranked by exact overlap with {currentOpening.company_name}&apos;s stack, giving maximum interview success probability.
                        </p>
                      </div>
                    </div>

                    {/* Ranked Candidates Cards */}
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h4 className="text-xs font-bold text-stone-700 uppercase tracking-wider flex items-center gap-1.5">
                          <UserCheck className="w-3.5 h-3.5 text-emerald-800" />
                          Ranked Candidate Recommendations ({matchedCandidates.length})
                        </h4>
                        <button
                          onClick={() => {
                            onSelectQuery(`Suggest students for ${currentOpening.company_name} ${currentOpening.role_title} opening`);
                            onClose();
                          }}
                          className="text-xs text-amber-900 hover:text-amber-800 font-semibold flex items-center gap-1 hover:underline"
                        >
                          Ask AI in Chat <ArrowRight className="w-3 h-3" />
                        </button>
                      </div>

                      {isLoading ? (
                        <div className="p-8 text-center text-xs text-stone-500">
                          Analyzing student skill vectors and calculating compatibility...
                        </div>
                      ) : matchedCandidates.length === 0 ? (
                        <div className="p-8 text-center text-xs text-stone-500 border border-dashed rounded-xl">
                          No matching students found for this opening criteria.
                        </div>
                      ) : (
                        matchedCandidates.map((c, idx) => (
                          <div
                            key={c.student_id}
                            className="p-4 rounded-xl bg-white border border-stone-200 hover:border-stone-300 transition-all shadow-xs space-y-2.5"
                          >
                            {/* Candidate Header */}
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <span className="w-6 h-6 rounded-full bg-stone-100 text-stone-700 font-bold text-xs flex items-center justify-center">
                                  {idx + 1}
                                </span>
                                <div>
                                  <h5 className="font-bold text-sm text-stone-900">{c.name}</h5>
                                  <span className="text-xs text-stone-500">
                                    ID: <code>{c.student_id}</code> | {c.department} (Sem {c.semester})
                                  </span>
                                </div>
                              </div>

                              <div className="flex items-center gap-2">
                                <span
                                  className={`text-xs px-2.5 py-1 rounded-full font-bold border ${
                                    c.match_percentage >= 85
                                      ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                                      : c.match_percentage >= 70
                                      ? "bg-blue-50 text-blue-800 border-blue-200"
                                      : "bg-amber-50 text-amber-900 border-amber-300"
                                  }`}
                                >
                                  {c.match_percentage}% Match
                                </span>
                                <span className="text-[11px] px-2 py-0.5 rounded-md bg-stone-100 text-stone-600 font-medium">
                                  {c.recommendation_badge}
                                </span>
                              </div>
                            </div>

                            {/* Academic standing pills */}
                            <div className="flex items-center gap-3 text-xs text-stone-600">
                              <span>
                                <strong>CGPA:</strong> {c.gpa.toFixed(2)}
                              </span>
                              <span>•</span>
                              <span>
                                <strong>Attendance:</strong> {c.attendance_percentage}%
                              </span>
                              {c.eligibility_flags.length > 0 && (
                                <span className="text-amber-800 font-medium flex items-center gap-1">
                                  <AlertCircle className="w-3 h-3 text-amber-600" />
                                  {c.eligibility_flags[0]}
                                </span>
                              )}
                            </div>

                            {/* Matched skills chips */}
                            <div>
                              <span className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">
                                Matched Required Skills:
                              </span>
                              <div className="flex flex-wrap gap-1.5 mt-1">
                                {c.matched_skills.map((sk) => (
                                  <span
                                    key={sk}
                                    className="text-[11px] px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 font-medium border border-emerald-200 flex items-center gap-1"
                                  >
                                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                                    {sk}
                                  </span>
                                ))}
                                {c.missing_skills.length > 0 && (
                                  <div className="flex flex-wrap gap-1.5 items-center">
                                    <span className="text-[10px] text-stone-400 ml-1">Missing:</span>
                                    {c.missing_skills.map((sk) => (
                                      <span
                                        key={sk}
                                        className="text-[11px] px-2 py-0.5 rounded-md bg-amber-50 text-amber-900 border border-amber-200"
                                      >
                                        {sk}
                                      </span>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Fit Rationale */}
                            <p className="text-xs text-stone-600 bg-stone-50 p-2.5 rounded-lg border border-stone-200/80">
                              <strong>Selection Rationale:</strong> {c.fit_rationale}
                            </p>

                            {/* Action to Ask in Chat */}
                            <div className="flex justify-end pt-1">
                              <button
                                onClick={() => {
                                  onSelectQuery(
                                    `Evaluate student ${c.name} (${c.student_id}) for ${currentOpening.company_name} ${currentOpening.role_title} opening`
                                  );
                                  onClose();
                                }}
                                className="text-xs px-3 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 font-medium transition-colors"
                              >
                                View Detailed Evaluation in Chat →
                              </button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </>
                )}
              </div>
            </div>
          ) : (
            /* ─────────────────────────────────────────────────────────────────
               STUDENT MODE: My Recommended Company Roles
               ───────────────────────────────────────────────────────────────── */
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-white border border-stone-200 shadow-xs flex flex-wrap items-center justify-between gap-3">
                <div>
                  <span className="text-xs font-bold text-amber-900 uppercase">
                    Personalized Opportunity Matcher
                  </span>
                  <h3 className="text-base font-bold text-stone-900 font-serif">
                    Best Company Openings for Student {activeStudentId}
                  </h3>
                  <p className="text-xs text-stone-500 mt-0.5">
                    Roles are ranked by your skill alignment so you can apply where you have the highest chance of selection without wasting applications.
                  </p>
                </div>

                <button
                  onClick={() => {
                    onSelectQuery("Which company roles match my skills best?");
                    onClose();
                  }}
                  className="px-3.5 py-2 rounded-xl bg-amber-800 hover:bg-amber-900 text-white text-xs font-semibold shadow-xs flex items-center gap-1.5"
                >
                  <Sparkles className="w-3.5 h-3.5" />
                  Run AI Skill Match in Chat
                </button>
              </div>

              {/* Recommended Openings Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {studentRecommendations.map((op, idx) => (
                  <div
                    key={op.opening_id}
                    className="p-4 rounded-xl bg-white border border-stone-200 hover:border-amber-300 transition-all shadow-xs space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-xs font-bold text-amber-900">{op.company_name}</span>
                        <h4 className="text-sm font-bold text-stone-900">{op.role_title}</h4>
                        <span className="text-xs text-stone-500">
                          {op.ctc} | {op.location}
                        </span>
                      </div>

                      <div className="text-right">
                        <span
                          className={`text-sm px-2.5 py-1 rounded-full font-bold border ${
                            op.match_percentage >= 85
                              ? "bg-emerald-50 text-emerald-800 border-emerald-300"
                              : "bg-blue-50 text-blue-800 border-blue-200"
                          }`}
                        >
                          {op.match_percentage}% Match
                        </span>
                      </div>
                    </div>

                    {/* Matched & Missing Skills */}
                    <div className="space-y-1.5">
                      <div>
                        <span className="text-[10px] font-bold text-stone-400 uppercase">Skills You Have:</span>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {op.matched_skills.map((sk) => (
                            <span
                              key={sk}
                              className="text-[11px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200 font-medium"
                            >
                              ✓ {sk}
                            </span>
                          ))}
                        </div>
                      </div>

                      {op.missing_skills.length > 0 && (
                        <div>
                          <span className="text-[10px] font-bold text-stone-400 uppercase">
                            Recommended to Prepare:
                          </span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {op.missing_skills.map((sk) => (
                              <span
                                key={sk}
                                className="text-[11px] px-2 py-0.5 rounded bg-amber-50 text-amber-900 border border-amber-200"
                              >
                                {sk}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Guidance */}
                    <p className="text-xs text-stone-600 bg-stone-50 p-2.5 rounded-lg border border-stone-200/80">
                      {op.fit_rationale}
                    </p>

                    <div className="flex items-center justify-between pt-1">
                      <span className="text-[11px] text-stone-400">Deadline: {op.deadline}</span>
                      <button
                        onClick={() => {
                          onSelectQuery(
                            `Can I apply for ${op.company_name} ${op.role_title} with my profile?`
                          );
                          onClose();
                        }}
                        className="text-xs text-amber-800 hover:text-amber-900 font-semibold hover:underline"
                      >
                        Check Application Odds →
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-stone-200 bg-stone-50 flex items-center justify-between text-xs text-stone-500">
          <span>AMYPO Career & Placement Cell • Deterministic Skill Compatibility Engine</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl border border-stone-300 bg-white hover:bg-stone-100 text-stone-700 font-medium transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
