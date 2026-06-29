from src.backend.api.auth import router as auth_router
from src.backend.api.pods import router as pods_router
from src.backend.api.alerts import router as alerts_router
from src.backend.api.health import router as health_router
from src.backend.api.analyze import router as analyze_router
from src.backend.api.metrics import router as metrics_router

routers = [
    auth_router,
    pods_router,
    alerts_router,
    health_router,
    analyze_router,
    metrics_router,
]

__all__ = ["routers"]
