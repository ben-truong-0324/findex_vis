from fastapi import APIRouter
from api.routes import datasets, etl, models # infer, \
                            #admin, status, monitor

api_router = APIRouter()
api_router.include_router(datasets.router, tags=["datasets"], prefix="/datasets")
api_router.include_router(etl.router, tags=["etl"], prefix="/etl")
api_router.include_router(models.router, tags=["models"], prefix="/models")

