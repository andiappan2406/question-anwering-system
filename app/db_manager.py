"""
Versatile Multi-Dialect Database Manager for AMYPO Institute of Technology & Science.
Supports production Supabase PostgreSQL and seamless local SQLite fallback,
providing connection pooling, automatic parameter translation, table migration,
seed synchronization, dynamic query execution, and live health metrics.
"""

import os
import re
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import quote_plus, urlparse

from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

from app.router.schemas import (
    DatabaseConnectionConfig,
    DatabaseDialect,
    DatabaseHealthStatus,
    DynamicQueryPayload,
)

# Optional psycopg2 import for PostgreSQL / Supabase
try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


SQLITE_DEFAULT_PATH = os.path.abspath(
    os.getenv("FALLBACK_SQLITE_PATH", "data/students.db")
)


def normalize_postgres_url(raw_url: str) -> str:
    """
    Sanitize and URL-encode credentials if special characters like '@' appear
    in the password component.
    """
    if not raw_url:
        return ""
    # Standardize scheme
    if raw_url.startswith("postgres://"):
        raw_url = "postgresql://" + raw_url[len("postgres://"):]

    # Check for unencoded '@' in password: e.g. postgresql://user:pass@word@host:port/db
    match = re.match(r"^(postgresql://)([^:]+):(.*)@([^@/]+(?::\d+)?)(/.*)?$", raw_url)
    if match:
        prefix, user, password, host, rest = match.groups()
        if "@" in password and not "%40" in password:
            encoded_password = quote_plus(password)
            return f"{prefix}{user}:{encoded_password}@{host}{rest or ''}"
    return raw_url


