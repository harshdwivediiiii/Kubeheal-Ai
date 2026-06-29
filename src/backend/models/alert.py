from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class Alert(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    status: str
    source: str
    pod_name: Optional[str] = None
    namespace: Optional[str] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class AlertRule(BaseModel):
    name: str
    description: str
    metric: str
    condition: str
    threshold: float
    duration: str
    severity: str
    enabled: bool = True


class AlertResponse(BaseModel):
    alerts: List[Alert]
    total: int
    page: int
    page_size: int
