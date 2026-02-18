import pandas as pd
import logging
import time

from sklearn.ensemble import IsolationForest
from prophet import Prophet

from services.database import get_recent_metrics


# =========================================================
# Silence Prophet / CmdStan logs
# =========================================================
logging.getLogger("prophet").setLevel(logging.CRITICAL)
logging.getLogger("cmdstanpy").setLevel(logging.CRITICAL)

logger = logging.getLogger("ML_ENGINE")
logger.setLevel(logging.INFO)


# =========================================================
# GLOBAL MODEL CACHE
# =========================================================
_anomaly_model = None
_forecast_model = None
_last_train_time = 0

# Retrain interval (seconds)
RETRAIN_INTERVAL = 300   # 5 minutes


# =========================================================
# Train Isolation Forest (cheap)
# =========================================================
def train_anomaly_model():

    global _anomaly_model

    history = get_recent_metrics(200)

    if len(history) < 50:
        return None

    try:
        df = pd.DataFrame(history, columns=[
            "cpu", "memory", "disk", "response_time", "error_rate"
        ])

        model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        model.fit(df)

        _anomaly_model = model
        return model

    except Exception as e:
        logger.error(f"Anomaly model training failed: {e}")
        return None


# =========================================================
# Detect anomaly using cached model
# =========================================================
def detect_anomaly(model, metrics):

    if model is None:
        return False

    try:
        data = pd.DataFrame([{
            "cpu": metrics["cpu_usage"],
            "memory": metrics["memory_usage"],
            "disk": metrics["disk_usage"],
            "response_time": metrics["response_time_ms"],
            "error_rate": metrics["error_rate"]
        }])

        prediction = model.predict(data)

        return prediction[0] == -1

    except Exception as e:
        logger.error(f"Anomaly detection failed: {e}")
        return False


# =========================================================
# Train Prophet Forecast Model (EXPENSIVE)
# =========================================================
def _train_forecast_model():

    history = get_recent_metrics(200)

    if len(history) < 30:
        return None

    try:
        cpu_values = [row[0] for row in history]

        df = pd.DataFrame({
            "ds": pd.date_range(
                end=pd.Timestamp.now(),
                periods=len(cpu_values),
                freq="min"
            ),
            "y": cpu_values
        })

        model = Prophet(
            yearly_seasonality=False,
            weekly_seasonality=False,
            daily_seasonality=False
        )

        model.fit(df)

        return model

    except Exception as e:
        logger.error(f"Forecast model training failed: {e}")
        return None


# =========================================================
# Forecast CPU with caching
# =========================================================
def forecast_cpu():

    global _forecast_model, _last_train_time

    now = time.time()

    # -----------------------------------------------------
    # Retrain only periodically
    # -----------------------------------------------------
    if (
        _forecast_model is None or
        now - _last_train_time > RETRAIN_INTERVAL
    ):
        logger.info("Retraining forecast model...")

        model = _train_forecast_model()

        if model:
            _forecast_model = model
            _last_train_time = now
        else:
            return None

    # -----------------------------------------------------
    # Predict future CPU
    # -----------------------------------------------------
    try:
        future = _forecast_model.make_future_dataframe(
            periods=30,
            freq="min"
        )

        forecast = _forecast_model.predict(future)

        future_cpu = forecast["yhat"].tail(30).mean()

        # Clamp to realistic range
        future_cpu = max(0, min(100, future_cpu))

        return float(future_cpu)

    except Exception as e:
        logger.error(f"CPU forecasting failed: {e}")
        return None
