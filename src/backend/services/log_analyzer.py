import re
from typing import Optional

from src.backend.services.kubernetes import KubernetesService


class LogAnalyzer:
    def __init__(self):
        self.k8s = KubernetesService()
        self.patterns = {
            "OOMKilled": [
                r"killed", r"out of memory", r"OOMKilled",
                r"memory cgroup out of memory",
            ],
            "CrashLoopBackOff": [
                r"CrashLoopBackOff", r"back-off", r"restarting",
            ],
            "ImagePullBackOff": [
                r"ImagePullBackOff", r"image pull", r"ErrImagePull",
                r"not found", r"repository does not exist",
            ],
            "CreateContainerConfigError": [
                r"CreateContainerConfigError", r"configmap",
                r"secret.*not found", r"env.*not found",
            ],
            "NodeLost": [
                r"node lost", r"NodeLost", r"node.*unreachable",
            ],
            "DiskPressure": [
                r"disk pressure", r"DiskPressure", r"no space left",
                r"disk full",
            ],
            "NetworkError": [
                r"connection refused", r"connection timeout",
                r"no route to host", r"network is unreachable",
                r"dial tcp.*i/o timeout",
            ],
        }

    async def analyze_pod_logs(
        self, namespace: str, pod_name: str, previous: bool = False
    ) -> dict:
        logs = await self.k8s.get_pod_logs(namespace, pod_name)
        messages = [log.message for log in logs]

        detected_issues = []
        for issue_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = [msg for msg in messages if re.search(pattern, msg, re.IGNORECASE)]
                if matches:
                    detected_issues.append({
                        "issue": issue_type,
                        "matches": len(matches),
                        "sample": matches[-1] if matches else "",
                    })

        return {
            "pod": pod_name,
            "namespace": namespace,
            "total_logs": len(messages),
            "detected_issues": detected_issues,
            "analysis_timestamp": datetime.utcnow().isoformat(),
        }

    async def analyze_failure(self, namespace: str, pod_name: str) -> dict:
        pod = await self.k8s.get_pod(namespace, pod_name)
        if not pod:
            return {"error": "Pod not found"}

        log_analysis = await self.analyze_pod_logs(namespace, pod_name)

        return {
            "pod": pod_name,
            "namespace": namespace,
            "status": pod.status,
            "restart_count": pod.restart_count,
            "phase": pod.phase,
            "log_analysis": log_analysis,
            "failure_signature": self._generate_signature(pod, log_analysis),
        }

    async def root_cause_analysis(self, namespace: str, pod_name: str) -> dict:
        analysis = await self.analyze_failure(namespace, pod_name)
        issues = analysis.get("log_analysis", {}).get("detected_issues", [])

        if not issues:
            return {
                "pod": pod_name,
                "root_cause": "No specific error patterns detected",
                "confidence": "low",
                "recommendation": "Examine full logs manually",
            }

        primary_issue = issues[0]["issue"]
        recommendations = {
            "OOMKilled": "Increase memory limits or optimize memory usage",
            "CrashLoopBackOff": "Check application code for unhandled exceptions",
            "ImagePullBackOff": "Verify image name and registry credentials",
            "CreateContainerConfigError": "Check ConfigMaps and Secrets references",
            "NodeLost": "Check node health and network connectivity",
            "DiskPressure": "Free up disk space or increase PV size",
            "NetworkError": "Check network policies and service endpoints",
        }

        return {
            "pod": pod_name,
            "root_cause": primary_issue,
            "details": issues,
            "confidence": "high" if len(issues) > 1 else "medium",
            "recommendation": recommendations.get(primary_issue, "Investigate logs"),
        }

    async def suggest_fix(self, namespace: str, pod_name: str) -> dict:
        rca = await self.root_cause_analysis(namespace, pod_name)

        fix_map = {
            "OOMKilled": {
                "action": "Increase memory resources",
                "command": "kubectl set resources pod/{pod} --limits=memory=512Mi",
                "automated": True,
            },
            "CrashLoopBackOff": {
                "action": "Delete pod to restart",
                "command": "kubectl delete pod {pod} -n {ns}",
                "automated": True,
            },
            "ImagePullBackOff": {
                "action": "Fix image reference",
                "command": "kubectl edit deployment/{deployment}",
                "automated": False,
            },
        }

        fix = fix_map.get(rca.get("root_cause"), {
            "action": "Manual investigation required",
            "command": "kubectl logs {pod} -n {ns} --previous",
            "automated": False,
        })

        return {
            "pod": pod_name,
            "root_cause": rca.get("root_cause"),
            "suggested_fix": fix["action"],
            "command": fix["command"].format(pod=pod_name, ns=namespace, deployment=pod_name),
            "can_auto_heal": fix["automated"],
        }

    def _generate_signature(self, pod, log_analysis: dict) -> str:
        issues = [i["issue"] for i in log_analysis.get("detected_issues", [])]
        return f"{pod.phase}_{pod.status}_{'_'.join(issues[:3])}"
