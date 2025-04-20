#!/bin/bash

set -e  # Exit immediately if any command fails

echo "🚀 Deploying Flask App..."

# 🔗 Point Docker to Minikube's daemon
eval $(minikube docker-env)

# 🐳 Build Flask Docker image
echo "🐳 Building Flask Docker image..."
docker build -t flask_app_image ../flask_app

# 🔄 Reapply Flask deployment
echo "🔄 Reapplying Flask deployment..."
kubectl delete -f ../k8s/fe_flask.yaml --ignore-not-found
kubectl apply -f ../k8s/fe_flask.yaml

# 🌐 Reapply Flask service
echo "🌐 Reapplying Flask service..."
kubectl delete -f ../k8s/flask_app_service.yaml --ignore-not-found
kubectl apply -f ../k8s/flask_app_service.yaml

# ⏳ Wait for the pod to be ready
echo "🕐 Waiting for Flask pod to become ready..."
kubectl wait --for=condition=ready pod -l app=flask-app --timeout=90s

# 🌍 Open the Flask service in browser
minikube service flask-service
