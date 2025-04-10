from fastapi import APIRouter
from fastapi import FastAPI, UploadFile, File, Form, HTTPException,Request 
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
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


router = APIRouter()

from fastapi_core.config import (
    DATA_DIR,
    MODEL_DIR,
    OUTPUT_DIR,
    TRAIN_PATH_2017,
    TRAIN_PATH_2021,
    TEST_PATH,
    PROCESSED_TEST_PATH,
    templates
)


@router.get("/", response_class=HTMLResponse)
async def list_datasets():
    """List available processed datasets and their metadata"""
    processed_dir = DATA_DIR / "processed_data"
    processed_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    
    # Get all processed datasets and metadata files
    dataset_files = {f.stem: f for f in processed_dir.glob("*.pkl")}
    metadata_files = {f.stem.replace("_metadata", ""): f for f in processed_dir.glob("*_metadata.json")}
    
    datasets_with_metadata = []
    for dataset_name, dataset_path in dataset_files.items():
        print(dataset_name, dataset_path)
        metadata = {}
        dataset_stripped = dataset_name.replace("_processed_dataset", "")
        if dataset_stripped in metadata_files:
            try:
                with open(metadata_files[dataset_stripped], "r") as f:
                    metadata = json.load(f)
                    datasets_with_metadata.append({
                        "name": dataset_name,
                        "path": str(dataset_path),
                        "created_at": dataset_path.stat().st_ctime,
                        "metadata": metadata
                    })
            except (json.JSONDecodeError, IOError):
                metadata = {"error": "Could not load metadata"}
        
    return templates.TemplateResponse(
        "datasets.html",
        {"request": {}, "datasets": datasets_with_metadata}
    )

@router.get("/upload")
async def redirect_back_to_datasets():
    return RedirectResponse(url=f"/", status_code=303)

COMMON_ENCODINGS = ['utf-8', 'ISO-8859-1', 'latin1', 'windows-1252']
 # Tracks versioning for each dataset
@router.post("/upload")
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
