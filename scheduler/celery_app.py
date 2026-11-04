"""
Celery and Celery Beat configuration for KrishiMitra AI.
Defines cron intervals for:
- Daily source health checks
- Automated circular & GO discovery
- Deadline & amendment detection
- Failed document retry queue
"""

import os
from celery import Celery
from celery.schedules import crontab

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("krishimitra", broker=REDIS_URL, backend=REDIS_URL)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    beat_schedule={
        "daily-source-health-check": {
            "task": "scheduler.tasks.check_sources_health_task",
            "schedule": crontab(hour="*/6", minute=0),
        },
        "daily-circular-discovery": {
            "task": "scheduler.tasks.discover_new_circulars_task",
            "schedule": crontab(hour=2, minute=30),
        },
        "weekly-amendment-and-deadline-detection": {
            "task": "scheduler.tasks.detect_amendments_task",
            "schedule": crontab(day_of_week="sunday", hour=4, minute=0),
        },
        "retry-failed-documents": {
            "task": "scheduler.tasks.retry_failed_documents_task",
            "schedule": crontab(hour="*/12", minute=15),
        }
    }
)
