import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Amazon Q Dashboard", layout="wide")
st_autorefresh(interval=120000, key="refresh")

# -----------------------------
# GLOBAL CSS (ONLY SAFE STYLING)
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}

/* KPI Cards */
.kpi-card {
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-radius: 12px;
    padding: 15px;
    color: white;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
}

.kpi-title {
    font-size: 14px;
}

.kpi-value {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# TITLE
# -----------------------------
st.markdown("<h1 style='text-align:center;color:#4CAF50;'>🚀 Amazon Q Developer Dashboard</h1>", unsafe_allow_html=True)
st.caption("📊 Time = Hours | % = Efficiency | Count = Volume")

# -----------------------------
# LOAD DATA
# -----------------------------
df = pd.read_csv("amazonq_usage.csv")
prod_df = pd.read_csv("productivity_data.csv")

df = pd.merge(df, prod_df, on="user", how="left")
df["date"] = pd.to_datetime(df["date"])

# -----------------------------
# CALCULATIONS
# -----------------------------
baseline_time = 50
df["time_saved"] = baseline_time - df["pr_time_hours"]
df["improvement"] = (df["time_saved"] / baseline_time) * 100
df["pr_success_rate"] = (df["pr_merged"] / df["pr_created"]) * 100

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.header("Filters")

teams = st.sidebar.multiselect("Team", df["team"].unique(), default=df["team"].unique())
filtered = df[df["team"].isin(teams)]

date_range = st.sidebar.date_input("Date Range", [df["date"].min(), df["date"].max()])
filtered = filtered[
    (filtered["date"] >= pd.to_datetime(date_range[0])) &
    (filtered["date"] <= pd.to_datetime(date_range[1]))
]

users = st.sidebar.multiselect("User", filtered["user"].unique(), default=filtered["user"].unique())
filtered = filtered[filtered["user"].isin(users)]

# -----------------------------
# KPI SECTION
# -----------------------------
col1, col2, col3 = st.columns(3, gap="large")

col1.markdown(f"""
<div class="kpi-card" style="background:linear-gradient(#4CAF50,#2E7D32)">
<div class="kpi-title">Total Queries</div>
<div class="kpi-value">{int(filtered["queries"].sum())}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card" style="background:linear-gradient(#2196F3,#1565C0)">
<div class="kpi-title">Total Users</div>
<div class="kpi-value">{filtered["user"].nunique()}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card" style="background:linear-gradient(#FF9800,#EF6C00)">
<div class="kpi-title">Total Teams</div>
<div class="kpi-value">{filtered["team"].nunique()}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# USAGE SECTION
# -----------------------------
st.markdown("## 📊 Usage Insights")

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("👤 Usage by Developer")
    st.caption("Queries per developer")
    st.bar_chart(filtered.groupby("user")["queries"].sum(), use_container_width=True)

with col2:
    st.subheader("👥 Usage by Team")
    st.caption("Queries by team")
    st.bar_chart(filtered.groupby("team")["queries"].sum(), use_container_width=True)

col3, col4 = st.columns(2, gap="large")

with col3:
    st.subheader("⚙️ Feature Usage")
    st.caption("Query distribution")
    feature = filtered.groupby("feature")["queries"].sum()
    fig, ax = plt.subplots()
    ax.pie(feature, labels=feature.index, autopct='%1.1f%%')
    st.pyplot(fig)

with col4:
    st.subheader("📈 Daily Trend")
    st.caption("Queries over time")
    st.line_chart(filtered.groupby("date")["queries"].sum(), use_container_width=True)

st.markdown("---")

# -----------------------------
# PRODUCTIVITY KPIs
# -----------------------------
st.markdown("## 🚀 Productivity Insights")

col1, col2, col3, col4 = st.columns(4, gap="large")

col1.markdown(f"""
<div class="kpi-card" style="background:linear-gradient(#9C27B0,#6A1B9A)">
<div class="kpi-title">Time Saved</div>
<div class="kpi-value">{round(filtered["time_saved"].sum(),2)}</div>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div class="kpi-card" style="background:linear-gradient(#00BCD4,#00838F)">
<div class="kpi-title">Productivity %</div>
<div class="kpi-value">{round(filtered["improvement"].mean(),2)}</div>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div class="kpi-card" style="background:linear-gradient(#8BC34A,#558B2F)">
<div class="kpi-title">Commits</div>
<div class="kpi-value">{int(filtered["commits"].sum())}</div>
</div>
""", unsafe_allow_html=True)

col4.markdown(f"""
<div class="kpi-card" style="background:linear-gradient(#FF5722,#BF360C)">
<div class="kpi-title">PR Success %</div>
<div class="kpi-value">{round(filtered["pr_success_rate"].mean(),2)}</div>
</div>
""", unsafe_allow_html=True)


st.markdown("---")


# -----------------------------
# PRODUCTIVITY CHARTS
# -----------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📈 Productivity by Developer")
    st.caption("Efficiency improvement (%)")
    st.bar_chart(filtered.groupby("user")["improvement"].mean(), use_container_width=True)

with col2:
    st.subheader("⏱️ Time Saved by Team")
    st.caption("Hours saved")
    st.bar_chart(filtered.groupby("team")["time_saved"].sum(), use_container_width=True)

col3, col4 = st.columns(2, gap="large")

with col3:
    st.subheader("📊 Before vs After")
    st.caption("Development time comparison (Hours)")

    comp = filtered[["user","pr_time_hours"]].drop_duplicates()

    comp["Before"] = 50
    comp["After"] = comp["pr_time_hours"]

    comp = comp.set_index("user")[["Before","After"]]
    comp.columns = ["Before (Hours)", "After (Hours)"]

    st.bar_chart(comp, use_container_width=True)


with col4:
    st.subheader("🔗 Usage vs Productivity")
    st.caption("Queries vs time saved")
    st.line_chart(
        filtered.groupby("user")[["queries","time_saved"]].sum(),
        use_container_width=True
    )

st.markdown("---")

# -----------------------------
# SUMMARY
# -----------------------------
st.subheader("📋 Summary")
st.dataframe(filtered)

# -----------------------------
# DOWNLOAD
# -----------------------------
st.download_button("⬇️ Download", filtered.to_csv(index=False), "report.csv")


