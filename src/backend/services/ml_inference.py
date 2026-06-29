import os
import pickle
from typing import Optional

import numpy as np
import pandas as pd

from src.backend.models.pod import PodPrediction, PodStatus
from src.backend.core.config import settings


class MLInferenceService:
    def __init__(self):
        self.models = {}
        self._load_models()

    def _load_models(self):
        models_dir = settings.models_dir
        if not os.path.exists(models_dir):
            os.makedirs(models_dir, exist_ok=True)
            return

        model_files = {
            "failure_predictor": "failure_predictor.pkl",
            "anomaly_detector": "anomaly_detector.pkl",
            "severity_classifier": "severity_classifier.pkl",
        }

        for name, filename in model_files.items():
            path = os.path.join(models_dir, filename)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    self.models[name] = pickle.load(f)

    async def predict_failure(self, pod: PodStatus) -> PodPrediction:
        if "failure_predictor" not in self.models:
            return self._default_prediction(pod)

        features = self._extract_features(pod)
        model = self.models["failure_predictor"]

        try:
            proba = model.predict_proba(features)[0][1]
            pred = model.predict(features)[0]
        except Exception:
            return self._default_prediction(pod)

        return PodPrediction(
            pod_name=pod.name,
            namespace=pod.namespace,
            failure_probability=float(proba),
            predicted_failure_type=str(pred),
            confidence=float(max(proba, 1 - proba)),
            timestamp=datetime.utcnow(),
        )

    async def predict_anomaly(self, metrics: dict) -> dict:
        if "anomaly_detector" not in self.models:
            return {"is_anomaly": False, "anomaly_score": 0.0}

        model = self.models["anomaly_detector"]
        features = np.array([[metrics.get(k, 0) for k in
                              ["cpu", "memory", "disk", "network"]]])
        score = model.decision_function(features)[0]
        is_anomaly = model.predict(features)[0] == -1

        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": float(score),
        }

    def _extract_features(self, pod: PodStatus) -> pd.DataFrame:
        data = {
            "restart_count": [pod.restart_count],
            "phase_encoded": [self._encode_phase(pod.phase)],
        }
        return pd.DataFrame(data)

    def _encode_phase(self, phase: str) -> int:
        phases = {"Pending": 0, "Running": 1, "Succeeded": 2, "Failed": 3, "Unknown": 4}
        return phases.get(phase, 4)

    def _default_prediction(self, pod: PodStatus) -> PodPrediction:
        return PodPrediction(
            pod_name=pod.name,
            namespace=pod.namespace,
            failure_probability=min(1.0, pod.restart_count / 5),
            predicted_failure_type="CrashLoopBackOff" if pod.restart_count >= 3 else "Stable",
            confidence=0.5,
            timestamp=datetime.utcnow(),
        )
