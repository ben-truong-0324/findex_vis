#!/bin/bash

set -e  # Exit if any command fails
echo "🚀 Deploying FastAPI (mlAPI)..."

# 🔗 Set Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# 🛠️ Build the Docker image
docker build -t mlapi_image ../mlAPI

# 🔄 Reapply the Kubernetes deployment
kubectl delete -f ../k8s/mlAPI.yaml --ignore-not-found
kubectl apply -f ../k8s/mlAPI.yaml

# ⏳ Wait for the pod to be ready
kubectl wait --for=condition=ready pod -l app=mlapi --timeout=90s

# 🌐 Open the service in browser
minikube service mlapi-service
