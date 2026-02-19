from datetime import datetime
from bharat.services.database import get_connection


# =========================================================
# Create Incident
# =========================================================
def create_incident(service_id, node_id, severity, root_cause="Unknown"):

    conn = get_connection()
    cursor = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO incidents (
            created_at,
            status,
            severity,
            service_id,
            node_id,
            root_cause
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            created_at,
            "OPEN",
            severity,
            service_id,
            node_id,
            root_cause
        )
    )

    conn.commit()

    incident_id = cursor.lastrowid

    conn.close()

    return incident_id


# =========================================================
# Resolve Incident
# =========================================================
def resolve_incident(incident_id):

    conn = get_connection()
    cursor = conn.cursor()

    resolved_at = datetime.utcnow().isoformat()

    cursor.execute(
        """
        UPDATE incidents
        SET status=?, resolved_at=?
        WHERE id=?
        """,
        ("RESOLVED", resolved_at, incident_id)
    )

    conn.commit()
    conn.close()

    return {"incident_id": incident_id, "status": "RESOLVED"}


# =========================================================
# Get All Incidents
# =========================================================
def get_all_incidents():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, severity, status, service_id,
               node_id, root_cause, created_at, resolved_at
        FROM incidents
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    incidents = []

    for r in rows:
        incidents.append({
            "id": r[0],
            "severity": r[1],
            "status": r[2],
            "service_id": r[3],
            "node_id": r[4],
            "root_cause": r[5],
            "created_at": r[6],
            "resolved_at": r[7]
        })

    return incidents
