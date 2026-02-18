# services/health_service.py

import psutil
from datetime import datetime


def get_system_health():
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
