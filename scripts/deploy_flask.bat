@echo off
setlocal enabledelayedexpansion
echo 🚀 Deploying Flask App...

:: Point Docker to Minikube's daemon
FOR /f "tokens=*" %%i IN ('minikube docker-env --shell=cmd') DO @%%i

echo 🐳 Building Flask Docker image...
docker build -t flask_app_image ..\flask_app

echo 🔄 Reapplying Flask deployment...
kubectl delete -f ..\k8s\fe_flask.yaml --ignore-not-found
kubectl apply -f ..\k8s\fe_flask.yaml

echo 🌐 Reapplying Flask service...
kubectl delete -f ..\k8s\flask_app_service.yaml --ignore-not-found
kubectl apply -f ..\k8s\flask_app_service.yaml

echo 🕐 Waiting for Flask pod to become ready...
kubectl wait --for=condition=ready pod -l app=flask-app --timeout=90s
minikube service flask-service