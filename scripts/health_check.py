import os
import sys
import subprocess
from pathlib import Path


def check_python():
    print(f"Python: {sys.version}")
    assert sys.version_info >= (3, 9), "Python 3.9+ required"


def check_pip():
    result = subprocess.run(["pip", "--version"], capture_output=True, text=True)
    print(f"pip: {result.stdout.strip()}")


def check_docker():
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        print(f"Docker: {result.stdout.strip()}")
    except FileNotFoundError:
        print("Docker: NOT INSTALLED")


def check_kubectl():
    try:
        result = subprocess.run(["kubectl", "version", "--client"], capture_output=True, text=True)
        print(f"kubectl: {result.stdout.strip()}")
    except FileNotFoundError:
        print("kubectl: NOT INSTALLED")


def check_minikube():
    try:
        result = subprocess.run(["minikube", "version"], capture_output=True, text=True)
        print(f"Minikube: {result.stdout.strip()}")
    except FileNotFoundError:
        print("Minikube: NOT INSTALLED")


def check_helm():
    try:
        result = subprocess.run(["helm", "version", "--short"], capture_output=True, text=True)
        print(f"Helm: {result.stdout.strip()}")
    except FileNotFoundError:
        print("Helm: NOT INSTALLED")


def check_mongodb():
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.server_info()
        print("MongoDB: Connected")
    except Exception as e:
        print(f"MongoDB: {e}")


def check_directories():
    required_dirs = [
        "src", "src/backend", "src/dashboard", "src/models",
        "data/raw", "data/processed", "data/features",
        "logs", "artifacts/models", "configs", "docker",
        "k8s", "tests", "docs", "notebooks", "requirements",
        ".github/workflows",
    ]
    for d in required_dirs:
        path = Path(d)
        if path.exists():
            print(f"  ✅ {d}")
        else:
            print(f"  ❌ {d}")


def check_packages():
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "streamlit",
        "plotly", "pandas", "numpy", "scikit-learn",
        "kubernetes", "pymongo", "redis",
        "transformers", "sentence-transformers",
        "xgboost", "lightgbm",
    ]
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")


def main():
    print("=" * 60)
    print("KUBEHEAL AI - HEALTH CHECK")
    print("=" * 60)

    print("\n[1/7] Python Environment")
    check_python()
    check_pip()

    print("\n[2/7] Docker & Kubernetes Tools")
    check_docker()
    check_kubectl()
    check_minikube()
    check_helm()

    print("\n[3/7] MongoDB")
    check_mongodb()

    print("\n[4/7] Project Structure")
    check_directories()

    print("\n[5/7] Python Packages")
    check_packages()

    print("\n[6/7] Git Status")
    result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)
    print(f"    {result.stdout.strip() if result.stdout.strip() else 'Clean'}")

    print("\n[7/7] Environment Variables")
    env_vars = ["KAGGLE_USERNAME", "KAGGLE_KEY", "OPENAI_API_KEY", "MONGODB_URI", "SECRET_KEY"]
    for var in env_vars:
        val = os.getenv(var, "")
        masked = val[:8] + "..." if len(val) > 8 else "(not set)"
        print(f"    {var}: {masked}")

    print("\n" + "=" * 60)
    print("Health check complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
