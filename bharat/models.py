from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# =========================================================
# METRICS TABLE
# =========================================================
class Metric(db.Model):

    __tablename__ = "metrics"

    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.String, nullable=False)

    node_id = db.Column(db.Integer, nullable=False)
    service_id = db.Column(db.Integer, nullable=False)

    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    disk_usage = db.Column(db.Float)

    response_time_ms = db.Column(db.Float)
    error_rate = db.Column(db.Float)

    def __repr__(self):
        return (
            f"<Metric id={self.id} "
            f"CPU={self.cpu_usage}% MEM={self.memory_usage}%>"
        )


# =========================================================
# INCIDENTS TABLE
# =========================================================
class Incident(db.Model):

    __tablename__ = "incidents"

    id = db.Column(db.Integer, primary_key=True)

    service_id = db.Column(db.Integer, nullable=False)
    node_id = db.Column(db.Integer, nullable=False)

    severity = db.Column(db.String(50))
    root_cause = db.Column(db.String(255))

    status = db.Column(db.String(50), default="OPEN")

    created_at = db.Column(db.String, nullable=False)

    # IMPORTANT — used by resolve_incident()
    resolved_at = db.Column(db.String, nullable=True)

    def __repr__(self):
        return (
            f"<Incident id={self.id} "
            f"severity={self.severity} status={self.status}>"
        )
