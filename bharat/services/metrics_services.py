import psutil
import time
import threading
import multiprocessing
import logging
from datetime import datetime
import random

from bharat.services.database import insert_metrics


# =========================================================
# Logging Configuration
# =========================================================
logger = logging.getLogger("METRICS")
logger.setLevel(logging.INFO)


# =========================================================
# Static identifiers (prototype)
# =========================================================
NODE_ID = 1
SERVICE_ID = 1


# =========================================================
# Metric Helper Functions
# =========================================================
def get_cpu_metrics():
    return {
        "cpu_usage": psutil.cpu_percent(interval=1),
        "core_count": psutil.cpu_count()
    }


def get_memory_metrics():
    mem = psutil.virtual_memory()
    return {
        "memory_usage": mem.percent,
        "total_memory_mb": mem.total // (1024 * 1024)
    }


def get_disk_metrics():
    disk = psutil.disk_usage('/')
    return {
        "disk_usage": disk.percent
    }


def get_network_metrics():
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_received": net.bytes_recv
    }


# =========================================================
# Mock Application Metrics (Simulated)
# =========================================================
def get_application_metrics():
    return {
        "response_time_ms": random.randint(80, 200),
        "error_rate": round(random.uniform(0.0, 0.05), 3),
        "request_count": random.randint(100, 500),
        "db_query_count": random.randint(50, 300),
        "cache_hit_ratio": round(random.uniform(0.7, 0.99), 2),
        "network_throughput_mbps": random.randint(50, 300),
        "bandwidth_usage_percent": random.randint(20, 80)
    }


# =========================================================
# Main Collector Function
# =========================================================
def collect_metrics():

    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_id": NODE_ID,
            "service_id": SERVICE_ID
        }

        metrics.update(get_cpu_metrics())
        metrics.update(get_memory_metrics())
        metrics.update(get_disk_metrics())
        metrics.update(get_network_metrics())
        metrics.update(get_application_metrics())

        # Save only fields DB expects
        insert_metrics(metrics)

        logger.info(
            f"Metrics collected: CPU {metrics['cpu_usage']}%, "
            f"MEM {metrics['memory_usage']}%"
        )

        return metrics

    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        return None


# =========================================================
# CPU Spike Simulation (MULTI-CORE)
# =========================================================
def simulate_cpu_spike(duration=15):

    logger.warning("Starting HIGH CPU spike simulation")

    def burn():
        end = time.time() + duration
        while time.time() < end:
            pass

    processes = []

    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=burn)
        p.start()
        processes.append(p)

    return {"status": "High CPU spike started"}


# =========================================================
# Memory Spike Simulation
# =========================================================
def simulate_memory_spike(duration=15):

    logger.warning("Starting MEMORY spike simulation")

    def allocate():
        big = []
        end = time.time() + duration

        while time.time() < end:
            big.append("X" * 10_000_000)

    thread = threading.Thread(target=allocate)
    thread.start()

    return {"status": "Memory spike started"}


# =========================================================
# Standalone Test Runner
# =========================================================
if __name__ == "__main__":

    while True:
        data = collect_metrics()
        print(data)
        time.sleep(5)
