import logging

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routers.base import api_router
from api.utils import models
from api.utils.database import check_db_connected, check_db_disconnected, engine

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables() -> None:
    models.Base.metadata.create_all(bind=engine)


def include_routers(app: FastAPI) -> None:
    app.include_router(api_router, prefix="/api")


def start_application() -> FastAPI:
    app = FastAPI(
        title="Contact Book API",
        description="A simple API to manage contacts",
        version="0.0.1",
        docs_url="/swagger",
    )
    create_tables()
    include_routers(app)

    return app


app = start_application()


@app.on_event("startup")
async def app_startup() -> None:
    await check_db_connected()


@app.on_event("shutdown")
async def app_shutdown() -> None:
    await check_db_disconnected()
