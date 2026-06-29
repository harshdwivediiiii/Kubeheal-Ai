import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="KubeHeal AI Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; margin-bottom: 0; }
    .sub-header { font-size: 1.2rem; color: #6c757d; margin-top: 0; }
    .metric-card { background-color: #f8f9fa; border-radius: 10px; padding: 20px; text-align: center; }
    .metric-value { font-size: 2rem; font-weight: 700; }
    .metric-label { font-size: 0.9rem; color: #6c757d; }
    .status-running { color: #28a745; font-weight: bold; }
    .status-failing { color: #dc3545; font-weight: bold; }
    .status-pending { color: #ffc107; font-weight: bold; }
</style>
""",
    unsafe_allow_html=True,
)


def generate_mock_pods(n: int = 20) -> pd.DataFrame:
    np.random.seed(42)
    statuses = ["Running", "Pending", "Failed", "CrashLoopBackOff", "Succeeded"]
    pods = []
    for i in range(n):
        status = np.random.choice(statuses, p=[0.6, 0.1, 0.1, 0.1, 0.1])
        restart_count = int(np.random.exponential(2))
        pods.append({
            "name": f"kubeheal-pod-{i}",
            "namespace": "default",
            "status": status,
            "restart_count": restart_count,
            "cpu_usage": round(np.random.uniform(10, 95), 1),
            "memory_usage": round(np.random.uniform(20, 90), 1),
            "age_hours": round(np.random.exponential(48), 1),
            "node": f"node-{np.random.randint(0, 3)}",
        })
    return pd.DataFrame(pods)


def generate_mock_metrics(hours: int = 24) -> pd.DataFrame:
    np.random.seed(42)
    timestamps = pd.date_range(
        end=datetime.now(), periods=hours * 4, freq="15min"
    )
    metrics = pd.DataFrame({
        "timestamp": timestamps,
        "cpu": 50 + 20 * np.sin(np.linspace(0, 4 * np.pi, len(timestamps))) + np.random.normal(0, 10, len(timestamps)),
        "memory": 60 + 15 * np.sin(np.linspace(0, 3 * np.pi, len(timestamps))) + np.random.normal(0, 8, len(timestamps)),
        "disk": 45 + np.random.normal(0, 5, len(timestamps)),
        "network_rx": 500 + 200 * np.sin(np.linspace(0, 6 * np.pi, len(timestamps))) + np.random.normal(0, 50, len(timestamps)),
        "network_tx": 300 + 150 * np.sin(np.linspace(0, 5 * np.pi, len(timestamps))) + np.random.normal(0, 30, len(timestamps)),
    })
    metrics[["cpu", "memory", "disk"]] = metrics[["cpu", "memory", "disk"]].clip(0, 100)
    metrics[["network_rx", "network_tx"]] = metrics[["network_rx", "network_tx"]].clip(0)
    return metrics


def main():
    st.markdown('<p class="main-header">🩺 KubeHeal AI Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Self-healing Kubernetes with AI-powered diagnostics</p>',
        unsafe_allow_html=True,
    )

    pods_df = generate_mock_pods(20)
    metrics_df = generate_mock_metrics(24)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", "📦 Pods", "⚠️ Alerts", "🔮 Predictions",
        "📝 Logs", "📈 Metrics", "🤖 AI Recommendations",
    ])

    with tab1:
        show_cluster_overview(pods_df)

    with tab2:
        show_pods(pods_df)

    with tab3:
        show_alerts()

    with tab4:
        show_predictions(pods_df)

    with tab5:
        show_log_explorer()

    with tab6:
        show_metrics(metrics_df)

    with tab7:
        show_ai_recommendations()


def show_cluster_overview(pods_df: pd.DataFrame):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Pods", len(pods_df), delta="+2 today")

    with col2:
        running = len(pods_df[pods_df["status"] == "Running"])
        st.metric("Running Pods", running, delta=f"{running - 10} baseline")

    with col3:
        failing = len(pods_df[pods_df["status"].isin(["Failed", "CrashLoopBackOff"])])
        st.metric("Failing Pods", failing, delta="⚠️", delta_color="inverse")

    with col4:
        avg_cpu = pods_df["cpu_usage"].mean()
        st.metric("Avg CPU", f"{avg_cpu:.1f}%", delta="3% above target")

    st.markdown("### 🖥️ Cluster Resources")
    col1, col2 = st.columns(2)

    with col1:
        status_counts = pods_df["status"].value_counts()
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            title="Pod Status Distribution",
            color_discrete_map={
                "Running": "#28a745",
                "Pending": "#ffc107",
                "Failed": "#dc3545",
                "CrashLoopBackOff": "#fd7e14",
                "Succeeded": "#17a2b8",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        node_stats = pods_df.groupby("node").agg(
            pod_count=("name", "count"),
            avg_cpu=("cpu_usage", "mean"),
            avg_memory=("memory_usage", "mean"),
        ).reset_index()
        fig = px.bar(
            node_stats,
            x="node",
            y=["avg_cpu", "avg_memory"],
            title="Per-Node Resource Usage",
            barmode="group",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### ⏱️ Recent Events")
    events = pd.DataFrame({
        "time": pd.date_range(end=datetime.now(), periods=10, freq="5min"),
        "pod": [f"kubeheal-pod-{i}" for i in range(10)],
        "event": np.random.choice(
            ["PodStarted", "PodKilling", "BackOff", "Unhealthy", "Pulled"],
            10,
        ),
        "reason": np.random.choice(
            ["Started container", "Container killed", "Back-off restarting",
             "Readiness probe failed", "Successfully pulled image"],
            10,
        ),
    })
    st.dataframe(events, use_container_width=True)


def show_pods(pods_df: pd.DataFrame):
    st.markdown("### 📦 All Pods")

    status_filter = st.multiselect(
        "Filter by status",
        options=pods_df["status"].unique(),
        default=pods_df["status"].unique(),
    )

    filtered = pods_df[pods_df["status"].isin(status_filter)]
    st.dataframe(filtered, use_container_width=True)

    st.markdown("### ⚠️ Failing Pods")
    failing = pods_df[pods_df["status"].isin(["Failed", "CrashLoopBackOff"])]
    if len(failing) > 0:
        for _, pod in failing.iterrows():
            with st.expander(f"🔴 {pod['name']} - {pod['status']}"):
                st.write(f"**Restart Count:** {pod['restart_count']}")
                st.write(f"**CPU Usage:** {pod['cpu_usage']}%")
                st.write(f"**Memory Usage:** {pod['memory_usage']}%")
                st.write(f"**Node:** {pod['node']}")
                if st.button(f"🔄 Auto-Heal {pod['name']}", key=f"heal_{pod['name']}"):
                    st.success(f"✅ Initiated recovery for {pod['name']}")
    else:
        st.success("✅ No failing pods detected")


def show_alerts():
    st.markdown("### 🚨 Active Alerts")

    alerts = pd.DataFrame({
        "severity": np.random.choice(["critical", "warning", "info"], 10, p=[0.3, 0.5, 0.2]),
        "title": [
            "High CPU Usage", "Pod CrashLoopBackOff", "Memory Pressure",
            "Node NotReady", "OOMKilled", "High Restart Count",
            "Disk Pressure", "Network Errors", "Image Pull Failure",
            "Readiness Probe Failed",
        ],
        "pod": [f"kubeheal-pod-{i}" for i in range(10)],
        "status": np.random.choice(["active", "acknowledged", "resolved"], 10, p=[0.5, 0.3, 0.2]),
        "time": pd.date_range(end=datetime.now(), periods=10, freq="1h"),
    })

    severity_colors = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
    for _, alert in alerts.iterrows():
        color = severity_colors.get(alert["severity"], "⚪")
        st.markdown(
            f"{color} **[{alert['severity'].upper()}]** {alert['title']} "
            f"- {alert['pod']} ({alert['status']})"
        )


def show_predictions(pods_df: pd.DataFrame):
    st.markdown("### 🔮 Failure Predictions")

    pods_df["failure_prob"] = 1 / (1 + np.exp(-(pods_df["restart_count"] - 2)))
    pods_df["prediction"] = np.where(pods_df["failure_prob"] > 0.5, "⚠️ Likely to Fail", "✅ Stable")

    fig = px.scatter(
        pods_df,
        x="cpu_usage",
        y="memory_usage",
        size="failure_prob",
        color="prediction",
        hover_data=["name", "restart_count", "failure_prob"],
        title="Pod Failure Risk Assessment",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### High-Risk Pods")
    high_risk = pods_df[pods_df["failure_prob"] > 0.5].sort_values("failure_prob", ascending=False)
    if len(high_risk) > 0:
        st.dataframe(high_risk, use_container_width=True)
    else:
        st.success("No high-risk pods detected")


def show_log_explorer():
    st.markdown("### 📝 Log Explorer")

    col1, col2 = st.columns(2)
    with col1:
        namespace = st.selectbox("Namespace", ["default", "kube-system", "monitoring"])
    with col2:
        pod = st.text_input("Pod Name", "kubeheal-pod-0")

    levels = st.multiselect("Log Level", ["INFO", "WARN", "ERROR", "FATAL"], default=["ERROR", "FATAL"])

    log_lines = [
        f"2024-01-01 10:00:{str(i).zfill(2)} {lvl} {msg}"
        for i, (lvl, msg) in enumerate(
            zip(
                np.random.choice(["INFO", "WARN", "ERROR", "FATAL"], 50, p=[0.6, 0.2, 0.15, 0.05]),
                np.random.choice(
                    [
                        "Container started successfully",
                        "Health check passed",
                        "Connection timeout to backend",
                        "OOMKilled - Memory limit exceeded",
                        "CrashLoopBackOff - Back-off restarting",
                        "Readiness probe failed",
                        "Image pull failed: not found",
                        "Failed to mount volume",
                    ],
                    50,
                ),
            )
        )
    ]

    st.text_area("Log Output", "\n".join(log_lines), height=300)

    if st.button("🔍 Analyze Logs"):
        st.info("Analyzing logs for failure patterns...")
        st.success("Detected: CrashLoopBackOff pattern")


def show_metrics(metrics_df: pd.DataFrame):
    st.markdown("### 📈 Prometheus Metrics")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            px.line(metrics_df, x="timestamp", y="cpu", title="CPU Usage (%)"),
            use_container_width=True,
        )
    with col2:
        st.plotly_chart(
            px.line(metrics_df, x="timestamp", y="memory", title="Memory Usage (%)"),
            use_container_width=True,
        )

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            px.line(metrics_df, x="timestamp", y="disk", title="Disk Usage (%)"),
            use_container_width=True,
        )
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=metrics_df["timestamp"], y=metrics_df["network_rx"],
            name="RX", line=dict(color="blue"),
        ))
        fig.add_trace(go.Scatter(
            x=metrics_df["timestamp"], y=metrics_df["network_tx"],
            name="TX", line=dict(color="red"),
        ))
        fig.update_layout(title="Network Traffic (MB/s)")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("📊 Prometheus Query"):
        query = st.text_input("PromQL Query", 'rate(container_cpu_usage_seconds_total[5m])')
        if st.button("Execute Query"):
            st.json({"status": "success", "data": {"result": []}})


def show_ai_recommendations():
    st.markdown("### 🤖 AI-Generated Recommendations")

    recommendations = [
        {
            "pod": "kubeheal-pod-3",
            "issue": "CrashLoopBackOff",
            "root_cause": "Application exiting with code 137 (OOMKilled)",
            "recommendation": "Increase memory limit from 256Mi to 512Mi",
            "auto_fix": True,
        },
        {
            "pod": "kubeheal-pod-7",
            "issue": "High Restart Count (12)",
            "root_cause": "Readiness probe failing - application not ready within 30s",
            "recommendation": "Increase initialDelaySeconds to 60 or fix app startup time",
            "auto_fix": False,
        },
        {
            "pod": "kubeheal-pod-12",
            "issue": "ImagePullBackOff",
            "root_cause": "Container image 'kubeheal-app:latest' not found",
            "recommendation": "Build and push image or update image tag",
            "auto_fix": True,
        },
    ]

    for rec in recommendations:
        with st.expander(f"🔴 {rec['pod']} - {rec['issue']}"):
            st.markdown(f"**Root Cause:** {rec['root_cause']}")
            st.markdown(f"**Recommendation:** {rec['recommendation']}")
            if rec["auto_fix"]:
                if st.button(f"🔄 Auto-Fix {rec['pod']}", key=f"fix_{rec['pod']}"):
                    st.success(f"✅ Applied fix for {rec['pod']}")
            else:
                st.warning("Manual intervention required")


if __name__ == "__main__":
    main()
