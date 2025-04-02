from fastapi import APIRouter, Query

from app.tasks.example import example_task, run_group

router = APIRouter()


@router.post("/run-task", description="Trigger an example Celery task.")
async def run_task():
    task = example_task.delay()
    return {"task_id": task.id, "status": "Task submitted"}


@router.post("/run-group", description="Trigger a group of Celery tasks.")
async def run_masks_success_endpoint(raise_error: bool = Query(False)):
    task_id = run_group(raise_error)
    return {
        "status": "Group tasks submitted successfully",
        "task_id": task_id,
        "raise_error": raise_error,
    }
