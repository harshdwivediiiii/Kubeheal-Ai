from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    project_name: str = "KubeHeal AI"
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_log_level: str = "info"

    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "kubeheal"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    kubeconfig_path: str = "~/.kube/config"
    kubernetes_namespace: str = "default"
    in_cluster: bool = False

    prometheus_url: str = "http://localhost:9090"
    prometheus_scrape_interval: int = 15

    models_dir: str = "artifacts/models"
    mlflow_tracking_uri: str = "file:./artifacts/mlflow"

    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    vector_store_type: str = "chroma"

    docker_registry: str = "docker.io"
    docker_username: Optional[str] = None
    docker_password: Optional[str] = None
    image_tag: str = "latest"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
