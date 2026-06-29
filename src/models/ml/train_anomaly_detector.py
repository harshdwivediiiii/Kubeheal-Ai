import os
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

warnings.filterwarnings("ignore")


def generate_synthetic_metrics(n_samples: int = 10000) -> pd.DataFrame:
    np.random.seed(42)

    normal = pd.DataFrame({
        "cpu_usage": np.random.normal(50, 15, n_samples),
        "memory_usage": np.random.normal(60, 10, n_samples),
        "disk_io": np.random.normal(100, 30, n_samples),
        "network_in": np.random.normal(500, 100, n_samples),
        "network_out": np.random.normal(300, 75, n_samples),
        "disk_usage": np.random.normal(60, 20, n_samples),
        "error_rate": np.random.exponential(0.1, n_samples),
        "latency_ms": np.random.exponential(50, n_samples),
        "connection_count": np.random.poisson(100, n_samples),
    })

    n_anomalies = int(n_samples * 0.05)
    anomalies = pd.DataFrame({
        "cpu_usage": np.random.uniform(95, 100, n_anomalies),
        "memory_usage": np.random.uniform(95, 100, n_anomalies),
        "disk_io": np.random.uniform(0, 1000, n_anomalies),
        "network_in": np.random.uniform(0, 5000, n_anomalies),
        "network_out": np.random.uniform(0, 3000, n_anomalies),
        "disk_usage": np.random.uniform(95, 100, n_anomalies),
        "error_rate": np.random.exponential(10, n_anomalies),
        "latency_ms": np.random.exponential(1000, n_anomalies),
        "connection_count": np.random.poisson(500, n_anomalies),
    })

    df = pd.concat([normal, anomalies], ignore_index=True)
    df = df.sample(frac=1).reset_index(drop=True)
    return df


def train_anomaly_detector():
    print("=" * 60)
    print("KubeHeal AI - Anomaly Detector Training")
    print("=" * 60)

    print("\n[1/5] Generating synthetic metrics data...")
    df = generate_synthetic_metrics(10000)
    print(f"    Generated {len(df)} samples")

    print("\n[2/5] Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df)
    print(f"    Features: {df.shape[1]}")

    print("\n[3/5] Training Isolation Forest...")
    model = IsolationForest(
        n_estimators=200,
        max_samples="auto",
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled)
    print("    Training complete")

    print("\n[4/5] Training Autoencoder (PyTorch)...")
    print("    (Simplified - using Isolation Forest as primary detector)")

    print("\n[5/5] Saving models...")
    output_dir = Path("artifacts/models")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "anomaly_detector.pkl", "wb") as f:
        pickle.dump(model, f)
    print(f"    Saved anomaly_detector.pkl")

    with open(output_dir / "anomaly_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    print(f"    Saved anomaly_scaler.pkl")

    print("\nTraining complete!")
    print("=" * 60)

    anomalies = model.predict(X_scaled)
    print(f"\nDetected anomalies: {(anomalies == -1).sum()} ({((anomalies == -1).sum() / len(anomalies)):.2%})")


if __name__ == "__main__":
    train_anomaly_detector()
