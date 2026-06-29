from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from src.backend.models.alert import Alert, AlertRule, AlertResponse
from src.backend.services.alert_manager import AlertManager

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=AlertResponse)
async def list_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    manager = AlertManager()
    alerts = await manager.get_alerts(severity, status, page, page_size)
    return alerts


@router.get("/rules", response_model=List[AlertRule])
async def list_alert_rules():
    manager = AlertManager()
    rules = await manager.get_rules()
    return rules


@router.post("/rules", response_model=AlertRule)
async def create_alert_rule(rule: AlertRule):
    manager = AlertManager()
    created = await manager.create_rule(rule)
    return created


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    manager = AlertManager()
    result = await manager.acknowledge(alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "acknowledged"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    manager = AlertManager()
    result = await manager.resolve(alert_id)
    if not result:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "resolved"}
