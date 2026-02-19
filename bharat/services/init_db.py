import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sentinelops.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Metrics table
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

    # Incidents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        severity TEXT,
        description TEXT,
        node_id INTEGER,
        service_id INTEGER,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

    print("✅ Database initialized")

if __name__ == "__main__":
    init_db()
