# KubeHeal AI Architecture

## System Overview

KubeHeal AI is a self-healing Kubernetes system that uses AI-powered log analysis, automated failure detection, and Prometheus/Grafana monitoring.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │  Streamlit        │  │  Grafana Dashboard               │ │
│  │  Dashboard        │  │  (Monitoring UI)                 │ │
│  └────────┬─────────┘  └──────────────┬───────────────────┘ │
└───────────┼────────────────────────────┼─────────────────────┘
            │                            │
┌───────────▼────────────────────────────▼─────────────────────┐
│                      API Layer                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              FastAPI Backend (Port 8000)                │  │
│  │  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Auth    │ │ Pods     │ │ Alerts   │ │ Metrics  │   │  │
│  │  │ API     │ │ API      │ │ API      │ │ API      │   │  │
│  │  └─────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                      AI Layer                                 │
│  ┌────────────────┐ ┌────────────────┐ ┌──────────────────┐  │
│  │ ML Models       │ │ RAG System     │ │ LLM Integration  │  │
│  │ - RandomForest  │ │ - Vector Store │ │ - OpenAI         │  │
│  │ - XGBoost       │ │ - Knowledge    │ │ - Anthropic      │  │
│  │ - LightGBM      │ │   Base         │ │ - Groq           │  │
│  │ - Isolation     │ │ - Sentence     │ │ - Rule-based     │  │
│  │   Forest        │ │   Transformers │ │   Fallback       │  │
│  └────────────────┘ └────────────────┘ └──────────────────┘  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   Data Layer                                  │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐  │
│  │ MongoDB    │ │ Redis      │ │ Prometheus │ │ File      │  │
│  │ (Primary)  │ │ (Cache)    │ │ (Metrics)  │ │ Storage   │  │
│  └────────────┘ └────────────┘ └────────────┘ └───────────┘  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   Self-Healing Layer                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Python Healer Script                                  │  │
│  │  - CrashLoopBackOff → Delete & Restart                 │  │
│  │  - OOMKilled → Increase Memory Limits                  │  │
│  │  - ImagePullBackOff → Log & Alert                      │  │
│  │  - High Restart Count → Auto-Heal or Escalate          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                        │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐  │
│  │ Docker     │ │ Kubernetes │ │ Helm       │ │ GitHub    │  │
│  │ Containers │ │ (Minikube) │ │ Charts     │ │ Actions   │  │
│  └────────────┘ └────────────┘ └────────────┘ └───────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## Components

### 1. FastAPI Backend
- RESTful API for all operations
- JWT authentication
- Swagger documentation
- MongoDB integration
- Kubernetes client integration

### 2. Streamlit Dashboard
- Real-time cluster overview
- Pod management
- Alert visualization
- Failure predictions
- Log explorer
- Prometheus metrics
- AI recommendations

### 3. ML Models
- **Failure Predictor**: RandomForest/XGBoost/LightGBM
- **Anomaly Detector**: Isolation Forest
- **Severity Classifier**: Gradient Boosting
- **Autoencoder**: Deep learning anomaly detection

### 4. RAG System
- Vector store (FAISS/ChromaDB)
- Sentence Transformers for embeddings
- Knowledge base for Kubernetes issues
- LLM integration for fix suggestions

### 5. Self-Healing Agent
- Monitors pods continuously
- Detects failure patterns
- Applies automated fixes
- Escalates when needed

### 6. Monitoring Stack
- Prometheus for metrics collection
- Grafana for visualization
- Alertmanager for notifications
- Node Exporter for node metrics
