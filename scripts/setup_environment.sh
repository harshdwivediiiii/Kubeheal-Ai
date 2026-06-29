#!/bin/bash
set -e

echo "============================================================"
echo "KubeHeal AI - Environment Setup Script"
echo "============================================================"

echo ""
echo "[1/8] Checking Python..."
python3 --version || { echo "Install Python 3.9+ from https://python.org"; exit 1; }

echo ""
echo "[2/8] Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel

echo ""
echo "[3/8] Installing dependencies..."
pip install -r requirements/requirements.txt
pip install -r requirements/requirements-api.txt
pip install -r requirements/requirements-dashboard.txt
pip install -r requirements/requirements-ml.txt
pip install -r requirements/requirements-llm.txt
pip install -r requirements/requirements-dev.txt

echo ""
echo "[4/8] Checking Git..."
git --version || { echo "Install Git from https://git-scm.com"; exit 1; }

echo ""
echo "[5/8] Checking Docker..."
docker --version || echo "WARNING: Install Docker Desktop from https://docker.com"

echo ""
echo "[6/8] Checking Kubernetes tools..."
kubectl version --client 2>/dev/null || echo "WARNING: Install kubectl"
minikube version 2>/dev/null || echo "WARNING: Install Minikube"
helm version --short 2>/dev/null || echo "WARNING: Install Helm"

echo ""
echo "[7/8] Checking MongoDB..."
python3 -c "import pymongo; print('pymongo:', pymongo.__version__)"

echo ""
echo "[8/8] Verifying installations..."
python3 scripts/health_check.py

echo ""
echo "============================================================"
echo "Environment setup complete!"
echo "Run 'source .venv/bin/activate' to activate"
echo "============================================================"
