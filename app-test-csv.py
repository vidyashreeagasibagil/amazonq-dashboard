import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# Login सिस्टम
# -----------------------------
# def login():
#     st.title("🔐 Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):
#         if username == "admin" and password == "admin123":
#             st.session_state["logged_in"] = True
#         else:
#             st.error("Invalid credentials")

# Session init
# if "logged_in" not in st.session_state:
#     st.session_state["logged_in"] = False

# if not st.session_state["logged_in"]:
#     login()
#     st.stop()



# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(page_title="Amazon Q Dashboard", layout="wide")

# Auto refresh (2 min)
st_autorefresh(interval=120000, key="refresh")

# Title
st.markdown("""
<h1 style='text-align: center; color: #4CAF50;'>
🚀 Amazon Q Developer Usage Dashboard
</h1>
""", unsafe_allow_html=True)

# -----------------------------
# Load CSV Data
# -----------------------------
df = pd.read_csv("amazonq_usage.csv")

# Convert date
df["date"] = pd.to_datetime(df["date"])

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("Filters")

# Team filter
selected_team = st.sidebar.multiselect(
    "Select Team",
    options=sorted(df["team"].dropna().unique()),
    default=sorted(df["team"].dropna().unique())
)

filtered_team_df = df[df["team"].isin(selected_team)]

# Date filter
min_date = df["date"].min()
max_date = df["date"].max()

selected_date = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

filtered_team_df = filtered_team_df[
    (filtered_team_df["date"] >= pd.to_datetime(selected_date[0])) &
    (filtered_team_df["date"] <= pd.to_datetime(selected_date[1]))
]

# User filter (dependent)
selected_user = st.sidebar.multiselect(
    "Select User",
    options=sorted(filtered_team_df["user"].dropna().unique()),
    default=sorted(filtered_team_df["user"].dropna().unique())
)

filtered_df = filtered_team_df[
    filtered_team_df["user"].isin(selected_user)
]

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2, col3 = st.columns(3)

total_queries = int(filtered_df["queries"].sum())
total_users = filtered_df["user"].nunique()
total_teams = filtered_df["team"].nunique()

col1.markdown(f"""
<div style="background-color:#1f77b4;padding:20px;border-radius:12px;text-align:center;color:white">
<h4>Total Queries</h4>
<h2>{total_queries}</h2>
</div>
""", unsafe_allow_html=True)

col2.markdown(f"""
<div style="background-color:#2ca02c;padding:20px;border-radius:12px;text-align:center;color:white">
<h4>Total Users</h4>
<h2>{total_users}</h2>
</div>
""", unsafe_allow_html=True)

col3.markdown(f"""
<div style="background-color:#ff7f0e;padding:20px;border-radius:12px;text-align:center;color:white">
<h4>Total Teams</h4>
<h2>{total_teams}</h2>
</div>
""", unsafe_allow_html=True)

st.divider()

# -----------------------------
# Charts
# -----------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("👤 Usage by Developer")
    user_data = filtered_df.groupby("user")["queries"].sum()
    st.bar_chart(user_data)

with col_right:
    st.subheader("👥 Usage by Team")
    team_data = filtered_df.groupby("team")["queries"].sum()
    st.bar_chart(team_data)

st.divider()

# Feature Usage
st.subheader("⚙️ Feature Usage")
feature_data = filtered_df.groupby("feature")["queries"].sum()

fig, ax = plt.subplots()
ax.pie(feature_data, labels=feature_data.index, autopct='%1.1f%%')
st.pyplot(fig)

# Daily Trend
st.subheader("📈 Daily Usage Trend")
date_data = filtered_df.groupby("date")["queries"].sum()
st.line_chart(date_data)

st.divider()

# -----------------------------
# Leaderboard
# -----------------------------
st.subheader("🏆 Top Amazon Q Users")

top_users = (
    filtered_df.groupby("user")["queries"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

st.dataframe(top_users)

st.divider()

# -----------------------------
# Download Button
# -----------------------------
st.subheader("⬇️ Download Data")

csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download as CSV",
    data=csv,
    file_name="amazonq_usage_report.csv",
    mime="text/csv",
)

# -----------------------------
# Raw Data
# -----------------------------
with st.expander("🔍 View Raw Data"):
    st.dataframe(filtered_df)
