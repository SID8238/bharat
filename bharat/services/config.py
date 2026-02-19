import os

# =========================================================
# Project Root
# =========================================================
# This file is in bharat/services/config.py
# BASE_DIR should be the bharat/ directory
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

# =========================================================
# Database Configuration
# =========================================================
# Single source of truth for the DB path
DB_PATH = os.path.join(BASE_DIR, "sentinelops.db")

# =========================================================
# Scheduler Configuration
# =========================================================
METRIC_COLLECTION_INTERVAL = 5  # seconds

# =========================================================
# Resource Thresholds
# =========================================================
HIGH_CPU = 80
CRITICAL_CPU = 90
MEMORY_THRESHOLD = 85
MEM_CRITICAL = 90
ERROR_RATE_THRESHOLD = 0.05
ERROR_CRITICAL = 0.1

# =========================================================
# Risk Engine Configuration
# =========================================================
SUSTAINED_COUNT = 3

# =========================================================
# Forecast Configuration
# =========================================================
FORECAST_WINDOW = 30

# =========================================================
# Remediation Configuration
# =========================================================
DEFAULT_SCALE_REPLICAS = 2

# =========================================================
# System Metadata
# =========================================================
SYSTEM_NAME = "SentinelOps"
VERSION = "1.0"
