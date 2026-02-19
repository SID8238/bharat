# services/api.py

from fastapi import FastAPI
from bharat.services.metrics_services import collect_metrics, simulate_cpu_spike
from bharat.services.scheduler_service import start_scheduler
from bharat.services.database import get_incidents
from bharat.services.health_service import get_system_health
import threading

app = FastAPI(title="SentinelOps API")


# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return get_system_health()


# -----------------------------
# Get Metrics
# -----------------------------
@app.get("/metrics")
def metrics():
    data = collect_metrics()
    return {"latest_metrics": data}


# -----------------------------
# Get Incidents
# -----------------------------
@app.get("/incidents")
def incidents():
    return {"incidents": get_incidents()}


# -----------------------------
# Simulate Failure
# -----------------------------
@app.post("/simulate-spike")
def simulate_spike():
    simulate_cpu_spike(10)
    return {"message": "CPU spike simulation started"}


# -----------------------------
# Run monitoring loop manually
# -----------------------------
@app.post("/run-once")
def run_once():
    thread = threading.Thread(target=start_scheduler, daemon=True)
    thread.start()
    return {"message": "Monitoring loop started in background"}
