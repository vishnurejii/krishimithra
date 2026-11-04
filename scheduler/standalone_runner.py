"""
Standalone Scheduled Runner for Windows / Local Environment.
Runs periodic discovery, health checking, and retry tasks without external Redis dependency.
"""

import time
import threading
from scheduler.tasks import (
    check_sources_health_task,
    discover_new_circulars_task,
    detect_amendments_task,
    retry_failed_documents_task
)
from core.logger import get_logger

logger = get_logger("krishimitra.scheduler.runner")

def run_schedule_loop(interval_seconds: int = 3600):
    """Continuous background loop running scheduled cycles."""
    logger.info(f"Starting KrishiMitra Standalone Scheduler (cycle interval: {interval_seconds}s)...")
    while True:
        try:
            logger.info("--- Triggering Scheduled KrishiMitra Maintenance Cycle ---")
            check_sources_health_task()
            discover_new_circulars_task()
            detect_amendments_task()
            retry_failed_documents_task()
            logger.info("--- Scheduled Maintenance Cycle Complete ---")
        except Exception as e:
            logger.error(f"Error in scheduler loop: {e}")

        time.sleep(interval_seconds)

if __name__ == "__main__":
    run_schedule_loop(interval_seconds=1800)
