import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ---------- CONFIG ----------
# Sample enrichment using IPinfo (mock function)
def enrich_ip(ip):
    return {
        "company": "Acme Corp",
        "location": "San Francisco, CA",
        "industry": "Software",
        "employee_count": "201-500",
        "technologies": ["Salesforce", "Zendesk"]
    }

# Load data (replace with your own log file)
@st.cache_data
def load_data():
    data = pd.read_csv("sample_weblogs1.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data

# ---------- UI ----------
st.set_page_config(page_title="eGain Visitor Insights", layout="wide")
st.title("🔍 eGain Sales Intelligence Dashboard")

data = load_data()

# Sidebar filters
st.sidebar.header("Search Filters")
unique_ips = data["ip"].unique()
selected_ip = st.sidebar.selectbox("Select Visitor IP", ["All"] + list(unique_ips))
start_date = st.sidebar.date_input("Start Date", data["timestamp"].min().date())
end_date = st.sidebar.date_input("End Date", data["timestamp"].max().date())

# Text-based search bar
search_query = st.text_input("🔎 Search (company, state, vertical, pages viewed...)", "")

# Filter by date and IP
filtered = data[(data["timestamp"].dt.date >= start_date) & (data["timestamp"].dt.date <= end_date)]
if selected_ip != "All":
    filtered = filtered[filtered["ip"] == selected_ip]

# Filter by search query
if search_query:
    search_query_lower = search_query.lower()
    filtered = filtered[
        filtered["company_name"].str.lower().str.contains(search_query_lower)
        | filtered["state"].str.lower().str.contains(search_query_lower)
        | filtered["vertical"].str.lower().str.contains(search_query_lower)
        | filtered["total_pages_viewed"].astype(str).str.contains(search_query_lower)
    ]

# ---------- Summary Insights ----------
st.subheader("Summary Insights")
company_summary = []
for ip in filtered["ip"].unique():
    visits = filtered[filtered["ip"] == ip]
    company_summary.append({
        "Company": visits["company_name"].iloc[0],
        "State": visits["state"].iloc[0],
        "Vertical": visits["vertical"].iloc[0],
        "Sentiment": visits["sentiment"].iloc[0],
        "Intent": visits["intent"].iloc[0],
        "Sessions": visits["session_id"].nunique(),
        "Pages Viewed": len(visits),
        "Engagement Score": visits["engagement_score"].iloc[0],
        "Last Visit": visits["timestamp"].max().strftime("%Y-%m-%d %H:%M")
    })

summary_df = pd.DataFrame(company_summary).sort_values("Last Visit", ascending=False)

# Color-coding Engagement Score
def highlight_engagement(val):
    color = "blue"
    if val > 50:
        color = "red"
    elif val > 30:
        color = "green"
    return f"background-color: {color}; color: white"

styled_df = summary_df.style.applymap(highlight_engagement, subset=["Engagement Score"])
st.dataframe(styled_df.hide_index(), use_container_width=True)

# ---------- Visitor Sessions ----------
st.markdown("---")
st.subheader("Visitor Sessions")
session_groups = filtered.groupby("session_id")

for session_id, group in session_groups:
    visitor_ip = group["ip"].iloc[0]
    enrichment = enrich_ip(visitor_ip)

    with st.expander(f"Session {session_id} - {visitor_ip}"):
        st.write(f"**Company**: {group['company_name'].iloc[0]}")
        st.write(f"**Location**: {group['state'].iloc[0]}")
        st.write(f"**Vertical**: {group['vertical'].iloc[0]}")
        st.write(f"**Repeat Visits**: {group['repeat_visits'].iloc[0]}")
        st.write(f"**Pages Viewed**: {group['total_pages_viewed'].iloc[0]}")
        st.write(f"**Engagement Score**: {group['engagement_score'].iloc[0]}")
        st.write(f"**CRM Match**: {group['contact_match_in_crm'].iloc[0]}")

        st.markdown("**Page Visits:**")
        st.table(group[["timestamp", "url", "intent", "sentiment"]].sort_values("timestamp"))

st.markdown("\n---\n🔗 *Note: Data is demo-only. Replace with real weblogs + API enrichment for production.*")
