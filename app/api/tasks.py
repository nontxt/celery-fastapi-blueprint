from fastapi import APIRouter

from app.tasks.example import example_task

router = APIRouter()


@router.post("/run-task/")
async def run_task():
    """Trigger an example Celery task."""
    task = example_task.delay()
    return {"task_id": task.id, "status": "Task submitted"}
