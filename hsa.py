import streamlit as st

st.set_page_config(page_title = "Sentiment Analysis App", layout = "wide")

st.title("📊 Sentiment Analysis App")
st.subheader("Upload → Analyze → Dashboard")

st.markdown("""
Welcome! This app helps you analyze sentiment using **SentiWordNet**.
- Start by uploading a CSV file containing a `Description` column.
- Go to the **"Upload and Analyze"** page to process your data.
- Then explore interactive visualizations in the **Dashboard** tab.

Use the sidebar to navigate between pages.
""")
