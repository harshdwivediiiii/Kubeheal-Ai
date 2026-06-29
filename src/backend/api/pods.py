from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from src.backend.models.pod import PodStatus, PodPrediction, PodLog
from src.backend.services.kubernetes import KubernetesService
from src.backend.services.ml_inference import MLInferenceService

router = APIRouter(prefix="/pods", tags=["Pods"])


@router.get("/", response_model=List[PodStatus])
async def list_pods(namespace: Optional[str] = "default"):
    k8s = KubernetesService()
    pods = await k8s.list_pods(namespace)
    return pods


@router.get("/{namespace}/{pod_name}", response_model=PodStatus)
async def get_pod(namespace: str, pod_name: str):
    k8s = KubernetesService()
    pod = await k8s.get_pod(namespace, pod_name)
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    return pod


@router.get("/{namespace}/{pod_name}/logs", response_model=List[PodLog])
async def get_pod_logs(namespace: str, pod_name: str, tail_lines: int = 100):
    k8s = KubernetesService()
    logs = await k8s.get_pod_logs(namespace, pod_name, tail_lines)
    return logs


@router.get("/{namespace}/{pod_name}/predict", response_model=PodPrediction)
async def predict_pod_failure(namespace: str, pod_name: str):
    k8s = KubernetesService()
    pod = await k8s.get_pod(namespace, pod_name)
    if not pod:
        raise HTTPException(status_code=404, detail="Pod not found")
    ml = MLInferenceService()
    prediction = await ml.predict_failure(pod)
    return prediction


@router.get("/failing", response_model=List[PodStatus])
async def list_failing_pods():
    k8s = KubernetesService()
    pods = await k8s.list_failing_pods()
    return pods
