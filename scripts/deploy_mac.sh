#!/bin/bash

set -e
set -o pipefail

echo "🚀 Starting Minikube..."
minikube start --driver=docker

echo "🔁 Setting Docker to use Minikube environment..."
eval $(minikube docker-env)

echo "⚠️  NOTE: You must run this in a separate terminal:"
echo "    minikube mount ./data:/mnt/data"
echo "    (Leave that terminal open while services run!)"
echo ""

echo "🐳 Building Flask image..."
docker build -t flask_app_image ./flask_app

echo "🔥 Re-deploying Flask app..."
kubectl delete -f k8s/fe_flask.yaml --ignore-not-found
kubectl apply -f k8s/fe_flask.yaml

echo "🌐 Re-deploying Flask service..."
kubectl delete -f k8s/flask_app_service.yaml --ignore-not-found
kubectl apply -f k8s/flask_app_service.yaml

echo "🌍 Opening Flask app..."
minikube service flask-service

echo "🐳 Building FastAPI (mlAPI) image..."
docker build -t mlapi_image ./mlAPI

echo "🚀 Re-deploying FastAPI..."
kubectl delete -f k8s/mlAPI.yaml --ignore-not-found
kubectl apply -f k8s/mlAPI.yaml

echo "🌍 Opening FastAPI..."
minikube service mlapi-service

echo "🔎 Current pods:"
kubectl get pods
