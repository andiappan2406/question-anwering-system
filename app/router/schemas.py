from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RouteType(str, Enum):
    SQL = "personal_sql"
    RAG = "vector_rag"
    HYBRID = "hybrid"
    DIRECT = "direct_answer"
    CHITCHAT = "chitchat"
    UNKNOWN = "unknown"


class DatabaseDialect(str, Enum):
    POSTGRESQL = "postgresql"
    SUPABASE = "supabase"
    SQLITE = "sqlite"
    MYSQL = "mysql"


class DatabaseTargetType(str, Enum):
    POSTGRESQL = "postgresql"
    SUPABASE = "supabase"
    SQLITE = "sqlite"
    RELATIONAL_SQL = "relational_sql"
    VECTOR_STORE = "vector_store"
    CACHE = "semantic_cache"
    ANALYTICS = "analytics"


class DataPriority(int, Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class RouterInput(BaseModel):
    """
    Standardized, structured input packet for the router.
    """
    raw_query: str = Field(..., description="The raw natural language query.")
    user_id: Optional[str] = Field(default=None, description="Authenticated user ID if available.")
    session_id: Optional[str] = Field(default=None, description="Session tracking ID.")
    permissions: List[str] = Field(default_factory=list, description="Access permissions/roles.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary query metadata.")
    timestamp: float = Field(default_factory=time.time, description="Unix epoch timestamp.")

    @property
    def sanitized_query(self) -> str:
        return " ".join(self.raw_query.strip().split())


class DatabaseOffloadTarget(BaseModel):
    """
    Represents a specific target database to offload a query or sub-query to.
    """
    target_id: str = Field(..., description="Unique database target identifier, e.g., 'db_personal_students_sql'.")
    engine_type: DatabaseTargetType = Field(..., description="Target database engine type.")
    sub_query: str = Field(..., description="Decomposed sub-query or query slice for this database.")
    required_parameters: Dict[str, Any] = Field(default_factory=dict, description="Parameters required by the query (e.g. user_id, table).")
    priority: DataPriority = Field(default=DataPriority.MEDIUM, description="Execution and retrieval priority.")
    estimated_cost: float = Field(default=1.0, description="Relative computational/latency weight.")
    cacheable: bool = Field(default=False, description="Whether results from this offload can be safely cached.")
    privacy_level: str = Field(default="confidential", description="Privacy boundary ('confidential', 'restricted', 'public').")


class RoutingDecision(BaseModel):
    """
    Deterministic output from the Neuro-Symbolic Router.
    """
    primary_route: RouteType = Field(..., description="Primary routing path.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Routing confidence score.")
    intent_summary: str = Field(..., description="High-level description of user intent.")
    offload_plan: List[DatabaseOffloadTarget] = Field(default_factory=list, description="Sorted list of database offload targets.")
    execution_steps: List[str] = Field(default_factory=list, description="Ordered procedural pipeline steps.")
    reasoning_trace: List[str] = Field(default_factory=list, description="Step-by-step neuro-symbolic reasoning trace.")
    is_neuro_verified: bool = Field(default=False, description="Whether an SLM verified or refined the symbolic decision.")
    timestamp: float = Field(default_factory=time.time, description="Decision generation timestamp.")


class ContextItem(BaseModel):
    """
    Standardized payload for individual retrieved context snippets.
    """
    source_id: str = Field(..., description="Unique identifier of the record or document.")
    database_target: str = Field(..., description="Originating database identifier.")
    snippet: str = Field(..., description="Retrieved contextual snippet or data payload.")
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence or similarity score.")
    priority: DataPriority = Field(default=DataPriority.MEDIUM, description="Inherent priority.")
    timestamp: float = Field(default_factory=time.time, description="Record creation or retrieval timestamp.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional contextual metadata.")


class SortedContextBatch(BaseModel):
    """
    Strictly sorted collection of contexts delivered in and out of the QA pipeline.
    """
    query: str = Field(..., description="Query associated with the contexts.")
    route: RouteType = Field(..., description="Route type used.")
    items: List[ContextItem] = Field(default_factory=list, description="Sorted items.")
    total_items: int = Field(default=0, description="Count of items.")
    summary: Optional[str] = Field(default=None, description="Optional high-level synthesized summary.")


# ══════════════════════════════════════════════════════════════════════════════
# Versatile Database Management & Placement Schemas
# ══════════════════════════════════════════════════════════════════════════════

class DatabaseConnectionConfig(BaseModel):
    """
    Versatile database connection configuration supporting PostgreSQL (Supabase),
    SQLite, and other relational backends.
    """
    dialect: DatabaseDialect = Field(default=DatabaseDialect.POSTGRESQL, description="Database dialect.")
    url: Optional[str] = Field(default=None, description="Complete database connection URL.")
    host: Optional[str] = Field(default=None, description="Database host.")
    port: int = Field(default=5432, description="Database port.")
    database: Optional[str] = Field(default=None, description="Database name.")
    user: Optional[str] = Field(default=None, description="Database user.")
    password: Optional[str] = Field(default=None, description="Database password.")
    sslmode: str = Field(default="prefer", description="SSL connection mode.")
    pool_size: int = Field(default=5, description="Connection pool size.")
    max_overflow: int = Field(default=10, description="Max overflow connections.")
    timeout_sec: float = Field(default=5.0, description="Connection timeout in seconds.")


class DatabaseHealthStatus(BaseModel):
    """
    Live health and connectivity status of the configured database.
    """
    connected: bool = Field(..., description="Whether the database is connected and responsive.")
    engine: str = Field(..., description="Active database engine (e.g. 'PostgreSQL 17 (Supabase)', 'SQLite 3').")
    dialect: DatabaseDialect = Field(..., description="Current database dialect in use.")
    database_name: str = Field(..., description="Connected database name.")
    host: Optional[str] = Field(default=None, description="Connected database host.")
    latency_ms: float = Field(default=0.0, description="Roundtrip query latency in milliseconds.")
    active_tables: List[str] = Field(default_factory=list, description="List of recognized active tables.")
    total_records: int = Field(default=0, description="Total records across core institutional tables.")
    is_cloud_hosted: bool = Field(default=False, description="Whether connected to cloud DB (e.g. Supabase).")
    last_sync_timestamp: float = Field(default_factory=time.time, description="Unix timestamp of last health probe.")


class CompanyOpeningSchema(BaseModel):
    """
    Structured model for corporate job opening requirements.
    """
    opening_id: str = Field(..., description="Unique opening identifier, e.g. 'OPN-GOOG-01'.")
    company_name: str = Field(..., description="Hiring company name.")
    role_title: str = Field(..., description="Job role title.")
    required_skills: List[str] = Field(default_factory=list, description="Mandatory tech stack competencies.")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred secondary tools.")
    min_cgpa: float = Field(default=7.0, description="Minimum CGPA cutoff.")
    min_attendance: float = Field(default=75.0, description="Minimum attendance percentage requirement.")
    eligible_departments: List[str] = Field(default_factory=list, description="Eligible academic departments.")
    ctc: str = Field(..., description="Compensation package.")
    location: str = Field(..., description="Work location.")
    positions_open: int = Field(default=1, description="Number of available positions.")
    deadline: str = Field(..., description="Application deadline.")
    description: str = Field(..., description="Role summary and responsibilities.")


class StudentPlacementProfileSchema(BaseModel):
    """
    Structured profile of a student's placement credentials and verified skills.
    """
    student_id: str = Field(..., description="Unique student ID.")
    name: str = Field(..., description="Student full name.")
    department: str = Field(..., description="Academic department.")
    semester: int = Field(..., description="Current semester.")
    gpa: float = Field(..., description="Current cumulative GPA.")
    attendance_percentage: float = Field(..., description="Overall attendance percentage.")
    email: str = Field(..., description="Institutional email.")
    primary_skills: List[str] = Field(default_factory=list, description="Core technical competencies.")
    secondary_skills: List[str] = Field(default_factory=list, description="Familiar secondary tools.")
    certifications: List[str] = Field(default_factory=list, description="Verified professional certifications.")
    projects: List[str] = Field(default_factory=list, description="Key engineering and GitHub projects.")
    preferred_role: str = Field(default="Software Engineer", description="Target job profile.")
    placement_status: str = Field(default="Active Seeking", description="Current campus placement status.")


class CandidateMatchResult(BaseModel):
    """
    Deterministic compatibility assessment between a student and a corporate opening.
    """
    student_id: str = Field(..., description="Candidate student ID.")
    name: str = Field(..., description="Candidate name.")
    department: str = Field(..., description="Candidate department.")
    semester: int = Field(..., description="Semester.")
    gpa: float = Field(..., description="Cumulative GPA.")
    attendance_percentage: float = Field(..., description="Attendance percentage.")
    email: str = Field(..., description="Email.")
    match_percentage: float = Field(..., ge=0.0, le=100.0, description="Calculated composite compatibility percentage.")
    skill_score: float = Field(default=0.0, description="Pure skill overlap score.")
    matched_skills: List[str] = Field(default_factory=list, description="Required & preferred skills candidate possesses.")
    missing_skills: List[str] = Field(default_factory=list, description="Skills candidate needs to acquire.")
    is_fully_eligible: bool = Field(default=True, description="Whether academic cutoffs are strictly met.")
    eligibility_flags: List[str] = Field(default_factory=list, description="Specific cutoff warnings.")
    recommendation_tier: str = Field(..., description="Category: 'High Probability Selection', 'Strong Match', etc.")
    recommendation_badge: str = Field(..., description="Short badge title for UI display.")
    fit_rationale: str = Field(..., description="Detailed explanation of why this match prevents wasted chances.")
    projects: List[str] = Field(default_factory=list, description="Relevant project work.")
    certifications: List[str] = Field(default_factory=list, description="Certifications.")


class PlacementMatchBatchResponse(BaseModel):
    """
    API payload for candidate ranking on a corporate opening.
    """
    opening: Optional[CompanyOpeningSchema] = Field(default=None, description="Opening criteria.")
    matched_students: List[CandidateMatchResult] = Field(default_factory=list, description="Ranked list of candidates.")
    total_evaluated: int = Field(default=0, description="Total candidate pool size evaluated.")
    anti_random_selection_insight: str = Field(..., description="Empirical rationale for skill-aligned recruitment.")


class RecommendedOpeningResult(BaseModel):
    """
    Individual company opening recommendation for a specific student.
    """
    opening_id: str = Field(..., description="Opening ID.")
    company_name: str = Field(..., description="Company name.")
    role_title: str = Field(..., description="Role title.")
    ctc: str = Field(..., description="Compensation.")
    location: str = Field(..., description="Location.")
    deadline: str = Field(..., description="Deadline.")
    required_skills: List[str] = Field(default_factory=list, description="Required tech stack.")
    match_percentage: float = Field(..., description="Student compatibility score.")
    recommendation_tier: str = Field(..., description="Suitability tier.")
    recommendation_badge: str = Field(..., description="Display badge.")
    is_fully_eligible: bool = Field(default=True, description="Eligibility.")
    eligibility_flags: List[str] = Field(default_factory=list, description="Warnings.")
    matched_skills: List[str] = Field(default_factory=list, description="Skills student possesses.")
    missing_skills: List[str] = Field(default_factory=list, description="Skills student should prepare.")
    fit_rationale: str = Field(..., description="Personalized guidance.")


class StudentRoleRecommendationResponse(BaseModel):
    """
    API payload for student personalized company role suggestions.
    """
    student: Optional[StudentPlacementProfileSchema] = Field(default=None, description="Student profile.")
    recommended_openings: List[RecommendedOpeningResult] = Field(default_factory=list, description="Ranked openings.")
    all_openings_count: int = Field(default=0, description="Total active openings.")
    guidance: str = Field(..., description="Strategic application advice to avoid wasted chances.")


class DynamicQueryPayload(BaseModel):
    """
    Versatile database query specification for dynamic execution.
    """
    table: str = Field(..., description="Target database table.")
    columns: List[str] = Field(default_factory=lambda: ["*"], description="Columns to retrieve.")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Equality filters.")
    order_by: Optional[str] = Field(default=None, description="Order by column expression.")
    limit: Optional[int] = Field(default=100, description="Maximum rows.")
    offset: Optional[int] = Field(default=0, description="Row offset.")

