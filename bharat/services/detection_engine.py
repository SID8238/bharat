from bharat.services.incident_service import create_incident
from bharat.services.risk_engine import (
    calculate_failure_probability,
    estimate_time_to_failure,
    sustained_cpu_high,
    HIGH_CPU,
    CRITICAL_CPU
)


def analyze_metrics(metrics):

    cpu = metrics["cpu_usage"]

    risk, future_cpu, progress, warming = calculate_failure_probability(metrics)

    # =====================================================
    # WARM-UP MODE
    # =====================================================
    if warming:
        return {
            "anomaly": False,
            "risk": risk,
            "warmup": True,
            "progress": progress
        }

    eta = estimate_time_to_failure(metrics, future_cpu)

    # =====================================================
    # HARD CRITICAL OVERRIDE
    # =====================================================
    if cpu >= CRITICAL_CPU:

        incident_id = create_incident(
            service_id=metrics["service_id"],
            node_id=metrics["node_id"],
            severity="CRITICAL",
            root_cause=f"CPU extreme overload ({cpu:.1f}%)"
        )

        return {
            "anomaly": True,
            "severity": "CRITICAL",
            "risk": max(risk, 90),
            "eta_minutes": eta or 2,
            "incident_id": incident_id
        }

    # =====================================================
    # Sustained High CPU
    # =====================================================
    if sustained_cpu_high():

        incident_id = create_incident(
            service_id=metrics["service_id"],
            node_id=metrics["node_id"],
            severity="HIGH",
            root_cause=f"Sustained high CPU ({cpu:.1f}%)"
        )

        return {
            "anomaly": True,
            "severity": "HIGH",
            "risk": max(risk, 75),
            "eta_minutes": eta or 10,
            "incident_id": incident_id
        }

    # =====================================================
    # Normal Risk Logic
    # =====================================================
    if risk >= 70:

        incident_id = create_incident(
            service_id=metrics["service_id"],
            node_id=metrics["node_id"],
            severity="HIGH",
            root_cause=f"Failure Risk {risk:.1f}%"
        )

        return {
            "anomaly": True,
            "severity": "HIGH",
            "risk": risk,
            "eta_minutes": eta,
            "incident_id": incident_id
        }

    return {
        "anomaly": False,
        "risk": risk
    }
