import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Amazon Q Dashboard", layout="wide")
st_autorefresh(interval=120000, key="refresh")

st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>
🚀 Amazon Q Developer Usage Dashboard
</h1>
""", unsafe_allow_html=True)

st.caption("📊 All time values are in hours, percentages represent efficiency improvement, and counts represent number of queries.")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("amazonq_usage.csv")
prod_df = pd.read_csv("productivity_data.csv")

df = pd.merge(df, prod_df, on="user", how="left")
df["date"] = pd.to_datetime(df["date"])

# -----------------------------
# PRODUCTIVITY CALCULATIONS
# -----------------------------
baseline_time = 50

df["time_saved"] = baseline_time - df["pr_time_hours"]
df["improvement"] = (df["time_saved"] / baseline_time) * 100
df["pr_success_rate"] = (df["pr_merged"] / df["pr_created"]) * 100

# -----------------------------
# SIDEBAR FILTERS
# -----------------------------
st.sidebar.header("Filters")

selected_team = st.sidebar.multiselect(
    "Select Team",
    options=sorted(df["team"].unique()),
    default=sorted(df["team"].unique())
)

filtered_team_df = df[df["team"].isin(selected_team)]

selected_date = st.sidebar.date_input(
    "Select Date Range",
    [df["date"].min(), df["date"].max()]
)

filtered_team_df = filtered_team_df[
    (filtered_team_df["date"] >= pd.to_datetime(selected_date[0])) &
    (filtered_team_df["date"] <= pd.to_datetime(selected_date[1]))
]

selected_user = st.sidebar.multiselect(
    "Select User",
    options=sorted(filtered_team_df["user"].unique()),
    default=sorted(filtered_team_df["user"].unique())
)

filtered_df = filtered_team_df[
    filtered_team_df["user"].isin(selected_user)
]

# -----------------------------
# KPI CARDS
# -----------------------------
col1, col2, col3 = st.columns(3)

col1.markdown(f"""
<div style="background-color:#1f77b4;padding:20px;border-radius:12px;text-align:center;color:white">
<h4>Total Queries (Count)</h4>
<h2>{int(filtered_df["queries"].sum())}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="background-color:#2ca02c;padding:20px;border-radius:12px;text-align:center;color:white">
<h4>Total Users (Count)</h4>
<h2>{filtered_df["user"].nunique()}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style="background-color:#ff7f0e;padding:20px;border-radius:12px;text-align:center;color:white">
<h4>Total Teams (Count)</h4>
<h2>{filtered_df["team"].nunique()}</h2>
</div>
""", unsafe_allow_html=True)

st.divider()

# -----------------------------
# USAGE CHARTS
# -----------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("👤 Usage by Developer (Queries Count)")
    st.caption("Number of Amazon Q queries per developer")
    st.bar_chart(filtered_df.groupby("user")["queries"].sum())

with col_right:
    st.subheader("👥 Usage by Team (Queries Count)")
    st.caption("Total queries aggregated by team")
    st.bar_chart(filtered_df.groupby("team")["queries"].sum())

st.divider()

st.subheader("⚙️ Feature Usage (Queries Count)")
feature_data = filtered_df.groupby("feature")["queries"].sum()

fig, ax = plt.subplots()
ax.pie(feature_data, labels=feature_data.index, autopct='%1.1f%%')
st.pyplot(fig)

st.subheader("📈 Daily Usage Trend (Queries per Day)")
st.line_chart(filtered_df.groupby("date")["queries"].sum())

st.divider()

# -----------------------------
# LEADERBOARD
# -----------------------------
st.subheader("🏆 Top Amazon Q Users")
st.dataframe(
    filtered_df.groupby("user")["queries"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.divider()

# -----------------------------
# DOWNLOAD
# -----------------------------
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Data",
    csv,
    "amazonq_report.csv",
    "text/csv"
)

# =============================
# 🚀 PRODUCTIVITY INSIGHTS
# =============================
st.divider()
st.markdown("## 🚀 Engineering Productivity Insights")

col1, col2, col3, col4 = st.columns(4)

col1.metric("⏱️ Time Saved (Hours)", round(filtered_df["time_saved"].sum(), 2))
col2.metric("📈 Productivity Gain (%)", round(filtered_df["improvement"].mean(), 2))
col3.metric("💻 Total Commits (Count)", int(filtered_df["commits"].sum()))
col4.metric("✅ PR Success Rate (%)", round(filtered_df["pr_success_rate"].mean(), 2))

# Charts
st.subheader("📈 Productivity Improvement by Developer (%)")
st.bar_chart(filtered_df.groupby("user")["improvement"].mean())

st.subheader("⏱️ Time Saved by Team (Hours)")
st.bar_chart(filtered_df.groupby("team")["time_saved"].sum())

# Before vs After
st.subheader("📊 Before vs After Development Time (Hours)")
comparison = filtered_df[[
    "user", "pr_time_hours"
]].drop_duplicates()

comparison["Before (Hours)"] = 50
comparison["After (Hours)"] = comparison["pr_time_hours"]

comparison = comparison.set_index("user")[["Before (Hours)", "After (Hours)"]]

st.bar_chart(comparison)

# Correlation
st.subheader("🔗 Amazon Q Usage vs Productivity")
st.scatter_chart(
    filtered_df.groupby("user")[["queries", "time_saved"]].sum()
)

# Summary Table
st.subheader("📋 Developer Productivity Summary")

summary = filtered_df[[
    "user", "team", "queries", "commits",
    "pr_created", "pr_merged",
    "pr_time_hours", "time_saved",
    "improvement", "pr_success_rate"
]].drop_duplicates()

summary = summary.rename(columns={
    "queries": "Queries (Count)",
    "commits": "Commits (Count)",
    "pr_time_hours": "PR Time (Hours)",
    "time_saved": "Time Saved (Hours)",
    "improvement": "Improvement (%)",
    "pr_success_rate": "PR Success Rate (%)"
})

st.dataframe(summary)

# =============================
# 🔗 GITHUB INTEGRATION
# =============================

st.divider()
st.markdown("## 🔗 GitHub Activity (Live Data)")

GITHUB_TOKEN = "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"
OWNER = "vidyashreeagasibagil"

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

def get_repos():
    url = "https://api.github.com/user/repos"
    return requests.get(url, headers=headers).json()

def get_total_commits():
    total = 0
    for repo in get_repos():
        r = requests.get(repo["url"] + "/commits", headers=headers)
        if r.status_code == 200:
            total += len(r.json())
    return total

def get_total_prs():
    total = 0
    for repo in get_repos():
        r = requests.get(repo["url"] + "/pulls?state=all", headers=headers)
        if r.status_code == 200:
            total += len(r.json())
    return total

col1, col2 = st.columns(2)

col1.metric("💻 GitHub Commits (All Repos)", get_total_commits())
col2.metric("🔀 Pull Requests (All Repos)", get_total_prs())

# -----------------------------
# RAW DATA
# -----------------------------
with st.expander("🔍 View Raw Data"):
    st.dataframe(filtered_df)
