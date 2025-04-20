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
#open /Applications/Docker.app
minikube start --driver=docker

eval $(minikube docker-env)  #set local docker env to minikube. this is for mac
#& minikube -p minikube docker-env --shell=cmd | Invoke-Expression #powershell
#@FOR /f "tokens=*" %i IN ('minikube docker-env --shell=cmd') DO @%i #windows anaconda prompt

minikube mount ./data:/mnt/data

eval $(minikube docker-env) #in new shell, use corresponding command
docker build -t flask_app_image ./flask_app
kubectl apply -f k8s/fe_flask.yaml
kubectl apply -f k8s/flask_app_service.yaml
minikube service flask_app_service
kubectl get pods 

eval $(minikube docker-env) #in new shell, use corresponding command
docker build -t mlapi_image ./mlAPI
kubectl apply -f k8s/mlAPI.yaml
minikube service mlapi-service

#for troubleshooting
kubectl get pods
kubectl get services
kubectl describe pod <pod-name> #see why pod is failing outward
kubectl logs <pod-name> #see why pod fail inward
```