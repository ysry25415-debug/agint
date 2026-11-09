"""
Celery application setup for Product Hunter AI.
"""

from celery import Celery
from datetime import timedelta

from backend.app.core.config import settings

celery_app = Celery(
    "product_hunter",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB + 1}",
    include=["worker.tasks.agents"],
)

# Beat schedule for daily tasks
celery_app.conf.beat_schedule = {
    "daily-research-pipeline": {
        "task": "worker.tasks.agents.run_daily_pipeline",
        "schedule": timedelta(hours=24),
        "args": (),
    },
    "health-check-agents": {
        "task": "worker.tasks.agents.health_check_sources",
        "schedule": timedelta(hours=1),
        "args": (),
    },
}

celery_app.conf.timezone = "UTC"
celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 3600
celery_app.conf.task_soft_time_limit = 3300
celery_app.conf.worker_max_tasks_per_child = 100

# Result backend settings
celery_app.conf.result_backend_transport_options = {
    "visibility_timeout": 3600,
}

# Task routing
celery_app.conf.task_routes = {
    "worker.tasks.agents.run_daily_pipeline": {"queue": "research"},
    "worker.tasks.agents.health_check_sources": {"queue": "monitoring"},
}


if __name__ == "__main__":
    celery_app.worker_main()