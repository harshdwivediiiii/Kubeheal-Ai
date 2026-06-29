import os
import sys
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectKBest, f_classif

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)


def run_eda():
    print("=" * 60)
    print("KUBEHEAL AI - EXPLORATORY DATA ANALYSIS")
    print("=" * 60)

    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    all_files = list(processed_dir.glob("*.csv"))
    if not all_files:
        print("\nNo CSV files found in data/processed/.")
        print("Generating sample EDA on synthetic data...")
        df = generate_sample_data()
    else:
        csv_file = all_files[0]
        print(f"\nAnalyzing: {csv_file.name}")
        df = pd.read_csv(csv_file)

    print(f"\n[1/6] Dataset Overview")
    print(f"    Shape: {df.shape}")
    print(f"    Columns: {list(df.columns)}")
    print(f"    Memory: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")

    print(f"\n[2/6] Data Cleaning")
    print(f"    Null values:\n{df.isnull().sum()}")
    print(f"    Duplicates: {df.duplicated().sum()}")

    df = df.drop_duplicates()
    for col in df.select_dtypes(include=[np.number]).columns:
        df[col] = df[col].fillna(df[col].median())
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown")

    print(f"\n[3/6] Statistical Summary")
    print(df.describe().to_string())

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    print(f"\n[4/6] Feature Engineering")
    encoders = {}
    for col in categorical_cols:
        if df[col].nunique() > 1 and df[col].nunique() <= 50:
            le = LabelEncoder()
            df[f"{col}_encoded"] = le.fit_transform(df[col].astype(str))
            encoders[col] = le

    scaler = StandardScaler()
    if numeric_cols:
        scaled_features = scaler.fit_transform(df[numeric_cols])
        df_scaled = pd.DataFrame(
            scaled_features,
            columns=[f"{col}_scaled" for col in numeric_cols],
        )
        df = pd.concat([df, df_scaled], axis=1)
        print(f"    Scaled {len(numeric_cols)} numeric features")

    print(f"\n[5/6] Feature Selection")
    encoded_cols = [f"{c}_encoded" for c in categorical_cols if f"{c}_encoded" in df.columns]
    scaled_cols = [f"{c}_scaled" for c in numeric_cols]
    all_features = encoded_cols + scaled_cols
    all_features = [c for c in all_features if c in df.columns]

    if len(all_features) >= 2 and "failure" in df.columns or y_col_exists(df):
        target = "failure" if "failure" in df.columns else find_target_col(df)
        if target:
            print(f"    Target column: {target}")
            X = df[all_features].fillna(0)
            y = LabelEncoder().fit_transform(df[target].astype(str))

            selector = SelectKBest(f_classif, k=min(10, len(all_features)))
            selector.fit(X, y)
            selected_indices = selector.get_support(indices=True)
            selected_features = [all_features[i] for i in selected_indices]
            print(f"    Selected {len(selected_features)} best features")
            for feat, score in sorted(
                zip(all_features, selector.scores_),
                key=lambda x: x[1],
                reverse=True,
            )[:10]:
                print(f"      {feat}: {score:.2f}")

    print(f"\n[6/6] Saving Processed Dataset")
    output_path = processed_dir / "final_processed_dataset.csv"
    df.to_csv(output_path, index=False)
    print(f"    Saved to {output_path}")

    plot_path = Path("artifacts/plots")
    plot_path.mkdir(parents=True, exist_ok=True)

    print("\nEDA Complete!")
    print("=" * 60)


def generate_sample_data():
    np.random.seed(42)
    n = 1000
    data = {
        "cpu_usage": np.random.uniform(0, 100, n),
        "memory_usage": np.random.uniform(0, 100, n),
        "disk_usage": np.random.uniform(0, 100, n),
        "network_errors": np.random.poisson(2, n),
        "restart_count": np.random.poisson(1, n),
        "pod_age_hours": np.random.exponential(48, n),
        "error_rate": np.random.exponential(0.5, n),
        "latency_ms": np.random.exponential(100, n),
        "severity": np.random.choice(["info", "warning", "critical", "ok"], n),
        "pod_status": np.random.choice(["Running", "Pending", "Failed", "CrashLoopBackOff"], n, p=[0.7, 0.1, 0.1, 0.1]),
    }
    df = pd.DataFrame(data)

    score = (
        (df["cpu_usage"] > 85).astype(int) +
        (df["memory_usage"] > 85).astype(int) +
        (df["restart_count"] > 3).astype(int) * 2 +
        (df["network_errors"] > 5).astype(int)
    )
    df["failure"] = (score >= 2).astype(int)
    return df


def y_col_exists(df):
    return any(c in df.columns for c in ["y", "label", "target", "class", "anomaly", "failure"])


def find_target_col(df):
    for c in ["failure", "anomaly", "label", "target", "class", "y"]:
        if c in df.columns:
            return c
    return None


if __name__ == "__main__":
    run_eda()
