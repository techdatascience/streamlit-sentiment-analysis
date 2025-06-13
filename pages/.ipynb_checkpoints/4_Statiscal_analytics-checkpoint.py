import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.markdown("""
<style>
h1, h2, h3 {
    color: #00b4d8 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("📈 Statistical Analytics Overview")

if 'df' not in st.session_state:
    st.warning("⚠️ Please upload and process data first on the 'Get your Data Insights' page.")
else:
    df = st.session_state['df'].copy()

    st.markdown("### 🔍 Select insights you'd like to view:")

    options = st.multiselect(
        "Choose metrics to display:",
        ["Unique Diseases", "Count of Each Disease", "Number of Counties", "Number of Weeks"]
    )

    if "Unique Diseases" in options:
        if 'Disease' in df.columns:
            unique_diseases = df['Disease'].dropna().unique()
            st.markdown(f"#### 🧬 Unique Diseases Found: `{len(unique_diseases)}`")
            st.write(sorted(unique_diseases.tolist()))
        else:
            st.warning("❌ 'Disease' column not found in dataset.")

    if "Count of Each Disease" in options:
        if 'Disease' in df.columns:
            disease_counts = df['Disease'].value_counts().reset_index()
            disease_counts.columns = ['Disease', 'Count']
            st.markdown("#### 🧪 Disease Occurrence Counts")
            st.dataframe(disease_counts)
        else:
            st.warning("❌ 'Disease' column not found in dataset.")

    if "Number of Counties" in options:
        if 'county_name' in df.columns:
            county_count = df['county_name'].nunique()
            st.markdown(f"#### 🏙️ Total Counties Present: `{county_count}`")
        else:
            st.warning("❌ 'county_name' column not found in dataset.")

    if "Number of Weeks" in options:
        if 'MMWR_WEEK' in df.columns:
            week_count = df['MMWR_WEEK'].nunique()
            st.markdown(f"#### 🗓️ Total Weeks Captured: `{week_count}`")
        else:
            st.warning("❌ 'MMWR_WEEK' column not found in dataset.")
