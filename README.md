# Findex Vis

Findex Vis is a web application that visualizes machine learning model predictions on financial survey data. It features a Django backend and an HTML/CSS/D3.js frontend. Machine learning outputs are generated locally and made available for visualization.

## Project Overview

Data is retrieved from [NFIP Data Source](https://www.fema.gov/openfema-data-page/fima-nfip-redacted-claims-v2).  

Django Backend: Serves data and APIs for the frontend.
Frontend with D3.js: Interactive visualizations of ML model predictions.
Machine Learning Integration: ML scripts run locally, with outputs accessible to the frontend.
Containerized Deployment: The entire application is containerized using Docker.


## Installation and Setup
Download/copy data into ./data/

```bash
conda env create -f environment.yml
conda env update --file environment.yml --prune
conda env update --file environment.yml
conda activate ml_general
python -m findex.ml

# uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
uvicorn findex.main:app --host 0.0.0.0 --port 8000 --reload

http://127.0.0.1:8000/docs

docker build -t my-fastapi-app .
docker run -p 8000:8000 my-fastapi-app
```