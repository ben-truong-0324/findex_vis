# mlAPI/routes/ml_routes.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os

from mlAPI.ml import run_prediction
from mlAPI.schemas.ml_schemas import PredictionRequest

router = APIRouter()
DATA_DIR = "/app/data"

@router.get("/data-files")
def list_data_files():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
        return {"data_files": files}
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "Data folder not found"})

@router.post("/run-prediction")
def predict(request: PredictionRequest):
    try:
        metrics_df = run_prediction(model_type=request.model_type)
        return metrics_df.to_dict(orient="records")
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {str(e)}"})
