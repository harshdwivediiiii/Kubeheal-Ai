from fastapi import FastAPI, HTTPException
from kubernetes import client, config
from kubernetes.client.rest import ApiException

app = FastAPI(title="KubeHeal AI Log Analyzer")

# Load kube config: in-cluster when running as a pod, local kubeconfig otherwise
try:
    config.load_incluster_config()
except config.ConfigException:
    config.load_kube_config()

v1 = client.CoreV1Api()

# Rule-based pattern matcher — keeps it simple, no heavy AI needed
RULES = [
    {
        "pattern": "CrashLoopBackOff",
        "issue": "Pod is crashing repeatedly.",
        "fix": "Run: kubectl logs <pod> --previous\nCheck for app startup errors, missing env vars, or bad config.",
    },
    {
        "pattern": "OOMKilled",
        "issue": "Container ran out of memory and was killed.",
        "fix": "Increase memory limits in deployment.yaml or fix a memory leak in the app.",
    },
    {
        "pattern": "ImagePullBackOff",
        "issue": "Kubernetes cannot pull the container image.",
        "fix": "Check image name/tag is correct. For Minikube: run eval $(minikube docker-env) before docker build.",
    },
    {
        "pattern": "ErrImageNeverPull",
        "issue": "Image not found locally and imagePullPolicy is Never.",
        "fix": "Run eval $(minikube docker-env) then rebuild the image inside Minikube.",
    },
    {
        "pattern": "connection refused",
        "issue": "App cannot connect to a dependency (DB, service, etc.).",
        "fix": "Check the service name and port in your config. Verify the target pod is Running.",
    },
    {
        "pattern": "process.exit",
        "issue": "Application called process.exit — intentional or unhandled crash.",
        "fix": "Check app code for unhandled exceptions or explicit exit calls. Review logs above this line.",
    },
    {
        "pattern": "ENOMEM",
        "issue": "Out of memory error at OS level.",
        "fix": "Increase memory limits in deployment.yaml.",
    },
    {
        "pattern": "Error",
        "issue": "Generic error detected in logs.",
        "fix": "Review full logs with: kubectl logs <pod> --previous",
    },
]


def analyze_logs(log_text: str) -> dict:
    for rule in RULES:
        if rule["pattern"].lower() in log_text.lower():
            return {"issue": rule["issue"], "fix": rule["fix"], "matched_pattern": rule["pattern"]}
    return {"issue": "No known issue detected.", "fix": "Logs look clean.", "matched_pattern": None}


@app.get("/")
def root():
    return {"status": "ok", "service": "KubeHeal AI Log Analyzer"}


@app.get("/analyze/{namespace}/{pod_name}")
def analyze_pod(namespace: str, pod_name: str, previous: bool = False):
    try:
        logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            previous=previous,
            tail_lines=100,
        )
    except ApiException as e:
        if e.status == 404:
            raise HTTPException(status_code=404, detail=f"Pod '{pod_name}' not found in namespace '{namespace}'")
        raise HTTPException(status_code=500, detail=str(e))

    result = analyze_logs(logs)
    return {
        "pod": pod_name,
        "namespace": namespace,
        "previous_logs": previous,
        "log_tail": logs[-500:] if logs else "",
        **result,
    }


@app.get("/pods/{namespace}")
def list_pods(namespace: str):
    try:
        pods = v1.list_namespaced_pod(namespace=namespace)
        return {
            "namespace": namespace,
            "pods": [
                {
                    "name": p.metadata.name,
                    "status": p.status.phase,
                    "restarts": sum(
                        cs.restart_count for cs in (p.status.container_statuses or [])
                    ),
                }
                for p in pods.items
            ],
        }
    except ApiException as e:
        raise HTTPException(status_code=500, detail=str(e))
