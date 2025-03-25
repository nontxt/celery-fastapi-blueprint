import time

from celery_app.celery import celery_app


@celery_app.task
def example_task():
    """Simple example task."""
    time.sleep(5)  # Simulate some work
    return "Task executed successfully"


@celery_app.task
def scheduled_task():
    """Scheduled task that runs every 5 minutes."""
    time.sleep(5)  # Simulate some work
    return "Scheduled task executed"
