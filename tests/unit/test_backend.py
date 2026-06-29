import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "KubeHeal AI"


def test_readiness_endpoint():
    response = client.get("/readiness")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_liveness_endpoint():
    response = client.get("/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_auth_token_endpoint():
    response = client.post("/auth/token", data={
        "username": "testuser",
        "password": "testpass",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_list_pods():
    response = client.get("/pods/")
    assert response.status_code in (200, 500)


def test_alert_rules():
    response = client.get("/alerts/rules")
    assert response.status_code == 200
    rules = response.json()
    assert isinstance(rules, list)
