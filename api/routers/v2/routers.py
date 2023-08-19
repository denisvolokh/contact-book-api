from fastapi import APIRouter

from api import tasks
from api.utils import schema

router = APIRouter()


@router.get("/search", response_model=schema.TaskStatus)
def get_search(text: str):  # type: ignore
    """Endpoint to asynchronously search contacts"""

    task = tasks.task_full_text_search.apply_async(args=[text])

    return {"task_id": task.id, "task_status": task.state}


@router.get(
    "/search/status/{task_id}",
    response_model=schema.TaskResult,
    response_model_exclude_none=True,
)
def get_task_status(task_id: str):  # type: ignore
    """Endpoint to get the status of a task and results if completed"""

    task = tasks.task_full_text_search.AsyncResult(task_id)

    if task.state == "PENDING":
        response = {"state": task.state, "status": "Task is pending!"}
    elif task.state != "FAILURE":
        response = {"state": task.state, "result": task.result or []}
    else:
        # task failed
        response = {"state": task.state, "status": str(task.info)}

    return response
