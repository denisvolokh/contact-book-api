import logging
from typing import List

from fastapi import APIRouter, Depends, FastAPI, HTTPException
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


@v1_router.get("/search", response_model=List[schema.Contact])
async def search_v1(text: str, db=Depends(db_session)):  # type: ignore
    """Endpoint to synchronously search contacts"""

    results = search.full_text_seach(session=db, text=text)

    if not results:
        raise HTTPException(404, detail={"error": "Contact not found"})

    return [dict(row) for row in results]


@v2_router.get("/search")
async def search_v2():  # type: ignore
    return "V2"


app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
