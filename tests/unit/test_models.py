import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime

from src.backend.models.user import UserCreate, UserLogin, UserResponse, Token
from src.backend.models.pod import PodStatus, PodPrediction, PodLog, PodMetrics
from src.backend.models.alert import Alert, AlertRule


def test_user_create_model():
    user = UserCreate(username="testuser", email="test@example.com", password="securepass")
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_pod_status_model():
    pod = PodStatus(
        name="test-pod",
        namespace="default",
        status="Running",
        restart_count=0,
        age="2d",
        node="node-1",
        ip="10.0.0.1",
        phase="Running",
        conditions=["Ready"],
    )
    assert pod.name == "test-pod"
    assert pod.status == "Running"


def test_pod_prediction_model():
    pred = PodPrediction(
        pod_name="test-pod",
        namespace="default",
        failure_probability=0.85,
        predicted_failure_type="CrashLoopBackOff",
        confidence=0.9,
        timestamp=datetime.utcnow(),
    )
    assert pred.failure_probability == 0.85
    assert pred.confidence == 0.9


def test_alert_model():
    alert = Alert(
        id="alert-1",
        title="High CPU Usage",
        description="CPU usage above 90%",
        severity="warning",
        status="active",
        source="prometheus",
        created_at=datetime.utcnow(),
    )
    assert alert.severity == "warning"
    assert alert.status == "active"


def test_alert_rule_model():
    rule = AlertRule(
        name="HighRestartCount",
        description="Pod restart count exceeds threshold",
        metric="restart_count",
        condition=">",
        threshold=5.0,
        duration="5m",
        severity="critical",
    )
    assert rule.name == "HighRestartCount"
    assert rule.threshold == 5.0
