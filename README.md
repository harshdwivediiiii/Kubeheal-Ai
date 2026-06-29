# KubeHeal AI

> Self-healing Kubernetes system with AI-powered log analysis, automated failure detection, and Prometheus/Grafana monitoring — running fully local on Minikube.

![Architecture](docs/architecture.png)

---

## Demo

<!-- Add your demo GIF here after recording -->
<!-- ![Demo](docs/demo.gif) -->

---

## What it does

When a pod crashes repeatedly, KubeHeal AI:
1. **Detects** the failure (restart count ≥ 3 or CrashLoopBackOff)
2. **Diagnoses** the root cause by reading pod logs via Kubernetes API
3. **Suggests a fix** using pattern-based log analysis
4. **Heals automatically** by deleting the broken pod — Kubernetes recreates it clean

---

## Stack

| Layer | Technology |
|---|---|
| App | Node.js + Express |
| Container | Docker |
| Orchestration | Kubernetes (Minikube) |
| Monitoring | Prometheus + Grafana (Helm) |
| AI Analyzer | Python FastAPI + Kubernetes client |
| Self-Healing | Python automation script |
| CI/CD | GitHub Actions |

---

## Project Structure

```
kubeheal-ai/
├── app/                    # Node.js app
│   ├── index.js
│   └── package.json
├── ai-analyzer/            # FastAPI log analyzer
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── healer/                 # Self-healing script
│   └── heal.py
├── k8s/                    # Kubernetes manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ai-analyzer/
│       ├── rbac.yaml
│       ├── deployment.yaml
│       └── service.yaml
├── docs/
│   └── architecture.png
├── Dockerfile
└── .github/workflows/
    └── deploy.yml
```

---

## Local Setup

### Prerequisites
- Docker Desktop
- Minikube
- kubectl
- Helm
- Python 3.9+

### 1 — Start cluster
```bash
minikube start --driver=docker
eval $(minikube docker-env)
```

### 2 — Build and deploy the app
```bash
docker build -t kubeheal-app:latest .
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl get pods -w
```

### 3 — Install Prometheus + Grafana
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

### 4 — Deploy AI Analyzer
```bash
docker build -t ai-analyzer:latest -f ai-analyzer/Dockerfile ai-analyzer/
kubectl apply -f k8s/ai-analyzer/rbac.yaml
kubectl apply -f k8s/ai-analyzer/deployment.yaml
kubectl apply -f k8s/ai-analyzer/service.yaml
```

### 5 — Run self-healing script
```bash
pip3 install kubernetes requests
python3 healer/heal.py
```

### 6 — Access services
```bash
# App
kubectl port-forward deployment/kubeheal-app 8080:3000

# AI Analyzer
kubectl port-forward svc/ai-analyzer 8001:8000

# Grafana
kubectl port-forward -n monitoring svc/monitoring-grafana 3001:80
```

---

## API Endpoints

### kubeheal-app
| Endpoint | Description |
|---|---|
| `GET /` | App status + hostname |
| `GET /healthz` | Health check |
| `GET /crash` | Trigger intentional crash (Phase 3) |

### ai-analyzer
| Endpoint | Description |
|---|---|
| `GET /pods/{namespace}` | List pods with restart counts |
| `GET /analyze/{namespace}/{pod}` | Analyze current pod logs |
| `GET /analyze/{namespace}/{pod}?previous=true` | Analyze crashed pod logs |

---

## Example

```bash
curl "http://localhost:8001/analyze/default/kubeheal-app-xxx?previous=true"
```

```json
{
  "pod": "kubeheal-app-xxx",
  "issue": "Application called process.exit — intentional or unhandled crash.",
  "fix": "Check app code for unhandled exceptions or explicit exit calls.",
  "matched_pattern": "process.exit"
}
```
# Kubeheal-Ai
