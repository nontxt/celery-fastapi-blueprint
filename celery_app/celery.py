import os

from celery import Celery

# Read configuration from environment variables
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks.example"],  # Auto-import tasks
)

# Configure Celery
celery_app.conf.update(
    task_track_started=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    result_expires=300,  # 5 min expiration time for results
    result_backend_transport_options={
        "visibility_timeout": 300
    },  # 5 min visibility timeout for
)

# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#entries
celery_app.conf.beat_schedule = {
    # "scheduled_task": {
    #     "task": "app.tasks.example.scheduled_task",
    #     "schedule": crontab(minute="*/1"),  # Every 1 minutes
    # },
    # "every-10-seconds": {  # Name of the task / label
    #     "task": "app.tasks.example.scheduled_task",
    #     "schedule": 10.0,  # Every 10 seconds
    # },
}

# https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-routes
celery_app.conf.task_routes = {"app.tasks.example.scheduled_task": "periodic"}
