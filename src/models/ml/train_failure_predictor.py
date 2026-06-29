import os
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
import xgboost as xgb
import lightgbm as lgb

warnings.filterwarnings("ignore")


def generate_synthetic_failure_data(n_samples: int = 10000) -> pd.DataFrame:
    np.random.seed(42)
    data = {
        "cpu_usage": np.random.uniform(0, 100, n_samples),
        "memory_usage": np.random.uniform(0, 100, n_samples),
        "disk_usage": np.random.uniform(0, 100, n_samples),
        "network_errors": np.random.poisson(2, n_samples),
        "restart_count": np.random.poisson(1, n_samples),
        "pod_age_hours": np.random.exponential(48, n_samples),
        "container_restarts": np.random.poisson(1, n_samples),
        "oom_score": np.random.exponential(10, n_samples),
        "fs_inodes_free": np.random.uniform(0, 100, n_samples),
        "fs_inodes_used": np.random.uniform(0, 100, n_samples),
    }
    df = pd.DataFrame(data)

    failure_score = (
        (df["cpu_usage"] > 90).astype(int) * 2 +
        (df["memory_usage"] > 90).astype(int) * 2 +
        (df["disk_usage"] > 95).astype(int) * 3 +
        (df["restart_count"] > 3).astype(int) * 3 +
        (df["network_errors"] > 5).astype(int) * 2 +
        (df["container_restarts"] > 2).astype(int) * 2
    )

    df["failure"] = (failure_score >= 5).astype(int)
    return df


def train_models():
    print("=" * 60)
    print("KubeHeal AI - Failure Predictor Training")
    print("=" * 60)

    print("\n[1/6] Generating synthetic training data...")
    df = generate_synthetic_failure_data(10000)
    print(f"    Generated {len(df)} samples")
    print(f"    Failure rate: {df['failure'].mean():.2%}")

    print("\n[2/6] Preparing features...")
    feature_cols = [c for c in df.columns if c != "failure"]
    X = df[feature_cols]
    y = df["failure"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"    Train: {len(X_train)}, Test: {len(X_test)}")

    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, n_jobs=-1
        ),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, use_label_encoder=False, eval_metric="logloss"
        ),
        "LightGBM": lgb.LGBMClassifier(
            n_estimators=100, max_depth=6, learning_rate=0.1,
            random_state=42, verbose=-1
        ),
    }

    results = {}
    best_model = None
    best_score = 0.0
    best_name = ""

    print("\n[3/6] Training models...")
    for name, model in models.items():
        print(f"    Training {name}...")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_proba)

        results[name] = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "roc_auc": roc_auc,
        }

        print(f"      Accuracy:  {accuracy:.4f}")
        print(f"      Precision: {precision:.4f}")
        print(f"      Recall:    {recall:.4f}")
        print(f"      F1 Score:  {f1:.4f}")
        print(f"      ROC AUC:   {roc_auc:.4f}")

        if f1 > best_score:
            best_score = f1
            best_model = model
            best_name = name

    print(f"\n[4/6] Best model: {best_name} (F1: {best_score:.4f})")

    print("\n[5/6] Saving models...")
    output_dir = Path("artifacts/models")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "failure_predictor.pkl", "wb") as f:
        pickle.dump(best_model, f)
    print(f"    Saved failure_predictor.pkl")

    with open(output_dir / "feature_columns.pkl", "wb") as f:
        pickle.dump(feature_cols, f)
    print(f"    Saved feature_columns.pkl")

    print("\n[6/6] Training complete!")
    print("=" * 60)

    return results


if __name__ == "__main__":
    train_models()
