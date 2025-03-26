from typing import Callable

from fastapi import FastAPI
from loguru import logger

# from findex.services.models import HousePriceModel


def _startup_routine(app: FastAPI) -> None:
    # model_path = DEFAULT_MODEL_PATH
    # model_instance = HousePriceModel(model_path)
    # app.state.model = model_instance
    pass


def _shutdown_model(app: FastAPI) -> None:
    # app.state.model = None
    pass


def start_app_handler(app: FastAPI) -> Callable:
    def startup() -> None:
        logger.info("Running app start handler.")
        # _startup_routine(app)
    return startup


def stop_app_handler(app: FastAPI) -> Callable:
    def shutdown() -> None:
        logger.info("Running app shutdown handler.")
        _shutdown_model(app)
    return shutdown
