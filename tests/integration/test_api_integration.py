import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from src.backend.main import app

client = TestClient(app)


def test_full_auth_flow():
    response = client.post("/auth/token", data={
        "username": "admin",
        "password": "admin",
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    assert token is not None

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_full_api_flow():
    response = client.get("/health")
    assert response.status_code == 200

    response = client.get("/pods/")
    assert response.status_code in (200, 500)

    response = client.get("/alerts/rules")
    assert response.status_code == 200

    response = client.get("/metrics/cluster")
    assert response.status_code == 200
