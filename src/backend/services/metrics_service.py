from typing import Optional
from datetime import datetime, timedelta

import aiohttp

from src.backend.core.config import settings


class MetricsService:
    def __init__(self):
        self.prometheus_url = settings.prometheus_url

    async def get_cluster_metrics(self) -> dict:
        return {
            "total_pods": 0,
            "running_pods": 0,
            "failing_pods": 0,
            "total_nodes": 0,
            "healthy_nodes": 0,
            "cpu_usage_pct": 0.0,
            "memory_usage_pct": 0.0,
            "disk_usage_pct": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_pod_metrics(self, namespace: str, pod_name: str) -> dict:
        return {
            "pod_name": pod_name,
            "namespace": namespace,
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "network_rx": 0.0,
            "network_tx": 0.0,
            "restart_count": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def get_metric_history(
        self, pod_name: str, metric_type: str, hours: int = 24
    ) -> list:
        return []

    async def query_prometheus(self, query: str) -> dict:
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.prometheus_url}/api/v1/query"
                params = {"query": query}
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    return {"error": f"Prometheus returned {response.status}"}
            except Exception as e:
                return {"error": str(e), "query": query}
