# Findex Vis

Findex Vis is a web application that visualizes machine learning model predictions on financial survey data. It features a FastAPI backend and an HTML/CSS/D3.js frontend. Machine learning outputs are generated onto mounted drive and made available for visualization.

## Project Overview

Data is retrieved from [WorldBank.org Data Source](https://www.worldbank.org/en/publication/globalfindex/Data).  

FastAPI Backend: Serves data and APIs for the frontend.
Frontend with D3.js: Interactive visualizations of ML model predictions.
Containerized Deployment: The entire application is containerized using Docker, ready for minikube dev deployment.

## Data Folder Manual add
Create data folder in root, not included due to size upload limit.
Download/copy data into ./data/ and make sure to have these files in data:
```bash
mkdir data
findex2021_micro_world_139countries.csv
ft2verbose.json
world_countries.json
```
## Installation and Setup
```bash
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