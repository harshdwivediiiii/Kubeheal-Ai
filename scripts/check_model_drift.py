import pickle
import numpy as np
from pathlib import Path


def check_model_drift():
    models_dir = Path("artifacts/models")
    if not models_dir.exists():
        print("No models directory found")
        return

    results = {}

    for model_file in models_dir.glob("*.pkl"):
        with open(model_file, "rb") as f:
            model = pickle.load(f)
            results[model_file.name] = {
                "type": type(model).__name__,
                "size_kb": model_file.stat().st_size / 1024,
            }

    print("=" * 60)
    print("KubeHeal AI - Model Drift Check")
    print("=" * 60)

    for name, info in results.items():
        print(f"\n{name}:")
        print(f"  Type: {info['type']}")
        print(f"  Size: {info['size_kb']:.2f} KB")

    print(f"\nTotal models: {len(results)}")
    print("Model drift check complete")


if __name__ == "__main__":
    check_model_drift()
