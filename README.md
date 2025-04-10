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

#run in dev with separate containers
# docker compose up --build -d
# app1: http://localhost:8080
# app2: http://localhost:8080

#run PROD with k8 and uploaded registry
docker build -t mlapi:latest . 
docker login
docker tag mlapi:latest <username>/mlapi:latest
docker push <username>/mlapi:latest

#run in DEV with minikube and mounted vol
# may need to exit out venv/conda to see Docker
open /Applications/Docker.app
minikube start --driver=docker
eval $(minikube docker-env)  #set local docker env to minikube

docker run -v /path/to/your/local/code:/app -p 8000:8000 mlapi:latest
docker run -v
cd mlAPI
docker build -t mlapi:latest . #now build image of app, to be built in container of minikube
#image built inside minikube docker, to check:
minikube -p minikube ssh
docker images
cd ..

kubectl get all
# kubectl get nodes
# kubectl get ingress
# kubectl get services
# kubectl get deployments
# kubectl apply -k ./k8s/overlays/dev
kubectl apply -f k8s/deployments.yaml
kubectl get pods
minikube addons enable ingress
minikube tunnel


# minikube service fastapi-service #expose services
# minikube service flask-service

http://127.0.0.1:8000/docs

docker build -t my-fastapi-app .

docker build --build-arg INSTALL_CUDA=no -t mlapi:latest .
docker build --build-arg INSTALL_CUDA=yes -t mlapi:latest .

docker run -p 8000:8000 my-fastapi-app
```