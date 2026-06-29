from locust import HttpUser, task, between


class KubeHealUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def health_check(self):
        self.client.get("/health")

    @task(1)
    def list_pods(self):
        self.client.get("/pods/")

    @task(1)
    def list_alerts(self):
        self.client.get("/alerts/")

    @task(1)
    def get_alert_rules(self):
        self.client.get("/alerts/rules")

    @task(1)
    def get_cluster_metrics(self):
        self.client.get("/metrics/cluster")
