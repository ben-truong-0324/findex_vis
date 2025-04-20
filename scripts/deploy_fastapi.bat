@echo off
setlocal enabledelayedexpansion
echo 🚀 Deploying FastAPI (mlAPI)...

FOR /f "tokens=*" %%i IN ('minikube docker-env --shell=cmd') DO @%%i

docker build -t mlapi_image ..\mlAPI

kubectl delete -f ..\k8s\mlAPI.yaml --ignore-not-found
kubectl apply -f ..\k8s\mlAPI.yaml

kubectl wait --for=condition=ready pod -l app=mlapi --timeout=90s
minikube service mlapi-service 