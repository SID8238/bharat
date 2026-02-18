import logging
from datetime import datetime

logger = logging.getLogger("REMEDIATION")
logger.setLevel(logging.INFO)


# =========================================================
# Restart Service (Simulated)
# =========================================================
def restart_service(service_id, node_id):

    logger.info(
        f"Restarting service {service_id} on node {node_id}"
    )

    return {
        "action": "restart_service",
        "status": "success",
        "service_id": service_id,
        "node_id": node_id,
        "timestamp": datetime.utcnow().isoformat()
    }


# =========================================================
# Scale Service (Simulated)
# =========================================================
def scale_service(service_id, replicas=2):

    logger.info(
        f"Scaling service {service_id} to {replicas} replicas"
    )

    return {
        "action": "scale_service",
        "status": "success",
        "service_id": service_id,
        "replicas": replicas,
        "timestamp": datetime.utcnow().isoformat()
    }


# =========================================================
# Emergency Shutdown (for CRITICAL)
# =========================================================
def emergency_shutdown(service_id, node_id):

    logger.warning(
        f"Emergency shutdown for service {service_id} on node {node_id}"
    )

    return {
        "action": "emergency_shutdown",
        "status": "success",
        "service_id": service_id,
        "node_id": node_id,
        "timestamp": datetime.utcnow().isoformat()
    }


# =========================================================
# Main Remediation Decision Engine
# =========================================================
def trigger_remediation(severity, service_id, node_id):

    # CRITICAL → strongest action
    if severity == "CRITICAL":
        return emergency_shutdown(service_id, node_id)

    # HIGH → restart service
    if severity == "HIGH":
        return restart_service(service_id, node_id)

    # MEDIUM → scale service
    if severity == "MEDIUM":
        return scale_service(service_id, replicas=2)

    # LOW → no action
    return {
        "action": "none",
        "status": "no_action_needed",
        "service_id": service_id,
        "node_id": node_id,
        "timestamp": datetime.utcnow().isoformat()
    }
