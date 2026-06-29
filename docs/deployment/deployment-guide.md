# KubeHeal AI Deployment Guide

## Prerequisites

- Docker Desktop
- Minikube
- kubectl
- Helm
- Python 3.9+
- MongoDB

## Local Development

### 1. Setup
```bash
git clone https://github.com/harshdwivediiiii/Kubeheal-Ai.git
cd Kubeheal-Ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements/requirements.txt
pip install -r requirements/requirements-api.txt
pip install -r requirements/requirements-dashboard.txt
pip install -r requirements/requirements-ml.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Training
```bash
python scripts/run_training_pipeline.py
```

### 4. Run Services
```bash
# Terminal 1: FastAPI Backend
make run-api

# Terminal 2: Streamlit Dashboard
make run-dashboard

# Terminal 3: Self-Healing Agent
python healer/heal.py
```

## Docker Deployment

```bash
# Build and run all services
make docker-build
make docker-up

# View logs
docker compose -f docker/docker-compose.yaml logs -f
```

## Kubernetes Deployment (Minikube)

### 1. Start Minikube
```bash
minikube start --driver=docker --cpus=4 --memory=8192
eval $(minikube docker-env)
```

### 2. Deploy KubeHeal
```bash
make k8s-deploy
```

### 3. Deploy Monitoring
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### 4. Access Services
```bash
# Backend API
kubectl port-forward svc/kubeheal-backend -n kubeheal 8000:8000

# Dashboard
kubectl port-forward svc/kubeheal-dashboard -n kubeheal 8501:8501

# Grafana
kubectl port-forward svc/monitoring-grafana -n monitoring 3001:80

# Prometheus
kubectl port-forward svc/monitoring-prometheus -n monitoring 9090:9090
```

## Production Deployment

### Cloud (GKE/EKS/AKS)
```bash
# Build and push images
make docker-build
docker tag kubeheal-backend:latest your-registry/kubeheal-backend:latest
docker push your-registry/kubeheal-backend:latest

# Deploy
helm install kubeheal k8s/helm/kubeheal/
```

### Security Checklist
- Change all default secrets
- Enable TLS/SSL
- Configure network policies
- Set up RBAC
- Enable audit logging
- Regular backup strategy
