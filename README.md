# Findex Vis

Findex Vis is a web application that visualizes machine learning model predictions on financial survey data. It features a Django backend and an HTML/CSS/D3.js frontend. Machine learning outputs are generated locally and made available for visualization.

## Project Overview

Data is retrieved from [NFIP Data Source](https://www.fema.gov/openfema-data-page/fima-nfip-redacted-claims-v2).  

Django Backend: Serves data and APIs for the frontend.
Frontend with D3.js: Interactive visualizations of ML model predictions.
Machine Learning Integration: ML scripts run locally, with outputs accessible to the frontend.
Containerized Deployment: The entire application is containerized using Docker.


## Installation and Setup

```bash
conda env create -f environment.yml
conda env update --file environment.yml --prune
conda activate ml_general
python -m findex.ml

# download/copy data into ./data/
```

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
docker-compose up --build # or with docker
fastapi dev main.py
http://127.0.0.1:8000/docs


#run app
uvicorn app.main:app --reload
pytest app/test.py

#run docker
docker-compose up -d --build
docker-compose exec app pytest test/test.py
docker-compose exec db psql --username=fastapi --dbname=fastapi_dev
http://127.0.0.1:8000/docs

#after done with venv
deactivate
rmdir /s /q venv #to delete venv after use