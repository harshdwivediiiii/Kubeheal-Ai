import os
import json
import zipfile
import subprocess
from pathlib import Path

import requests
from tqdm import tqdm


def setup_kaggle():
    print("[1/5] Setting up Kaggle API...")
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)

    kaggle_json = kaggle_dir / "kaggle.json"
    if not kaggle_json.exists():
        username = os.getenv("KAGGLE_USERNAME", "")
        key = os.getenv("KAGGLE_KEY", "")
        if username and key:
            with open(kaggle_json, "w") as f:
                json.dump({"username": username, "key": key}, f)
            kaggle_json.chmod(0o600)
            print("    Kaggle credentials configured from environment variables")
        else:
            print("    WARNING: Kaggle credentials not found. Set KAGGLE_USERNAME and KAGGLE_KEY")


def download_kaggle_dataset(dataset: str, output_dir: Path):
    print(f"    Downloading {dataset}...")
    result = subprocess.run(
        ["kaggle", "datasets", "download", dataset, "-p", str(output_dir)],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        zip_files = list(output_dir.glob("*.zip"))
        for zf in zip_files:
            with zipfile.ZipFile(zf, "r") as zip_ref:
                zip_ref.extractall(output_dir)
            zf.unlink()
            print(f"    Extracted {zf.name}")
        return True
    else:
        print(f"    Failed: {result.stderr[:100]}")
        return False


def download_direct_url(url: str, output_path: Path):
    print(f"    Downloading {output_path.name}...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))
        with open(output_path, "wb") as f:
            with tqdm(total=total, unit="B", unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        return True
    except Exception as e:
        print(f"    Failed: {e}")
        return False


def download_all_datasets():
    print("=" * 60)
    print("KUBEHEAL AI - DATASET DOWNLOADER")
    print("=" * 60)

    raw_dir = Path("data/raw")
    raw_dir.mkdir(parents=True, exist_ok=True)

    setup_kaggle()

    kaggle_datasets = [
        "harshdwivediiiii/kubernetes-pod-failure-dataset",
        "harshdwivediiiii/prometheus-metrics-dataset",
        "harshdwivediiiii/linux-system-logs",
        "harshdwivediiiii/hdfs-log-dataset",
        "harshdwivediiiii/bgl-log-dataset",
        "harshdwivediiiii/openstack-logs",
        "harshdwivediiiii/failure-prediction-dataset",
        "harshdwivediiiii/anomaly-detection-dataset",
        "harshdwivediiiii/server-metrics-dataset",
        "harshdwivediiiii/container-metrics-dataset",
    ]

    kaggle_available = False
    try:
        subprocess.run(["kaggle", "--version"], capture_output=True)
        kaggle_available = True
    except FileNotFoundError:
        print("\nWARNING: Kaggle CLI not installed. Install with: pip install kaggle")

    print(f"\n[2/5] Downloading Kaggle datasets ({len(kaggle_datasets)} total)...")
    for ds in kaggle_datasets:
        dataset_name = ds.split("/")[-1]
        dataset_dir = raw_dir / dataset_name
        dataset_dir.mkdir(exist_ok=True)

        if kaggle_available:
            download_kaggle_dataset(ds, dataset_dir)
        else:
            print(f"    Skipping {dataset_name} (Kaggle CLI not available)")

    print(f"\n[3/5] Creating synthetic datasets...")
    create_synthetic_datasets(raw_dir)

    print(f"\n[4/5] Organizing datasets...")
    organize_datasets(raw_dir)

    print(f"\n[5/5] Dataset download complete!")
    print("=" * 60)


def create_synthetic_datasets(raw_dir: Path):
    import csv
    import numpy as np

    datasets = {
        "synthetic_kubernetes_logs.csv": [
            "timestamp,pod_name,namespace,container,level,message",
            [
                f"2024-01-01T00:00:{str(i).zfill(2)}Z,pod-{i % 10},default,container-0,{np.random.choice(['INFO','WARN','ERROR','FATAL'], p=[0.7,0.15,0.1,0.05])},{np.random.choice(['Pod started','Health check passed','OOMKilled','CrashLoopBackOff','ImagePullBackOff'])}"
                for i in range(1000)
            ],
        ],
        "synthetic_crashloop.csv": [
            "pod_name,namespace,restart_count,cpu_request,cpu_limit,memory_request,memory_limit,reason,last_exit_code,last_message",
            [
                f"pod-{i},default,{int(np.random.exponential(2))},100m,500m,256Mi,512Mi,{np.random.choice(['OOMKilled','Error','Completed','ContainerCannotRun'])},{np.random.choice([0,1,137,139])},\"Error message {i}\""
                for i in range(500)
            ],
        ],
        "node_exporter_metrics.csv": [
            "timestamp,node,cpu_usage,memory_usage,disk_usage,network_rx,network_tx,load_1m,load_5m,load_15m",
            [
                f"2024-01-01T00:00:00Z,node-{i%3},{np.random.uniform(0,100):.2f},{np.random.uniform(0,100):.2f},{np.random.uniform(0,100):.2f},{np.random.uniform(0,1000):.2f},{np.random.uniform(0,1000):.2f},{np.random.uniform(0,5):.2f},{np.random.uniform(0,4):.2f},{np.random.uniform(0,3):.2f}"
                for i in range(500)
            ],
        ],
        "github_issues_kubernetes.csv": [
            "issue_id,title,body,labels,state,created_at,comments_count",
            [
                f"{i},\"Kubernetes issue {i}\",\"Description of issue {i}\",\"{np.random.choice(['kind/bug','kind/feature','area/networking','sig/node'])}\",{np.random.choice(['open','closed'])},2024-01-01,{int(np.random.poisson(5))}"
                for i in range(500)
            ],
        ],
    }

    for name, (header, rows) in datasets.items():
        filepath = raw_dir / name
        with open(filepath, "w") as f:
            f.write(header + "\n")
            f.write("\n".join(rows))
        print(f"    Created {name} ({len(rows)} rows)")


def organize_datasets(raw_dir: Path):
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    for dataset_dir in raw_dir.iterdir():
        if dataset_dir.is_dir():
            csv_files = list(dataset_dir.glob("*.csv"))
            for csv_file in csv_files:
                dest = processed_dir / csv_file.name
                if not dest.exists():
                    import shutil
                    shutil.copy2(csv_file, dest)
                    print(f"    Copied {csv_file.name} to processed/")


if __name__ == "__main__":
    download_all_datasets()
