"""
Scheduler package for KrishiMitra AI.
"""
from scheduler.tasks import (
    check_sources_health_task,
    discover_new_circulars_task,
    detect_amendments_task,
    retry_failed_documents_task
)
