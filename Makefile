.PHONY: help install setup train test lint format run-api run-dashboard docker-build docker-up k8s-deploy clean

help:
	@echo "KubeHeal AI - Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install        Install all dependencies"
	@echo "  make setup          Setup virtual environment and install"
	@echo "  make train          Train all ML models"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linters"
	@echo "  make format         Format code"
	@echo "  make run-api        Run FastAPI server"
	@echo "  make run-dashboard  Run Streamlit dashboard"
	@echo "  make docker-build   Build Docker images"
	@echo "  make docker-up      Start Docker Compose"
	@echo "  make k8s-deploy     Deploy to Kubernetes"
	@echo "  make clean          Clean artifacts"

install:
	pip install -r requirements/requirements.txt
	pip install -r requirements/requirements-dev.txt
	pip install -r requirements/requirements-api.txt
	pip install -r requirements/requirements-dashboard.txt
	pip install -r requirements/requirements-ml.txt
	pip install -r requirements/requirements-llm.txt

setup:
	python3 -m venv .venv
	. .venv/bin/activate && pip install --upgrade pip && make install

train:
	python scripts/run_training_pipeline.py

test:
	pytest tests/ -v --cov=src --cov-report=term

lint:
	ruff check src/ scripts/ tests/
	black --check src/ scripts/ tests/

format:
	black src/ scripts/ tests/
	ruff --fix src/ scripts/ tests/

run-api:
	uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	streamlit run src/dashboard/app.py --server.port=8501

docker-build:
	docker compose -f docker/docker-compose.yaml build

docker-up:
	docker compose -f docker/docker-compose.yaml up -d

docker-down:
	docker compose -f docker/docker-compose.yaml down

k8s-deploy:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/rbac.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/secrets.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/hpa.yaml
	kubectl apply -f k8s/ingress.yaml

k8s-delete:
	kubectl delete -f k8s/

helm-install:
	helm install kubeheal k8s/helm/kubeheal/

clean:
	rm -rf artifacts/models/
	rm -rf artifacts/plots/
	rm -rf .pytest_cache/
	rm -rf __pycache__/
	rm -rf .venv/
	rm -rf logs/*.log
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
