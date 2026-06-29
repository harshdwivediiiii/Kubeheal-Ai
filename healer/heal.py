import os
import time
import logging
from datetime import datetime

from kubernetes import client, config
from kubernetes.client.rest import ApiException

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("kubeheal-healer")


class KubeHealHealer:
    def __init__(self, namespace: str = "default"):
        self.namespace = namespace
        self._init_client()
        self.failure_patterns = {
            "CrashLoopBackOff": self._handle_crashloop,
            "OOMKilled": self._handle_oom,
            "ImagePullBackOff": self._handle_image_pull,
            "NodeLost": self._handle_node_lost,
            "CreateContainerConfigError": self._handle_config_error,
        }

    def _init_client(self):
        try:
            config.load_incluster_config()
        except config.ConfigException:
            config.load_kube_config()
        self.core_v1 = client.CoreV1Api()

    def scan_and_heal(self):
        logger.info(f"Scanning pods in namespace: {self.namespace}")
        try:
            pods = self.core_v1.list_namespaced_pod(self.namespace)
        except ApiException as e:
            logger.error(f"Failed to list pods: {e}")
            return

        for pod in pods.items:
            self._analyze_pod(pod)

    def _analyze_pod(self, pod):
        name = pod.metadata.name
        status = pod.status

        if status.container_statuses:
            for container_status in status.container_statuses:
                state = container_status.state
                waiting = state.waiting
                terminated = state.terminated

                if waiting and waiting.reason in self.failure_patterns:
                    logger.warning(f"🔴 {name}: {waiting.reason} - {waiting.message}")
                    self.failure_patterns[waiting.reason](name, waiting.message)

                if terminated and terminated.reason == "OOMKilled":
                    logger.warning(f"🔴 {name}: OOMKilled (exit code: {terminated.exit_code})")
                    self._handle_oom(name, terminated.message)

                if container_status.restart_count >= 3:
                    logger.warning(f"⚠️  {name}: High restart count ({container_status.restart_count})")
                    self._auto_heal(name, container_status.restart_count)

    def _handle_crashloop(self, pod_name: str, message: str):
        logger.info(f"🔄 Attempting to heal {pod_name} (CrashLoopBackOff)")
        self._restart_pod(pod_name)

    def _handle_oom(self, pod_name: str, message: str):
        logger.info(f"🔄 Increasing memory for {pod_name} (OOMKilled)")
        try:
            deployment_name = self._get_deployment_name(pod_name)
            if deployment_name:
                apps_v1 = client.AppsV1Api()
                deployment = apps_v1.read_namespaced_deployment(deployment_name, self.namespace)
                containers = deployment.spec.template.spec.containers
                for container in containers:
                    if container.resources and container.resources.limits:
                        old_limit = container.resources.limits.get("memory", "256Mi")
                        new_limit = self._increase_memory(old_limit)
                        container.resources.limits["memory"] = new_limit
                        logger.info(f"    Memory limit: {old_limit} -> {new_limit}")
                apps_v1.patch_namespaced_deployment(deployment_name, self.namespace, deployment)
                logger.info(f"    ✅ Updated resources for {deployment_name}")
        except Exception as e:
            logger.error(f"    Failed to update resources: {e}")
            self._restart_pod(pod_name)

    def _handle_image_pull(self, pod_name: str, message: str):
        logger.info(f"🔄 Attempting to fix image pull for {pod_name}")
        logger.info(f"    Action: Check image name and registry credentials")

    def _handle_node_lost(self, pod_name: str, message: str):
        logger.info(f"🔄 Rescheduling {pod_name} from lost node")
        self._restart_pod(pod_name)

    def _handle_config_error(self, pod_name: str, message: str):
        logger.info(f"🔄 Checking ConfigMap/Secret references for {pod_name}")
        logger.info(f"    Error: {message}")

    def _restart_pod(self, pod_name: str):
        try:
            self.core_v1.delete_namespaced_pod(pod_name, self.namespace)
            logger.info(f"    ✅ Deleted {pod_name} - Kubernetes will recreate it")
        except ApiException as e:
            logger.error(f"    Failed to delete {pod_name}: {e}")

    def _get_deployment_name(self, pod_name: str) -> str:
        try:
            pod = self.core_v1.read_namespaced_pod(pod_name, self.namespace)
            for owner in pod.metadata.owner_references:
                if owner.kind == "ReplicaSet":
                    return "-".join(owner.name.split("-")[:-1])
                if owner.kind == "Deployment":
                    return owner.name
        except ApiException:
            pass
        return None

    def _increase_memory(self, current: str) -> str:
        units = {"Ki": 1024, "Mi": 1024**2, "Gi": 1024**3}
        for unit, multiplier in units.items():
            if current.endswith(unit):
                value = int(current[:-len(unit)])
                new_value = int(value * 1.5)
                return f"{new_value}{unit}"
        return "512Mi"

    def _auto_heal(self, pod_name: str, restart_count: int):
        if restart_count >= 5:
            logger.info(f"⚠️  High restart count ({restart_count}) - escalating to human operator")
        elif restart_count >= 3:
            logger.info(f"🔄 Auto-healing {pod_name} (restart count: {restart_count})")
            self._restart_pod(pod_name)

    def run_forever(self, interval: int = 30):
        logger.info("=" * 50)
        logger.info("KubeHeal AI - Self-Healing Agent Started")
        logger.info(f"Namespace: {self.namespace}")
        logger.info(f"Interval: {interval}s")
        logger.info("=" * 50)

        while True:
            try:
                self.scan_and_heal()
            except Exception as e:
                logger.error(f"Error during scan: {e}")
            time.sleep(interval)


if __name__ == "__main__":
    namespace = os.getenv("KUBERNETES_NAMESPACE", "default")
    interval = int(os.getenv("HEAL_INTERVAL", "30"))

    healer = KubeHealHealer(namespace)
    healer.run_forever(interval)
