from fastapi import FastAPI
from api.router import api_router
from fastapi_core.config import API_PREFIX, APP_NAME, APP_VERSION, IS_DEBUG, configure_static
from fastapi_core.event_handlers import start_app_handler, stop_app_handler
from fastapi.responses import RedirectResponse


import mlAPI.ml_scripts
import mlAPI.etl  
from etl import ETL_FUNCTIONS  

AVAILABLE_MODELS = {
    "random_forest": "Random Forest",
}


def get_app() -> FastAPI:
    fast_app = FastAPI(title=APP_NAME, version=APP_VERSION, debug=IS_DEBUG)
    fast_app.include_router(api_router, prefix=API_PREFIX) #should be pages and api separated, but api for now

    fast_app.add_event_handler("startup", start_app_handler(fast_app))
    fast_app.add_event_handler("shutdown", stop_app_handler(fast_app))

    return fast_app

app = get_app()
configure_static(app)

@app.get("/")
async def root():
    return RedirectResponse(url=f"/api/datasets", status_code=303)