class DatabaseManager:
    """
    Unified database manager providing multi-dialect support (PostgreSQL/Supabase + SQLite),
    automatic placeholder adaptation, health monitoring, and schema auto-migration.
    """

    CORE_TABLES = [
        "students",
        "staff",
        "courses",
        "student_course_attendance",
        "exam_schedule",
        "company_openings",
        "student_skills",
    ]

    def __init__(self, database_url: Optional[str] = None, sqlite_path: Optional[str] = None):
        self.raw_db_url = database_url or os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL") or ""
        self.db_url = normalize_postgres_url(self.raw_db_url)
        self.sqlite_path = sqlite_path or SQLITE_DEFAULT_PATH
        self.force_sqlite = os.getenv("USE_SQLITE", "false").strip().lower() in ("true", "1", "yes")

        self.dialect: DatabaseDialect = DatabaseDialect.SQLITE
        self.is_connected: bool = False
        self.active_engine_name: str = "SQLite 3 (Local)"
        self.pool: Optional[Any] = None

        self._initialize_connection()
        self._ensure_schema_and_seed()

    @property
    def active_dialect(self) -> str:
        return self.dialect.value if hasattr(self.dialect, "value") else str(self.dialect)

    def _initialize_connection(self):
        """Initialize connection pool for PostgreSQL or fall back to SQLite."""
        if not self.force_sqlite and self.db_url and HAS_PSYCOPG2:
            try:
                # Test connection directly
                test_conn = psycopg2.connect(self.db_url, connect_timeout=5)
                cur = test_conn.cursor()
                cur.execute("SELECT version();")
                version_str = cur.fetchone()[0]
                test_conn.close()

                # Initialize connection pool
                self.pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=self.db_url,
                )
                self.dialect = DatabaseDialect.SUPABASE if "supabase" in self.db_url else DatabaseDialect.POSTGRESQL
                self.is_connected = True
                
                # Format engine name
                short_ver = version_str.split(",")[0] if "," in version_str else version_str.split()[0] + " " + version_str.split()[1]
                target_label = "Supabase Cloud" if "supabase" in self.db_url else "PostgreSQL"
                self.active_engine_name = f"{target_label} ({short_ver})"
                print(f"[DB Manager] Connected to {self.active_engine_name} successfully.")
                return
            except Exception as e:
                print(f"[DB Manager] Failed to connect to PostgreSQL ({e}). Falling back to SQLite.")
                self.pool = None

        # Fallback: SQLite
        self.dialect = DatabaseDialect.SQLITE
        self.active_engine_name = f"SQLite 3 ({os.path.basename(self.sqlite_path)})"
        self.is_connected = os.path.exists(self.sqlite_path)
        print(f"[DB Manager] Using {self.active_engine_name} at {self.sqlite_path}")

    def _get_pg_connection(self):
        """Obtain a PostgreSQL connection from the pool or directly."""
        if self.pool:
            return self.pool.getconn()
        return psycopg2.connect(self.db_url)

    def _put_pg_connection(self, conn):
        """Return a PostgreSQL connection to the pool."""
        if self.pool and conn:
            try:
                self.pool.putconn(conn)
            except Exception:
                try:
                    conn.close()
                except Exception:
                    pass
        elif conn:
            try:
                conn.close()
            except Exception:
                pass

    def get_sqlite_connection(self) -> sqlite3.Connection:
        """Create and return a configured SQLite connection with row factory."""
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        return conn

    def adapt_query(self, query: str) -> str:
        """
        Adapt parameter placeholders:
        Converts '?' to '%s' when targeting PostgreSQL, while escaping literal '%'
        characters so psycopg2 does not confuse them with Python format specifiers.
        """
        if self.dialect in (DatabaseDialect.POSTGRESQL, DatabaseDialect.SUPABASE):
            # Replace ? with %s
            adapted = query.replace("?", "%s")
            # Escape literal % that is not %s and not already %%
            return re.sub(r"%(?!s|%)", "%%", adapted)
        return query

    def execute_query(
        self,
        query: str,
        params: Union[Tuple, List] = (),
        fetch: str = "all",
    ) -> Any:
        """
        Execute a query across the active dialect with automatic parameter adaptation
        and dictionary-friendly row conversion.
        fetch: 'all', 'one', or 'none' (for INSERT/UPDATE/DELETE).
        """
        adapted_sql = self.adapt_query(query)

        # ── PostgreSQL / Supabase Path ──────────────────────────────────────────
        if self.dialect in (DatabaseDialect.POSTGRESQL, DatabaseDialect.SUPABASE) and HAS_PSYCOPG2:
            conn = None
            try:
                conn = self._get_pg_connection()
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(adapted_sql, params)

                if fetch == "all":
                    rows = cur.fetchall()
                    result = [dict(r) for r in rows]
                elif fetch == "one":
                    row = cur.fetchone()
                    result = dict(row) if row else None
                else:
                    conn.commit()
                    result = cur.rowcount

                cur.close()
                self._put_pg_connection(conn)
                return result
            except Exception as pg_err:
                print(f"[DB Manager] PG Query error: {pg_err}. Attempting SQLite fallback.")
                if conn:
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    self._put_pg_connection(conn)
                # Fall through to SQLite fallback on query error

        # ── SQLite Fallback Path ──────────────────────────────────────────────
        conn = self.get_sqlite_connection()
        c = conn.cursor()
        # Ensure ? placeholders for SQLite
        sqlite_sql = query.replace("%s", "?")
        try:
            c.execute(sqlite_sql, params)
            if fetch == "all":
                rows = c.fetchall()
                result = [dict(r) for r in rows]
            elif fetch == "one":
                row = c.fetchone()
                result = dict(row) if row else None
            else:
                conn.commit()
                result = c.rowcount
            conn.close()
            return result
        except Exception as sq_err:
            print(f"[DB Manager] SQLite Query error: {sq_err}")
            conn.close()
            raise sq_err

    # ══════════════════════════════════════════════════════════════════════════
    # Schema Provisioning & Auto-Sync
    # ══════════════════════════════════════════════════════════════════════════

    def _ensure_schema_and_seed(self):
        """Provision schema on cloud PostgreSQL if missing, and sync seed data."""
        if self.dialect in (DatabaseDialect.POSTGRESQL, DatabaseDialect.SUPABASE) and HAS_PSYCOPG2:
            try:
                self.create_tables_postgres()
                self.sync_seed_data_to_postgres()
            except Exception as e:
                print(f"[DB Manager] Error during PostgreSQL schema ensure/seed: {e}")

    def create_tables_postgres(self):
        """Create standard institutional and placement tables in PostgreSQL if not present."""
        tables_ddl = [
            """
            CREATE TABLE IF NOT EXISTS students (
                student_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                department VARCHAR(255) NOT NULL,
                semester INT NOT NULL,
                section VARCHAR(50) NOT NULL,
                attendance_percentage REAL NOT NULL,
                gpa REAL NOT NULL,
                fees_status TEXT NOT NULL,
                pending_dues INT NOT NULL,
                email VARCHAR(255) NOT NULL,
                mentor VARCHAR(255) NOT NULL,
                hostel_details TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS staff (
                staff_id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                department VARCHAR(255) NOT NULL,
                role VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                office VARCHAR(255) NOT NULL,
                specialization VARCHAR(255) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_code VARCHAR(50) PRIMARY KEY,
                course_name VARCHAR(255) NOT NULL,
                department VARCHAR(255) NOT NULL,
                semester INT NOT NULL,
                credits INT NOT NULL,
                instructor VARCHAR(255) NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS student_course_attendance (
                student_id VARCHAR(50) NOT NULL,
                course_code VARCHAR(50) NOT NULL,
                course_name VARCHAR(255) NOT NULL,
                attendance_percentage REAL NOT NULL,
                classes_attended INT NOT NULL,
                total_classes INT NOT NULL,
                status VARCHAR(50) NOT NULL,
                PRIMARY KEY (student_id, course_code)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS exam_schedule (
                course_code VARCHAR(50) NOT NULL,
                course_name VARCHAR(255) NOT NULL,
                exam_date VARCHAR(50) NOT NULL,
                exam_time VARCHAR(50) NOT NULL,
                venue VARCHAR(100) NOT NULL,
                session VARCHAR(50) NOT NULL,
                PRIMARY KEY (course_code, exam_date)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS company_openings (
                opening_id VARCHAR(50) PRIMARY KEY,
                company_name VARCHAR(255) NOT NULL,
                role_title VARCHAR(255) NOT NULL,
                required_skills TEXT NOT NULL,
                preferred_skills TEXT NOT NULL,
                min_cgpa REAL NOT NULL,
                min_attendance REAL NOT NULL,
                eligible_departments TEXT NOT NULL,
                ctc VARCHAR(100) NOT NULL,
                location VARCHAR(255) NOT NULL,
                positions_open INT NOT NULL,
                deadline VARCHAR(50) NOT NULL,
                description TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS student_skills (
                student_id VARCHAR(50) PRIMARY KEY,
                primary_skills TEXT NOT NULL,
                secondary_skills TEXT NOT NULL,
                certifications TEXT NOT NULL,
                projects TEXT NOT NULL,
                preferred_role VARCHAR(255) NOT NULL,
                placement_status VARCHAR(100) NOT NULL
            );
            """,
        ]

        conn = self._get_pg_connection()
        cur = conn.cursor()
        for ddl in tables_ddl:
            cur.execute(ddl)
        conn.commit()
        cur.close()
        self._put_pg_connection(conn)
        print("[DB Manager] PostgreSQL institutional schema verified.")

    def sync_seed_data_to_postgres(self):
        """
        If PostgreSQL tables are empty, copy all records from local SQLite data/students.db
        into PostgreSQL to guarantee full data availability.
        """
        if not os.path.exists(self.sqlite_path):
            return

        sq_conn = sqlite3.connect(self.sqlite_path)
        sq_cur = sq_conn.cursor()

        pg_conn = self._get_pg_connection()
        pg_cur = pg_conn.cursor()

        for table in self.CORE_TABLES:
            try:
                pg_cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = pg_cur.fetchone()[0]
                if count == 0:
                    sq_cur.execute(f"SELECT * FROM {table}")
                    rows = sq_cur.fetchall()
                    if rows:
                        col_names = [desc[0] for desc in sq_cur.description]
                        cols_joined = ", ".join(col_names)
                        placeholders = ", ".join(["%s"] * len(col_names))
                        insert_sql = f"INSERT INTO {table} ({cols_joined}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                        
                        for row in rows:
                            pg_cur.execute(insert_sql, list(row))
                        pg_conn.commit()
                        print(f"[DB Manager] Synced {len(rows)} rows for '{table}' to PostgreSQL.")
            except Exception as sync_err:
                pg_conn.rollback()
                print(f"[DB Manager] Sync note for '{table}': {sync_err}")

        sq_conn.close()
        pg_cur.close()
        self._put_pg_connection(pg_conn)

    # ══════════════════════════════════════════════════════════════════════════
    # Health & Status Inspection
    # ══════════════════════════════════════════════════════════════════════════

    def get_health_status(self) -> DatabaseHealthStatus:
        """Probe the active database, calculate real latency, and count table records."""
        start_time = time.time()
        connected = False
        table_counts: Dict[str, int] = {}
        total_records = 0
        active_tables = []

        try:
            # Latency ping
            self.execute_query("SELECT 1 AS ping", fetch="one")
            latency_ms = round((time.time() - start_time) * 1000, 2)
            connected = True
        except Exception:
            latency_ms = -1.0
            connected = False

        # Query counts for core tables
        for tbl in self.CORE_TABLES:
            try:
                res = self.execute_query(f"SELECT COUNT(*) as cnt FROM {tbl}", fetch="one")
                count = res.get("cnt", 0) if isinstance(res, dict) else (res[0] if res else 0)
                table_counts[tbl] = count
                total_records += count
                active_tables.append(tbl)
            except Exception:
                pass

        # Identify host
        host_display = None
        db_name = "students.db"
        is_cloud = self.dialect in (DatabaseDialect.POSTGRESQL, DatabaseDialect.SUPABASE)

        if is_cloud and self.db_url:
            parsed = urlparse(self.db_url)
            host_display = parsed.hostname
            db_name = parsed.path.lstrip("/") or "postgres"
        else:
            host_display = "local_filesystem"
            db_name = os.path.basename(self.sqlite_path)

        return DatabaseHealthStatus(
            connected=connected,
            engine=self.active_engine_name,
            dialect=self.dialect,
            database_name=db_name,
            host=host_display,
            latency_ms=latency_ms,
            active_tables=active_tables,
            total_records=total_records,
            is_cloud_hosted=is_cloud,
            last_sync_timestamp=time.time(),
        )

    # ══════════════════════════════════════════════════════════════════════════
    # Dynamic Query Execution
    # ══════════════════════════════════════════════════════════════════════════

    def query_dynamic(self, payload: DynamicQueryPayload) -> Dict[str, Any]:
        """
        Execute a flexible, validated dynamic query across the active database.
        """
        safe_table = re.sub(r"[^a-zA-Z0-9_]", "", payload.table)
        if safe_table not in self.CORE_TABLES and not safe_table.startswith("view_"):
            raise ValueError(f"Table '{safe_table}' is not permitted for dynamic queries.")

        # Build column list safely
        safe_cols = []
        for c in payload.columns:
            if c == "*":
                safe_cols.append("*")
            else:
                safe_cols.append(re.sub(r"[^a-zA-Z0-9_]", "", c))
        cols_sql = ", ".join(safe_cols) if safe_cols else "*"

        # Build WHERE clause
        where_clauses = []
        params = []
        for k, v in payload.filters.items():
            col = re.sub(r"[^a-zA-Z0-9_]", "", k)
            where_clauses.append(f"{col} = ?")
            params.append(v)
        where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

        # Order by
        order_sql = ""
        if payload.order_by:
            clean_order = re.sub(r"[^a-zA-Z0-9_ ]", "", payload.order_by)
            order_sql = f" ORDER BY {clean_order}"

        # Pagination
        limit = min(max(1, payload.limit or 100), 500)
        offset = max(0, payload.offset or 0)
        limit_sql = f" LIMIT {limit} OFFSET {offset}"

        query = f"SELECT {cols_sql} FROM {safe_table}{where_sql}{order_sql}{limit_sql}"
        rows = self.execute_query(query, tuple(params), fetch="all")
        return {
            "table": safe_table,
            "count": len(rows),
            "rows": rows,
            "dialect": self.dialect.value,
            "engine": self.active_engine_name,
        }


# Global Singleton Database Manager Instance
db_manager = DatabaseManager()
