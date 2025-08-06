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
    #data = pd.read_csv("sample_weblogs.csv")
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data

# ---------- UI ----------
st.set_page_config(page_title="eGain Visitor Insights", layout="wide")
st.title("🔍 eGain Sales Intelligence Dashboard")

st.sidebar.header("Search Filters")
data = load_data()

# Unique IPs (simulate companies)
unique_ips = data["ip"].unique()
selected_ip = st.sidebar.selectbox("Select Visitor IP", ["All"] + list(unique_ips))

# Date filter
start_date = st.sidebar.date_input("Start Date", data["timestamp"].min().date())
end_date = st.sidebar.date_input("End Date", data["timestamp"].max().date())

# Filter logic
filtered = data[(data["timestamp"].dt.date >= start_date) & (data["timestamp"].dt.date <= end_date)]
if selected_ip != "All":
    filtered = filtered[filtered["ip"] == selected_ip]

# Show insights
st.subheader("Visitor Sessions")
session_groups = filtered.groupby("session_id")

for session_id, group in session_groups:
    visitor_ip = group["ip"].iloc[0]
    enrichment = enrich_ip(visitor_ip)

    with st.expander(f"Session {session_id} - {visitor_ip}"):
        st.write(f"**Company**: {enrichment['company']}")
        st.write(f"**Location**: {enrichment['location']}")
        st.write(f"**Industry**: {enrichment['industry']}")
        st.write(f"**Employees**: {enrichment['employee_count']}")
        st.write(f"**Technologies**: {', '.join(enrichment['technologies'])}")

        st.markdown("**Page Visits:**")
        st.table(group[["timestamp", "url"]].sort_values("timestamp"))

# ---------- Summary ----------
st.markdown("---")
st.subheader("Summary Insights")
company_summary = []
for ip in data["ip"].unique():
    visits = data[data["ip"] == ip]
    enrichment = enrich_ip(ip)
    company_summary.append({
        "Company": enrichment["company"],
        "IP": ip,
        "Sessions": visits["session_id"].nunique(),
        "Pages Viewed": len(visits),
        "Last Visit": visits["timestamp"].max().strftime("%Y-%m-%d %H:%M")
    })

summary_df = pd.DataFrame(company_summary).sort_values("Last Visit", ascending=False)
st.dataframe(summary_df, use_container_width=True)

st.markdown("\n---\n🔗 *Note: Data is demo-only. Replace with real weblogs + API enrichment for production.*")
