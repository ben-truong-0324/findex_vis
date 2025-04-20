# mlAPI/routes/ml_routes.py

from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os
import json
import numpy as np
from ml import run_prediction
from schemas.ml_schemas import PredictionRequest

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
        metrics_df, feature_importance_df, metrics_list_by_cluster = run_prediction(model_type=request.model_type)

        metrics_json_str = metrics_df.to_json(orient="records")
        feature_json_str = feature_importance_df.to_json(orient="records")
        metrics_list_by_cluster_json_str = metrics_list_by_cluster.to_json(orient="records")
        return {
            "metrics": json.loads(metrics_json_str),
            "feature_importance": json.loads(feature_json_str),
            "metrics_list_by_cluster": json.loads(metrics_list_by_cluster_json_str)
        }

    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Internal error: {str(e)}"})