
######################################################################
#Training Workflow APIs
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

from findex.fastapi_core.config import (
    DATA_DIR,
    MODEL_DIR,
    OUTPUT_DIR,
    TRAIN_PATH_2017,
    TRAIN_PATH_2021,
    TEST_PATH,
    PROCESSED_TEST_PATH,
    templates
)

router = APIRouter()

@router.get("/train/{dataset}", response_class=HTMLResponse)
async def train_page(dataset: str):
    """Show training page with options for selected dataset"""
    data_path = (DATA_DIR / "processed_data" / dataset).with_suffix('.pkl')


    if not data_path.exists():
        print(data_path)
        raise HTTPException(status_code=404, detail="Dataset not found!")

    
    if dataset not in TRAIN_SESSIONS:
        try:
            df = pd.read_pickle(data_path)
            TRAIN_SESSIONS[dataset] = {"df": df}
        except:
            raise HTTPException(status_code=404, detail="Processed dataset loading error")
    else:
        df = TRAIN_SESSIONS[dataset]["df"] 
    
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

@router.post("/train/{dataset}/start")
async def train_model(
    dataset: str,
    target_column: str = Form(...),
    test_size: float = Form(...),
    selected_models: List[str] = Form(...),
    early_stopping: Optional[str] = Form(None),
    cross_validation: Optional[str] = Form(None),
    max_epochs: Optional[int] = Form(100),
):
    """Train models on the selected dataset with given parameters"""

    if dataset not in TRAIN_SESSIONS:
        try:
            df = pd.read_pickle(data_path)
            TRAIN_SESSIONS[dataset] = {"df": df}
        except:
            raise HTTPException(status_code=404, detail="Processed dataset loading error")
    else:
        df = TRAIN_SESSIONS[dataset]["df"] 

    if target_column not in df.columns:
        raise HTTPException(status_code=400, detail="Invalid target column selected")

    # Splitting data
    X = df.drop(columns=[target_column])
    y = df[target_column]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # Model Training
    model_results = {}
    available_models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Logistic Regression": LogisticRegression(max_iter=max_epochs, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss'),
    }

    if "All" in selected_models:
        selected_models = list(available_models.keys())

    for model_name in selected_models:
        model = available_models.get(model_name)
        if not model:
            continue

        if cross_validation:
            scores = cross_val_score(model, X_train, y_train, cv=5)
            model_results[model_name] = {"cv_score_mean": scores.mean()}
        else:
            model.fit(X_train, y_train)
            accuracy = model.score(X_test, y_test)
            model_results[model_name] = {"accuracy": accuracy}

    # Save training results
    results_path = RESULTS_DIR / f"results_{dataset}.json"
    with open(results_path, "w") as f:
        json.dump(model_results, f, indent=4)

    return RedirectResponse(url=f"/results/{dataset}", status_code=303)

