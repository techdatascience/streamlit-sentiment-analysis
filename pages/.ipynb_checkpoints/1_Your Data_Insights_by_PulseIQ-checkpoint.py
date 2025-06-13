import streamlit as st
import pandas as pd
from textblob import TextBlob
from textblob.sentiments import PatternAnalyzer
import re
import unicodedata

# Page config and styling
st.set_page_config(page_title="Your Data Insights by PulseIQ", layout="wide")

st.markdown("""
<style>
h1, h2, h3, h4 {
    color: #00b4d8 !important;
}
</style>
""", unsafe_allow_html=True)

st.header("📤 Get your Data Insights")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# --- Clean text ---
def clean_description(text):
    if pd.isna(text): return ""
    text = text.lower()
    replacements = {
        '\x91': "'", '\x92': "'", '\x93': '"', '\x94': '"',
        '\x96': '-', '\x97': '-', '\xa0': ' ',
        '’': "'", '‘': "'", '“': '"', '”': '"',
        '–': '-', '—': '-', '…': '...',
        '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
    }
    for bad_char, replacement in replacements.items():
        text = text.replace(bad_char, replacement)
    text = unicodedata.normalize("NFKD", text).encode("ascii", errors="ignore").decode()
    text = re.sub(r'([.,!?;:()\[\]\'"-])', r' \1 ', text)
    return re.sub(r'\s+', ' ', text).strip()

# --- Analyze using PatternAnalyzer ---
def analyze_sentiment(text):
    try:
        blob = TextBlob(str(text), analyzer=PatternAnalyzer())
        polarity = blob.sentiment[0]
        if polarity > 0:
            sentiment = "Positive"
        elif polarity < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"
        return pd.Series([polarity, sentiment])
    except Exception:
        return pd.Series([None, "Error"])

# --- Main logic ---
if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='unicode_escape')

    if 'Description' not in df.columns:
        st.error("CSV must contain a 'Description' column.")
    else:
        df['Description_cleaned'] = df['Description'].apply(clean_description)
        df[['Polarity_pat_ana', 'Sentiments_pat_ana']] = df['Description_cleaned'].apply(analyze_sentiment)

        st.session_state['df'] = df

        st.success("✅ Data processed successfully!")
        st.write(f"🧮 Rows: {df.shape[0]} | Columns: {df.shape[1]}")

        # Exclude unwanted columns in preview
        columns_to_exclude = ["Current_MMWR_Year", "Description", "Total Cases", "Current_Week_Cases"]
        columns_to_show = [col for col in df.columns if col not in columns_to_exclude]

        st.markdown("🔍 Showing preview with selected columns only:")
        st.dataframe(df[columns_to_show].head())
