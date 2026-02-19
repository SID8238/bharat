from bharat.services.ml_engine import (
    train_anomaly_model,
    detect_anomaly,
    forecast_cpu
)
from bharat.services.database import get_recent_metrics


# =========================================================
# Thresholds
# =========================================================
HIGH_CPU = 80
CRITICAL_CPU = 90
MEM_CRITICAL = 90
ERROR_CRITICAL = 0.1

SUSTAINED_COUNT = 3


# =========================================================
# Warm-Up Configuration
# =========================================================
WARMUP_SAMPLES = 360   # ≈ 30 minutes at 5-sec interval


# =========================================================
# Warm-Up Status
# =========================================================
def warmup_status():

    history = get_recent_metrics(WARMUP_SAMPLES)
    count = len(history)

    progress = min(100, (count / WARMUP_SAMPLES) * 100)

    return count < WARMUP_SAMPLES, progress


# =========================================================
# Current Stress Score
# =========================================================
def calculate_current_risk(metrics):

    score = 0

    score += min(metrics["cpu_usage"] / CRITICAL_CPU, 1.0) * 30
    score += min(metrics["memory_usage"] / MEM_CRITICAL, 1.0) * 25
    score += min(metrics["error_rate"] / ERROR_CRITICAL, 1.0) * 25
    score += min(metrics["response_time_ms"] / 500, 1.0) * 20

    return score


# =========================================================
# Sustained High CPU Detection
# =========================================================
def sustained_cpu_high():

    history = get_recent_metrics(SUSTAINED_COUNT)

    if len(history) < SUSTAINED_COUNT:
        return False

    cpu_values = [row[0] for row in history]

    return all(cpu >= HIGH_CPU for cpu in cpu_values)


# =========================================================
# Failure Probability Calculation
# =========================================================
def calculate_failure_probability(metrics):

    risk_score = calculate_current_risk(metrics)

    # -----------------------------
    # Warm-Up Check
    # -----------------------------
    warming, progress = warmup_status()

    if warming:
        return risk_score, None, progress, True

    future_cpu = None

    # -----------------------------
    # Anomaly contribution
    # -----------------------------
    model = train_anomaly_model()

    if detect_anomaly(model, metrics):
        risk_score += 20

    # -----------------------------
    # Forecast contribution
    # -----------------------------
    future_cpu = forecast_cpu()

    if future_cpu is not None:
        forecast_risk = min(future_cpu / CRITICAL_CPU, 1.0) * 30
        risk_score += forecast_risk

    risk_score = min(risk_score, 100)

    return risk_score, future_cpu, 100, False


# =========================================================
# Time-to-Failure Estimation
# =========================================================
def estimate_time_to_failure(metrics, future_cpu):

    current_cpu = metrics["cpu_usage"]

    if sustained_cpu_high():
        return 10

    if current_cpu >= CRITICAL_CPU:
        return 2

    if current_cpu >= 85:
        return 5

    if current_cpu >= HIGH_CPU:
        return 15

    if future_cpu is not None:

        if future_cpu <= current_cpu:
            return None

        cpu_gap = future_cpu - current_cpu

        if cpu_gap < 5:
            return 60

        if cpu_gap < 15:
            return 30

        return 10

    return None
