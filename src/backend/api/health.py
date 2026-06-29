from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "KubeHeal AI",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/readiness")
async def readiness_check():
    return {"status": "ready"}


@router.get("/liveness")
async def liveness_check():
    return {"status": "alive"}
