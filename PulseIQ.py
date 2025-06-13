import streamlit as st
from streamlit_lottie import st_lottie
import requests

st.set_page_config(page_title="PulseIQ", layout="wide")

# ---- Load Lottie Animation ----
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_ai = load_lottie_url("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")  # AI assistant animation

# ---- CSS Styling ----
st.markdown("""
<style>
.subheading {
    color: #0077b6;
    font-size: 22px;
    font-weight: 600;
    margin-top: -10px;
}
.description-box {
    background-color: #f0f8ff;
    padding: 20px;
    border-radius: 10px;
    font-size: 17px;
    color: #000;
    border-left: 6px solid #00b4d8;
    margin-top: 20px;
}
@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.7; }
    100% { opacity: 1; }
}
</style>
""", unsafe_allow_html=True)

# ---- Layout with Columns ----
col1, col2 = st.columns([1, 2])

with col1:
    st_lottie(lottie_ai, height=250, key="ai_intro")

with col2:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px;'>
        <img src='https://cdn-icons-png.flaticon.com/512/1828/1828884.png' alt='icon' width='40'/>
        <h1 style='color: #00b4d8; font-size: 36px; font-weight: 800; margin: 0; animation: pulse 1.5s ease-in-out infinite;'>
            PulseIQ – AI & Analytics Decision Support
        </h1>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="subheading">Upload your own data → Our algorithms will analyze it for you→ You will see actionable insights!</div>', unsafe_allow_html=True)

# ---- Description Box ----
st.markdown("""
<div class="description-box">
    <p>Welcome! Our AI app helps you analyze sentiments across any geographical locations known.</p>
    <ul>
        <li>Start by uploading your data with human-recorded sentiments.</li>
        <li>Go to the <strong>"Your Data Insights by PulseIQ"</strong> page to process your file.</li>
        <li>Explore visualizations, maps, comparisons and trends inside the <strong>Dashboard</strong>.</li>
    </ul>
    <p>📅 For time-series analysis, use the sidebar options to dive deeper into trends!</p>
</div>
""", unsafe_allow_html=True)
