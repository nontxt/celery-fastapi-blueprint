import time

from celery import Task, group
from celery.exceptions import WorkerLostError
from celery.result import GroupResult, states

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


@celery_app.task(bind=True)
def group_task(self: Task, task_id, raise_error=False):
    """Example task that simulates a group of tasks with error handling."""
    time.sleep(1)  # !!THIS SLEEP IS VERY IMPORTANT TO SAVE GROUP RESULTS IN REDIS BACKEND

    print(f"Running task {task_id}")
    print(f"Task ID: {self.request.id}, Group ID: {self.request.group}")
    try:

        if raise_error and task_id == 2:  # Emulate an error for task 2
            raise ValueError("Simulated error in task 2")

        time.sleep(1000)

        return f"Task {task_id} completed successfully"

    except WorkerLostError:
        print(f"Worker lost for task {task_id}")

    except Exception as e:
        print(f"Error in task {task_id}: {e}")

        self.update_state(state=states.FAILURE, meta={"exc_type": str(type(e)), "exc_message": str(e)})
        cancel_remaining_tasks(self.request)
        raise e


def cancel_remaining_tasks(request):
    """Revoke all tasks in the group except the one that raised an error"""
    task_id = request.id
    group_id = request.group
    group_result: GroupResult = GroupResult.restore(group_id)

    print(f"Revoking group {group_id} from task {task_id}")

    if not group_result:
        print(f"Group {group_id} not found in the backend")
        return

    if not group_result.children:
        print(f"Active tasks in group {group_id} not found")
        return

    print(f"Revoking tasks in group {group_id}:")

    for task in group_result.children:
        if task.id != task_id:
            print(f"Revoking task {task.id}")
            task.revoke(terminate=True, signal="SIGKILL")


@celery_app.task
def success_callback() -> str:
    """Success callback for group of tasks"""
    print(f"Success callback triggered")

    message = "Tasks completed successfully"
    print(message)

    return message


@celery_app.task
def error_callback(request, exc, traceback) -> str:
    """Failure callback for group of tasks"""
    print(f"Error callback triggered")

    message = f"Tasks failed with error: {exc}"
    print(message)

    return message


def run_group(raise_error=False):
    """Run a group of mask tasks"""

    tasks = group([group_task.s(i, raise_error=raise_error) for i in range(150)])
    tasks.link(success_callback.s())
    tasks.link_error(error_callback.s())
    group_result = tasks.apply_async()
    group_result.save()

    return group_result.id
