from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime

from src.backend.services.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/cluster")
async def get_cluster_metrics():
    service = MetricsService()
    metrics = await service.get_cluster_metrics()
    return metrics


@router.get("/pod/{namespace}/{pod_name}")
async def get_pod_metrics(namespace: str, pod_name: str):
    service = MetricsService()
    metrics = await service.get_pod_metrics(namespace, pod_name)
    return metrics


@router.get("/history/{pod_name}")
async def get_metric_history(
    pod_name: str,
    metric_type: str,
    hours: int = Query(24, ge=1, le=720),
):
    service = MetricsService()
    history = await service.get_metric_history(pod_name, metric_type, hours)
    return history


@router.get("/prometheus/query")
async def prometheus_query(query: str):
    service = MetricsService()
    result = await service.query_prometheus(query)
    return result
