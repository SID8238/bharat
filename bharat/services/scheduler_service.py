import time
import logging

from services.metrics_services import collect_metrics
from services.detection_engine import analyze_metrics
from services.remediation_service import trigger_remediation


# =========================================================
# Logger (minimal — terminal is main output)
# =========================================================
logging.basicConfig(level=logging.WARNING)

INTERVAL = 5  # seconds


# =========================================================
# Pretty Terminal Output
# =========================================================
def print_header():
    print("\n" + "=" * 60)
    print("🚀 SentinelOps — Live Monitoring Console")
    print("=" * 60)


def print_metrics(metrics):
    print(
        f"📊 CPU: {metrics['cpu_usage']:.1f}% | "
        f"MEM: {metrics['memory_usage']:.1f}% | "
        f"DISK: {metrics['disk_usage']:.1f}% | "
        f"ERR: {metrics['error_rate']:.3f}"
    )


def print_warmup(progress):
    print(f"🟡 WARM-UP MODE — Collecting data ({progress:.0f}%)")


def print_healthy(risk):
    print(f"🟢 System Healthy — Risk: {risk:.1f}%")


def print_incident(incident_id, severity, risk, eta):
    eta_text = f"{eta} min" if eta is not None else "Unknown"

    print("\n🚨 INCIDENT DETECTED")
    print("-" * 40)
    print(f"ID: {incident_id}")
    print(f"Severity: {severity}")
    print(f"Risk Score: {risk:.1f}%")
    print(f"ETA to Failure: {eta_text}")


def print_remediation(remediation):
    print("🛠️ Remediation Action:")
    print(remediation)


# =========================================================
# Main Scheduler Loop
# =========================================================
def start_scheduler():

    print_header()

    while True:

        cycle_start = time.time()

        try:
            # -------------------------------------------------
            # Step 1 — Collect metrics
            # -------------------------------------------------
            metrics = collect_metrics()

            if not metrics:
                print("⚠️ No metrics collected")
                time.sleep(INTERVAL)
                continue

            print_metrics(metrics)

            # -------------------------------------------------
            # Step 2 — ML Analysis
            # -------------------------------------------------
            result = analyze_metrics(metrics)

            # -------------------------------------------------
            # Incident Handling
            # -------------------------------------------------
            if result.get("anomaly"):

                severity = result.get("severity")
                incident_id = result.get("incident_id")
                risk = result.get("risk", 0)
                eta = result.get("eta_minutes")

                print_incident(incident_id, severity, risk, eta)

                remediation = trigger_remediation(
                    severity=severity,
                    service_id=metrics.get("service_id"),
                    node_id=metrics.get("node_id")
                )

                print_remediation(remediation)

            # -------------------------------------------------
            # Warm-Up Mode
            # -------------------------------------------------
            elif result.get("warmup"):

                progress = result.get("progress", 0)
                print_warmup(progress)

            # -------------------------------------------------
            # Healthy Mode
            # -------------------------------------------------
            else:

                print_healthy(result.get("risk", 0))

        except Exception as e:
            print(f"❌ Scheduler error: {e}")

        # -------------------------------------------------
        # Maintain interval
        # -------------------------------------------------
        elapsed = time.time() - cycle_start
        sleep_time = max(0, INTERVAL - elapsed)

        time.sleep(sleep_time)
