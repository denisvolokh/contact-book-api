from fastapi import APIRouter

from api.routers.v1 import routers as v1_router
from api.routers.v2 import routers as v2_router

api_router = APIRouter()
api_router.include_router(v1_router.router, prefix="/v1", tags=["synch"])
api_router.include_router(v2_router.router, prefix="/v2", tags=["asynch"])
