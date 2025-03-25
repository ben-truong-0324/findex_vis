from fastapi import FastAPI, UploadFile, File, Form, HTTPException,Request 
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import joblib
import os
from pathlib import Path
import shutil
import uuid
import json
from typing import List, Optional
import uuid
import chardet
from io import BytesIO
from datetime import datetime

app = FastAPI()

from findex.fastapi_config import (
    DATA_DIR,
    MODEL_DIR,
    OUTPUT_DIR,
    TRAIN_PATH_2017,
    TRAIN_PATH_2021,
    TEST_PATH,
    PROCESSED_TEST_PATH
)
import findex.ml_scripts


AVAILABLE_MODELS = {
    "random_forest": "Random Forest",
    "xgboost": "XGBoost",
    "logistic_regression": "Logistic Regression"
}

# Mount static files and templates (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Dataset Management Endpoints
@app.get("/datasets", response_class=HTMLResponse)
async def list_datasets():
    """List available processed datasets and their metadata"""
    processed_dir = DATA_DIR / "processed_data"
    processed_datasets = [
        f.stem for f in processed_dir.glob("*.pkl")
    ]  # Extracting dataset names without extension

    metadata_files = {
        f.stem.replace("_metadata", ""): f for f in processed_dir.glob("*_metadata.json")
    }

    datasets_with_metadata = []
    for dataset in processed_datasets:
        metadata_path = metadata_files.get(dataset)
        if metadata_path:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
        else:
            metadata = {}

        datasets_with_metadata.append({
            "name": dataset,
            "metadata": metadata
        })

    return templates.TemplateResponse(
        "datasets.html",
        {"request": {}, "datasets": datasets_with_metadata}
    )

@app.get("/datasets/upload")
async def redirect_back_to_datasets():
    return RedirectResponse(url=f"/datasets", status_code=303)


COMMON_ENCODINGS = ['utf-8', 'ISO-8859-1', 'latin1', 'windows-1252']
ETL_SESSIONS = {}  # Stores dataset and steps temporarily
SESSION_COUNTER = {}  # Tracks versioning for each dataset
@app.post("/datasets/upload")
async def upload_dataset(request: Request, file: UploadFile = File(...)):
    """Handle file upload with robust encoding detection"""
    try:
        content = await file.read()

        original_name = file.filename
        short_name = original_name[:5] + original_name.split(".")[-2][-5:]  # First 5 + Last 5 chars
        date_str = datetime.now().strftime("%m%d%Y")
        if short_name not in SESSION_COUNTER:
            SESSION_COUNTER[short_name] = 1
        else:
            SESSION_COUNTER[short_name] += 1
        version = f"ver{SESSION_COUNTER[short_name]:03d}"
        user = "anon"
        pipeline_name = f"{short_name}_{user}_{date_str}_{version}"

        # First try common encodings
        for encoding in COMMON_ENCODINGS:
            try:
                file.file = BytesIO(content)  # Reset file pointer
                df = pd.read_csv(file.file, encoding=encoding)
                break  
            except UnicodeDecodeError:
                continue
        else:
            detection = chardet.detect(content)
            if detection['confidence'] > 0.7:  # Only use if confident
                try:
                    file.file = BytesIO(content)
                    df = pd.read_csv(file.file, encoding=detection['encoding'])
                except UnicodeDecodeError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Failed to detect encoding. Try specifying encoding manually. Detected: {detection}"
                    )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Could not automatically determine file encoding. Please specify encoding manually."
                )
        session_id = str(uuid.uuid4())
        ETL_SESSIONS[session_id] = {
            "df": df,
            "original_name": original_name,
            "pipeline_name": pipeline_name,
            "user": user,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "steps": [],
            "metadata": {
                "original_rows": df.shape[0],
                "original_columns": df.shape[1],
                "steps_applied": 0,
            }
            
            
        }
        return RedirectResponse(url=f"/etl/{session_id}", status_code=303)
    
    except Exception as e:
        if "UTF-8" in str(e):
            return templates.TemplateResponse(
                "encoding_error.html",
                {
                    "request": request,
                    "filename": file.filename,
                    "error": str(e),
                    "suggested_encodings": COMMON_ENCODINGS
                },
                status_code=400
            )
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/etl/{session_id}", response_class=HTMLResponse)
async def etl_builder_page(session_id: str):
    """Load ETL builder page with session data."""
    if session_id not in ETL_SESSIONS:
        raise HTTPException(status_code=404, detail="ETL session not found!")

    etl_session = ETL_SESSIONS[session_id]
    
    
    
    return templates.TemplateResponse(
        "etl_builder.html",
        {
            "request": {}, 
            "session_id": session_id, 
            "dataset": etl_session["original_name"],
            "columns": etl_session["df"].columns.tolist(),
            "pipeline_name": etl_session["pipeline_name"],
            "metadata": etl_session["metadata"],
            "steps": etl_session["steps"]
        }
    )

