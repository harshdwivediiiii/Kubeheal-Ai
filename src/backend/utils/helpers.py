import json
import yaml
from pathlib import Path
from typing import Any, Dict


def load_config(path: str) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {}

    with open(path) as f:
        if path.suffix in (".yaml", ".yml"):
            return yaml.safe_load(f)
        elif path.suffix == ".json":
            return json.load(f)
        return {}


def ensure_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def format_bytes(bytes_val: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


def parse_k8s_duration(duration_str: str) -> int:
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    if duration_str[-1] in units:
        return int(duration_str[:-1]) * units[duration_str[-1]]
    return int(duration_str)
