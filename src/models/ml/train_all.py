from src.models.ml.train_failure_predictor import train_models as train_failure
from src.models.ml.train_anomaly_detector import train_anomaly_detector
from src.models.ml.train_severity_classifier import train_severity_classifier


def train_all_models():
    print("\n" + "=" * 60)
    print("KUBEHEAL AI - COMPLETE MODEL TRAINING PIPELINE")
    print("=" * 60 + "\n")

    train_failure()
    print("\n" + "-" * 60 + "\n")
    train_anomaly_detector()
    print("\n" + "-" * 60 + "\n")
    train_severity_classifier()

    print("\n" + "=" * 60)
    print("ALL MODELS TRAINED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    train_all_models()
