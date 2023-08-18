import logging
from typing import List

import tasks
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.responses import JSONResponse
from utils import models, schema, search
from utils.database import SessionLocal, engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Contact Book API",
    description="A simple API to manage contacts",
    version="0.0.1",
    docs_url="/swagger",
)

v1_router = APIRouter()
v2_router = APIRouter()


def db_session() -> SessionLocal:
    """Create a new session for each request.

    Returns:
        SessionLocal: A new session.

    Yields:
        Iterator[SessionLocal]: A new session.
    """

    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup():  # type: ignore
    from tasks import task_update_contacts

    task_update_contacts.apply_async(countdown=60)


@app.on_event("shutdown")
async def shutdown():  # type: ignore
    logger.info("Shutting down...")


@app.exception_handler(ResponseValidationError)
async def validation_exception_handler(
    request: Request, exc: ResponseValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body},
    )


@v1_router.get("/search", response_model=List[schema.Contact])
async def search_v1(text: str, db=Depends(db_session)):  # type: ignore
    """Endpoint to synchronously search contacts"""

    results = search.full_text_search(session=db, text=text)

    if not results:
        raise HTTPException(404, detail={"error": "Contact not found"})

    return [dict(row) for row in results]


@v2_router.get("/search", response_model=schema.TaskStatus)
async def search_v2(text: str):  # type: ignore
    """Endpoint to asynchronously search contacts"""

    task = tasks.task_full_text_search.apply_async(args=[text])

    return {"task_id": task.id, "task_status": task.state}


@v2_router.get(
    "/search/status/{task_id}",
    response_model=schema.TaskResult,
    response_model_exclude_none=True,
)
async def get_task_status(task_id: str):  # type: ignore
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


app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
