import os
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")


def generate_severity_data(n_samples: int = 5000) -> pd.DataFrame:
    np.random.seed(42)

    data = {
        "restart_count": np.random.poisson(2, n_samples),
        "cpu_usage": np.random.uniform(0, 100, n_samples),
        "memory_usage": np.random.uniform(0, 100, n_samples),
        "error_count": np.random.poisson(5, n_samples),
        "response_time_ms": np.random.exponential(200, n_samples),
        "pod_count": np.random.poisson(5, n_samples),
        "node_count": np.random.poisson(3, n_samples),
        "network_errors": np.random.poisson(2, n_samples),
        "disk_io_wait": np.random.exponential(50, n_samples),
    }
    df = pd.DataFrame(data)

    conditions = [
        (df["restart_count"] >= 5) | (df["error_count"] >= 10),
        (df["restart_count"] >= 3) | (df["cpu_usage"] > 90) | (df["memory_usage"] > 90),
        (df["restart_count"] >= 1) | (df["error_count"] >= 3),
    ]
    choices = ["critical", "warning", "info"]
    df["severity"] = np.select(conditions, choices, default="ok")
    return df


def train_severity_classifier():
    print("=" * 60)
    print("KubeHeal AI - Severity Classifier Training")
    print("=" * 60)

    print("\n[1/4] Generating synthetic data...")
    df = generate_severity_data(5000)
    print(f"    Generated {len(df)} samples")
    print(f"    Severity distribution:\n{df['severity'].value_counts()}")

    print("\n[2/4] Preparing features...")
    feature_cols = [c for c in df.columns if c != "severity"]
    X = df[feature_cols]
    y = df["severity"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )

    print("\n[3/4] Training Gradient Boosting classifier...")
    model = GradientBoostingClassifier(
        n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"    Accuracy: {accuracy:.4f}")

    print(f"\n    Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    print("\n[4/4] Saving models...")
    output_dir = Path("artifacts/models")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "severity_classifier.pkl", "wb") as f:
        pickle.dump(model, f)
    print(f"    Saved severity_classifier.pkl")

    with open(output_dir / "severity_encoder.pkl", "wb") as f:
        pickle.dump(le, f)
    print(f"    Saved severity_encoder.pkl")

    print("\nTraining complete!")
    print("=" * 60)


if __name__ == "__main__":
    train_severity_classifier()
