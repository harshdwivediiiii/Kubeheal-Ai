from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PodMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_rx: float
    network_tx: float
    timestamp: datetime


class PodStatus(BaseModel):
    name: str
    namespace: str
    status: str
    restart_count: int
    age: str
    node: str
    ip: str
    phase: str
    conditions: List[str] = []
    metrics: Optional[PodMetrics] = None
    created_at: datetime


class PodPrediction(BaseModel):
    pod_name: str
    namespace: str
    failure_probability: float
    predicted_failure_type: str
    confidence: float
    features_used: List[str] = []
    timestamp: datetime


class PodLog(BaseModel):
    pod_name: str
    namespace: str
    container: str
    timestamp: datetime
    level: str
    message: str
    analyzed: bool = False
    severity: Optional[str] = None
