import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from datetime import datetime

from src.backend.services.log_analyzer import LogAnalyzer
from src.backend.services.alert_manager import AlertManager
from src.backend.services.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_alert_manager_get_rules():
    manager = AlertManager()
    rules = await manager.get_rules()
    assert len(rules) > 0
    assert rules[0].name == "HighRestartCount"


@pytest.mark.asyncio
async def test_alert_manager_get_alerts():
    manager = AlertManager()
    response = await manager.get_alerts()
    assert response.total == 0
    assert response.page == 1
    assert response.page_size == 20


@pytest.mark.asyncio
async def test_metrics_service_cluster():
    service = MetricsService()
    metrics = await service.get_cluster_metrics()
    assert "total_pods" in metrics
    assert "timestamp" in metrics


@pytest.mark.asyncio
async def test_metrics_service_pod():
    service = MetricsService()
    metrics = await service.get_pod_metrics("default", "test-pod")
    assert metrics["pod_name"] == "test-pod"
    assert metrics["namespace"] == "default"