@app.post("/etl/{session_id}/apply")
async def apply_etl_step(
        session_id: str, 
        action: str = Form(...), 
        column: str = Form(None), 
        value: float = Form(None)
    ):
    """Apply ETL step and track metadata"""
    if session_id not in ETL_SESSIONS:
        raise HTTPException(status_code=404, detail="ETL session not found!")

    etl_session = ETL_SESSIONS[session_id]
    df = etl_session["df"]

    # Apply transformation based on action
    if action == "drop_null_rows":
        df.dropna(inplace=True)
    elif action == "drop_null_columns":
        df.dropna(axis=1, inplace=True)
    elif action == "replace_null" and column:
        df[column].fillna(value, inplace=True)
    elif action == "create_sum_column" and column:
        new_column = str(column+"_sum")
        df[new_column] = df[column].sum() 
    elif action == "create_avg_column" and column:
        new_column = str(column+"_avg")
        df[new_column] = df[column].average() 
    
    # Update metadata
    etl_session["steps"].append({
        "action": action,
        "column": column,
        "value": value,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    etl_session["metadata"]["steps_applied"] += 1
    etl_session["metadata"]["rows_after"] = df.shape[0]
    etl_session["metadata"]["columns_after"] = df.shape[1]

    return RedirectResponse(url=f"/etl/{session_id}", status_code=303)

@app.post("/etl/{session_id}/rename")
async def rename_pipeline(
    session_id: str,
    pipeline_name: str = Form(...),
    request: Request = None
):
    """Update the pipeline name"""
    if session_id not in ETL_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    ETL_SESSIONS[session_id]["pipeline_name"] = pipeline_name
    return RedirectResponse(url=f"/etl/{session_id}", status_code=303)


@app.post("/etl/{session_id}/finalize")
async def finalize_etl(session_id: str, pipeline_name: str = None):
    """Finalize the ETL process, save dataset & metadata, and clear session."""
    if session_id not in ETL_SESSIONS:
        raise HTTPException(status_code=404, detail="ETL session not found!")

    etl_session = ETL_SESSIONS[session_id]
    df = etl_session["df"]
    
    # If no name provided, keep auto-generated name
    pipeline_name = pipeline_name or etl_session["pipeline_name"]

    # Ensure `processed_data/` directory exists
    processed_dir = DATA_DIR / "processed_data"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Save final dataset
    final_dataset_path = processed_dir / f"{pipeline_name}_processed_dataset.pkl"
    df.to_pickle(final_dataset_path, index=False)

    # Save metadata
    metadata = {
        "pipeline_name": pipeline_name,
        "original_dataset": etl_session["original_name"],
        "created_at": etl_session["created_at"],
        "user": etl_session["user"],
        "original_rows": etl_session["metadata"]["original_rows"],
        "original_columns": etl_session["metadata"]["original_columns"],
        "rows_after": etl_session["metadata"].get("rows_after", df.shape[0]),
        "columns_after": etl_session["metadata"].get("columns_after", df.shape[1]),
        "steps_applied": etl_session["metadata"]["steps_applied"],
        "etl_steps": etl_session["steps"],
    }

    metadata_path = processed_dir / f"{pipeline_name}_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=4)

    # Remove session from in-memory storage
    del ETL_SESSIONS[session_id]

    return RedirectResponse(url="/datasets", status_code=303)




@app.get("/train/{dataset}", response_class=HTMLResponse)
async def train_page(dataset: str):
    """Show training page with options for selected dataset"""
    data_path = DATA_DIR / dataset
    if not data_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found!")

    df = pd.read_pickle(data_path)
    
    columns = df.columns.tolist()
    available_models = ["Random Forest", "Logistic Regression", "XGBoost", "All"]
    return templates.TemplateResponse(
        "train.html",
        {
            "request": {},
            "dataset": dataset,
            "columns": columns,
            "models": available_models
        }
    )


@app.get("/models/{dataset}/{target}")
def list_models(dataset: str, target: str):
    """List all models trained for a given dataset and target column."""
    models = []
    for meta_file in MODEL_STORE.glob("*.json"):
        with meta_file.open("r") as f:
            metadata = json.load(f)
            if metadata["dataset"] == dataset and metadata["target_column"] == target:
                models.append(metadata)

    return {"models": models}


@app.post("/predict")
def predict(dataset: str, target_column: str, model_id: str, data: list):
    """Run inference on new data using a selected model."""
    model_path = MODEL_STORE / f"{model_id}.pkl"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model not found!")

    model = joblib.load(model_path)
    df = pd.DataFrame(data)
    predictions = model.predict(df).tolist()

    # Save predictions
    output_file = OUTPUT_DIR / f"{dataset}_{target_column}_{model_id}_predictions.json"
    with output_file.open("w") as f:
        json.dump(predictions, f)

    return {"predictions": predictions, "output_file": str(output_file)}


@app.get("/outputs/{dataset}/{target}/{model_id}")
def get_output(dataset: str, target: str, model_id: str):
    """Retrieve JSON output of predictions."""
    output_file = OUTPUT_DIR / f"{dataset}_{target}_{model_id}_predictions.json"
    if not output_file.exists():
        raise HTTPException(status_code=404, detail="Output file not found!")

    with output_file.open("r") as f:
        data = json.load(f)

    return {"predictions": data}
