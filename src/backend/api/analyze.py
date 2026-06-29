from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.backend.services.log_analyzer import LogAnalyzer
from src.backend.services.ml_inference import MLInferenceService

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post("/logs")
async def analyze_logs(
    namespace: str,
    pod_name: str,
    previous: bool = Query(False),
):
    analyzer = LogAnalyzer()
    result = await analyzer.analyze_pod_logs(namespace, pod_name, previous)
    return result


@router.post("/failure")
async def analyze_failure(namespace: str, pod_name: str):
    analyzer = LogAnalyzer()
    failure_analysis = await analyzer.analyze_failure(namespace, pod_name)
    return failure_analysis


@router.post("/root-cause")
async def root_cause_analysis(namespace: str, pod_name: str):
    analyzer = LogAnalyzer()
    rca = await analyzer.root_cause_analysis(namespace, pod_name)
    return rca


@router.post("/suggest-fix")
async def suggest_fix(namespace: str, pod_name: str):
    analyzer = LogAnalyzer()
    fix = await analyzer.suggest_fix(namespace, pod_name)
    return fix
