from typing import List, Optional
from datetime import datetime

from src.backend.models.alert import Alert, AlertRule, AlertResponse


class AlertManager:
    def __init__(self):
        pass

    async def get_alerts(
        self,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AlertResponse:
        return AlertResponse(
            alerts=[],
            total=0,
            page=page,
            page_size=page_size,
        )

    async def get_rules(self) -> List[AlertRule]:
        return [
            AlertRule(
                name="HighRestartCount",
                description="Pod restart count exceeds threshold",
                metric="restart_count",
                condition=">",
                threshold=5.0,
                duration="5m",
                severity="critical",
            ),
            AlertRule(
                name="HighCpuUsage",
                description="CPU usage exceeds 90%",
                metric="cpu_usage",
                condition=">",
                threshold=90.0,
                duration="10m",
                severity="warning",
            ),
        ]

    async def create_rule(self, rule: AlertRule) -> AlertRule:
        return rule

    async def acknowledge(self, alert_id: str) -> bool:
        return True

    async def resolve(self, alert_id: str) -> bool:
        return True
