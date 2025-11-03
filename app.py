import streamlit as st
import pandas as pd
import re
import math
import plotly.express as px
from markupsafe import Markup

st.set_page_config(page_title="DOGE Grants Viewer", layout="wide")

# ✅ Simple and stable refresh button
if st.button("🔄 Refresh Data"):
    st.rerun()

# --- Clean illegal characters ---
def clean_text(value):
    if isinstance(value, str):
        return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", value)
    return value

# --- Load data ---
@st.cache_data
def load_data():
    xls = pd.ExcelFile("doge_full_download.xlsx")
    grants = pd.read_excel(xls, "Grants")
    grants = grants.apply(lambda col: col.map(clean_text) if col.dtype == "object" else col)
    grants["date_parsed"] = pd.to_datetime(grants["date"], errors="coerce")
    grants["year"] = grants["date_parsed"].dt.year
    return grants

grants_df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Grants")

agency_options = sorted(grants_df["agency"].dropna().unique())
selected_agency = st.sidebar.selectbox("Select Agency", ["All"] + agency_options)

recipient_input = st.sidebar.text_input("Search Recipient Name").strip().lower()
description_input = st.sidebar.text_input("Keyword in Description").strip().lower()

sort_option = st.sidebar.selectbox("Sort Results By", [
    "Date (Newest → Oldest)",
    "Value (High → Low)",
    "Savings (High → Low)",
    "Recipient (A → Z)"
])

# --- Filtering Logic ---
filtered_df = grants_df.copy()

if selected_agency != "All":
    filtered_df = filtered_df[filtered_df["agency"] == selected_agency]

if recipient_input:
    filtered_df = filtered_df[filtered_df["recipient"].str.lower().str.contains(recipient_input, na=False)]

if description_input:
    filtered_df = filtered_df[filtered_df["description"].str.lower().str.contains(description_input, na=False)]

# --- Sorting ---
if sort_option == "Value (High → Low)":
    filtered_df = filtered_df.sort_values(by="value", ascending=False)
elif sort_option == "Savings (High → Low)":
    filtered_df = filtered_df.sort_values(by="savings", ascending=False)
elif sort_option == "Date (Newest → Oldest)":
    filtered_df = filtered_df.sort_values(by="date_parsed", ascending=False)
elif sort_option == "Recipient (A → Z)":
    filtered_df = filtered_df.sort_values(by="recipient", ascending=True)

# --- Format columns ---
filtered_df["value_display"] = filtered_df["value"].apply(lambda x: f"${x:,.0f}")
filtered_df["savings_display"] = filtered_df["savings"].apply(lambda x: f"${x:,.0f}")
filtered_df["date_display"] = filtered_df["date_parsed"].dt.strftime("%Y-%m-%d")

# --- Charts ---
st.subheader("📊 Top Agencies by Total Value")
if not filtered_df.empty:
    top_agencies = (
        filtered_df.groupby("agency")["value"]
        .sum()
        .reset_index()
        .sort_values(by="value", ascending=False)
        .head(10)
    )
    fig1 = px.bar(
        top_agencies,
        x="agency",
        y="value",
        labels={"value": "Total Value ($)", "agency": "Agency"},
        title="Top Agencies by Total Value",
        hover_data={"value": ":,.0f"},
    )
    fig1.update_layout(
        xaxis_tickangle=-45,
        yaxis_tickformat="$,.0f",
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(l=40, r=40, t=40, b=80),
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("📊 Top Recipients by Total Value")
    top_recipients = (
        filtered_df.groupby("recipient")["value"]
        .sum()
        .reset_index()
        .sort_values(by="value", ascending=False)
        .head(10)
    )
    fig2 = px.bar(
        top_recipients,
        x="recipient",
        y="value",
        labels={"value": "Total Value ($)", "recipient": "Recipient"},
        title="Top Recipients by Total Value",
        hover_data={"value": ":,.0f"},
    )
    fig2.update_layout(
        xaxis_tickangle=-45,
        yaxis_tickformat="$,.0f",
        hoverlabel=dict(bgcolor="white", font_size=12),
        margin=dict(l=40, r=40, t=40, b=80),
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No results to chart.")

# --- Total Value ---
total_value = filtered_df["value"].sum()
st.markdown(f"### 💰 Total Value of Filtered Grants: **${total_value:,.0f}**")

# --- Paginated Results ---
st.subheader("📄 Filtered Results")
results_per_page = 100
total_results = len(filtered_df)
total_pages = math.ceil(total_results / results_per_page)

if total_results == 0:
    st.warning("No matching results.")
else:
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start_idx = (page - 1) * results_per_page
    end_idx = start_idx + results_per_page
    page_df = filtered_df.iloc[start_idx:end_idx]

    for _, row in page_df.iterrows():
        expander_title = f"📄 {row['recipient']} — {row['agency']} — {row['date_display']} — {row['value_display']}"
        with st.expander(expander_title):
            st.markdown(f"**Amount:** {row.get('value_display', '')}")
            st.markdown(f"**Savings:** {row.get('savings_display', '')}")
            st.markdown(f"**Link:** [View Award]({row.get('link', '')})")
            st.markdown("**Description:**")
            description_text = row.get("description", "No description available.")
            if description_input:
                pattern = re.compile(re.escape(description_input), re.IGNORECASE)
                description_text = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", description_text)
            st.markdown(description_text, unsafe_allow_html=True)

    st.caption(f"Showing {len(page_df)} of {total_results} results")

# --- Download ---
st.download_button(
    label="Download Filtered Results as CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_grants.csv",
    mime="text/csv"
)
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
# touch app.py to trigger Streamlit redeploy
