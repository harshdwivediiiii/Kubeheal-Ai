import os
from typing import List, Optional

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from src.backend.models.pod import PodStatus, PodLog
from src.backend.core.config import settings


class KubernetesService:
    def __init__(self):
        self._init_client()

    def _init_client(self):
        if settings.in_cluster:
            config.load_incluster_config()
        else:
            kubeconfig = os.path.expanduser(settings.kubeconfig_path)
            if os.path.exists(kubeconfig):
                config.load_kube_config(kubeconfig)
            else:
                config.load_incluster_config()
        self.core_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()

    async def list_pods(self, namespace: str = "default") -> List[PodStatus]:
        try:
            pods = self.core_v1.list_namespaced_pod(namespace)
            return [self._parse_pod(pod) for pod in pods.items]
        except ApiException as e:
            print(f"Error listing pods: {e}")
            return []

    async def get_pod(self, namespace: str, pod_name: str) -> Optional[PodStatus]:
        try:
            pod = self.core_v1.read_namespaced_pod(pod_name, namespace)
            return self._parse_pod(pod)
        except ApiException:
            return None

    async def get_pod_logs(
        self, namespace: str, pod_name: str, tail_lines: int = 100
    ) -> List[PodLog]:
        try:
            log = self.core_v1.read_namespaced_pod_log(
                pod_name, namespace, tail_lines=tail_lines
            )
            return self._parse_logs(pod_name, namespace, log)
        except ApiException:
            return []

    async def list_failing_pods(self) -> List[PodStatus]:
        all_pods = await self.list_pods()
        failing_keywords = [
            "CrashLoopBackOff", "Error", "ImagePullBackOff",
            "Init:CrashLoopBackOff", "CreateContainerConfigError",
        ]
        return [
            pod for pod in all_pods
            if pod.status in failing_keywords or pod.restart_count >= 3
        ]

    def delete_pod(self, namespace: str, pod_name: str) -> bool:
        try:
            self.core_v1.delete_namespaced_pod(pod_name, namespace)
            return True
        except ApiException:
            return False

    def _parse_pod(self, pod) -> PodStatus:
        metadata = pod.metadata
        status = pod.status
        container_statuses = status.container_statuses or []

        restart_count = sum(
            cs.restart_count for cs in container_statuses
        )

        return PodStatus(
            name=metadata.name,
            namespace=metadata.namespace,
            status=status.phase if status.phase else "Unknown",
            restart_count=restart_count,
            age="",
            node=status.host_ip or "",
            ip=status.pod_ip or "",
            phase=status.phase or "",
            conditions=[c.type for c in (status.conditions or []) if c.status == "True"],
        )

    def _parse_logs(
        self, pod_name: str, namespace: str, log_text: str
    ) -> List[PodLog]:
        logs = []
        for line in log_text.strip().split("\n"):
            if line:
                logs.append(
                    PodLog(
                        pod_name=pod_name,
                        namespace=namespace,
                        container="",
                        timestamp=None,
                        level="INFO",
                        message=line,
                    )
                )
        return logs
