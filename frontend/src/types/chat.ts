export type UserRole = "student" | "staff";

export type RoutingPath = "cache" | "sql" | "vector" | "llm";

export interface SourceCitation {
  record_id: string;
  snippet: string;
  title?: string;
  score?: number;
  collection?: string;
  url?: string;
}

export interface RoutingStep {
  name: string;
  status: "completed" | "skipped" | "fallback";
  latencyMs: number;
  details?: string;
}

export interface RoutingTrace {
  path: RoutingPath;
  latencyMs: number;
  decisionReason: string;
  steps: RoutingStep[];
  // Path-specific metrics
  cachedAt?: string;
  cacheKey?: string;
  sqlQuery?: string;
  tablesAccessed?: string[];
  vectorSimilarity?: number;
  indexName?: string;
  topK?: number;
  isInferred?: boolean;
  model?: string;
  tokensUsed?: {
    prompt: number;
    completion: number;
    total: number;
  };
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  confidence?: number; // 0.0 to 1.0
  sources?: SourceCitation[];
  trace?: RoutingTrace;
  userId?: string;
  userRole?: UserRole;
  isStreaming?: boolean;
}

export interface AskRequestBody {
  question: string;
  user_id?: string;
  use_llm?: boolean;
}

export interface AskResponseBody {
  answer: string;
  sources: SourceCitation[];
  confidence: number;
  trace?: RoutingTrace;
}

export interface CompanyOpening {
  opening_id: string;
  company_name: string;
  role_title: string;
  required_skills: string[];
  preferred_skills: string[];
  min_cgpa: number;
  min_attendance: number;
  eligible_departments: string[];
  ctc: string;
  location: string;
  positions_open: number;
  deadline: string;
  description: string;
}

export interface MatchedCandidate {
  student_id: string;
  name: string;
  department: string;
  semester: number;
  gpa: number;
  attendance_percentage: number;
  email: string;
  match_percentage: number;
  skill_score: number;
  matched_skills: string[];
  matched_required_skills: string[];
  matched_preferred_skills: string[];
  missing_skills: string[];
  missing_required_skills: string[];
  missing_preferred_skills: string[];
  is_fully_eligible: boolean;
  eligibility_flags: string[];
  recommendation_tier: string;
  recommendation_badge: string;
  fit_rationale: string;
  projects: string[];
  certifications: string[];
}

export interface RecommendedOpening {
  opening_id: string;
  company_name: string;
  role_title: string;
  ctc: string;
  location: string;
  deadline: string;
  required_skills: string[];
  match_percentage: number;
  recommendation_tier: string;
  recommendation_badge: string;
  is_fully_eligible: boolean;
  eligibility_flags: string[];
  matched_skills: string[];
  missing_skills: string[];
  fit_rationale: string;
}

export interface DatabaseHealthStatus {
  connected: boolean;
  engine: string;
  dialect: "postgresql" | "supabase" | "sqlite" | "mysql";
  database_name: string;
  host?: string | null;
  latency_ms: number;
  active_tables: string[];
  total_records: number;
  is_cloud_hosted: boolean;
  last_sync_timestamp: number;
}

