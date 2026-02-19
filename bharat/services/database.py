import sqlite3
from contextlib import contextmanager
from pathlib import Path

# =========================================================
# Database Path (ALWAYS inside this folder)
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sentinelops.db"


# =========================================================
# Initialize Database (auto-create tables)
# =========================================================
def init_db():

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # ---------------- Metrics Table ----------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            node_id INTEGER,
            service_id INTEGER,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            response_time_ms REAL,
            error_rate REAL
        )
        """)

        # ---------------- Incidents Table ----------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            status TEXT,
            severity TEXT,
            service_id INTEGER,
            node_id INTEGER,
            root_cause TEXT
        )
        """)

        conn.commit()


# Initialize DB automatically on import
init_db()


# =========================================================
# Connection Helper
# =========================================================
def get_connection():

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# Cursor Context Manager
# =========================================================
@contextmanager
def get_cursor():

    conn = get_connection()
    cursor = conn.cursor()

    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# =========================================================
# Insert Metrics
# =========================================================
def insert_metrics(metrics: dict):

    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO metrics (
                timestamp, node_id, service_id,
                cpu_usage, memory_usage, disk_usage,
                response_time_ms, error_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metrics["timestamp"],
            metrics["node_id"],
            metrics["service_id"],
            metrics["cpu_usage"],
            metrics["memory_usage"],
            metrics["disk_usage"],
            metrics["response_time_ms"],
            metrics["error_rate"]
        ))


# =========================================================
# Fetch Recent Metrics
# =========================================================
def get_recent_metrics(limit=50):

    with get_cursor() as cursor:
        cursor.execute("""
            SELECT cpu_usage, memory_usage, disk_usage,
                   response_time_ms, error_rate
            FROM metrics
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        return [tuple(row) for row in rows]


# =========================================================
# Insert Incident
# =========================================================
def insert_incident(created_at, status, severity, service_id, node_id, root_cause):

    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO incidents
            (created_at, status, severity, service_id, node_id, root_cause)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            created_at,
            status,
            severity,
            service_id,
            node_id,
            root_cause
        ))


# =========================================================
# Fetch Incidents
# =========================================================
def get_incidents():

    with get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM incidents
            ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        return [dict(row) for row in rows]
