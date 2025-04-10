
######################################################################
#ETL Workflow APIs
from fastapi import APIRouter
from fastapi import FastAPI, UploadFile, File, Form, HTTPException,Request 
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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



@router.get("/{session_id}", response_class=HTMLResponse)
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
            "steps": etl_session["steps"],
            "etl_functions": list(ETL_FUNCTIONS.keys())  # Pass available ETL functions
        }
    )



@router.post("/{session_id}/apply")
async def apply_etl_step(
    session_id: str, 
    action: str = Form(...), 
    column: str = Form(None), 
    value: float = Form(None),
    custom_script: str = Form(None)  # Allow specifying a custom script
):
    """Apply ETL transformation to the dataset"""

    # Retrieve session data
    etl_session = ETL_SESSIONS.get(session_id)
    if not etl_session:
        raise HTTPException(status_code=404, detail="ETL session not found")

    df = etl_session["df"]

    if action in ETL_FUNCTIONS:
        try:
            if column and value is not None:
                df = ETL_FUNCTIONS[action](df, column, value)
            elif column:
                df = ETL_FUNCTIONS[action](df, column)
            else:
                df = ETL_FUNCTIONS[action](df)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ETL function error: {e}")
    else:
        raise HTTPException(status_code=400, detail="Invalid ETL action")

    # Update etl metadata of session 
    etl_session["df"] = df
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

@router.post("/{session_id}/rename")
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


@router.post("/{session_id}/finalize")
async def finalize_etl(session_id: str):
    """Finalize the ETL process, save dataset & metadata, and clear session."""
    if session_id not in ETL_SESSIONS:
        raise HTTPException(status_code=404, detail="ETL session not found!")

    etl_session = ETL_SESSIONS[session_id]
    df = etl_session["df"]
    pipeline_name =  etl_session["pipeline_name"]

    # Ensure `processed_data/` directory exists
    processed_dir = DATA_DIR / "processed_data"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Save final dataset
    final_dataset_path = processed_dir / f"{pipeline_name}_processed_dataset.pkl"
    df.to_pickle(final_dataset_path) 

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

    return RedirectResponse(url="/", status_code=303)

