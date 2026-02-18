from flask import Blueprint, jsonify
from services.database import get_recent_metrics, get_connection

monitoring_bp = Blueprint("monitoring", __name__)


# =========================================================
# GET /risk/current
# =========================================================
@monitoring_bp.route("/risk/current", methods=["GET"])
def get_current_risk():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT root_cause, severity, created_at
        FROM incidents
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({
            "risk": 0,
            "severity": "LOW",
            "message": "No incidents detected"
        })

    return jsonify({
        "latest_incident": row[0],
        "severity": row[1],
        "timestamp": row[2]
    })


# =========================================================
# GET /health
# =========================================================
@monitoring_bp.route("/health", methods=["GET"])
def get_health():

    metrics = get_recent_metrics(1)

    if not metrics:
        return jsonify({"health": "UNKNOWN"})

    cpu = metrics[0][0]

    health_score = max(0, 100 - cpu)

    if health_score > 70:
        status = "HEALTHY"
    elif health_score > 40:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    return jsonify({
        "health_score": health_score,
        "status": status
    })


# =========================================================
# GET /metrics/recent
# =========================================================
@monitoring_bp.route("/metrics/recent", methods=["GET"])
def get_metrics():

    metrics = get_recent_metrics(20)

    data = []

    for m in metrics:
        data.append({
            "cpu": m[0],
            "memory": m[1],
            "disk": m[2],
            "response_time": m[3],
            "error_rate": m[4]
        })

    return jsonify(data)


# =========================================================
# GET /incidents
# =========================================================
@monitoring_bp.route("/incidents", methods=["GET"])
def get_incidents():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, severity, status, root_cause, created_at
        FROM incidents
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()
    conn.close()

    incidents = []

    for r in rows:
        incidents.append({
            "id": r[0],
            "severity": r[1],
            "status": r[2],
            "root_cause": r[3],
            "created_at": r[4]
        })

    return jsonify(incidents)
