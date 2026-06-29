import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.ml.train_all import train_all_models


def run_training_pipeline():
    print("=" * 60)
    print("KUBEHEAL AI - TRAINING PIPELINE")
    print("=" * 60)

    print("\n[1/3] Running dataset preparation...")
    os.makedirs("data/processed", exist_ok=True)
    print("    Data directories ready")

    print("\n[2/3] Training all ML models...")
    train_all_models()

    print("\n[3/3] Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_training_pipeline()
