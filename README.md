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
On Mac:
In first terminal:
minikube start --driver=docker
minikube mount ./data:/mnt/data

In 2nd terminal: 
chmod +x deploy.sh
./deploy.sh

On Windows, at root folder findex_vis/
deploy_win.bat

#for troubleshooting
kubectl logs -l app=mlapi
kubectl logs -l app=flask-app
kubectl get pods
kubectl get services
kubectl describe pod <pod-name> #see why pod is failing outward
kubectl logs <pod-name> #see why pod fail inward
kubectl logs deployment/mlapi -f
```