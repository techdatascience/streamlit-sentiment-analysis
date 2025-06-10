import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import sentiwordnet as swn, wordnet
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import re
import unicodedata

# Download resources if not already available
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('sentiwordnet')
nltk.download('averaged_perceptron_tagger')

st.header("📤 Upload CSV & Analyze")

uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

# Cleaning function
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

# POS tag conversion
def get_wordnet_pos(word):
    tag = pos_tag([word])[0][1][0].upper()
    return {
        'J': wordnet.ADJ,
        'N': wordnet.NOUN,
        'V': wordnet.VERB,
        'R': wordnet.ADV
    }.get(tag, wordnet.NOUN)

# Custom SentiWordNet sentiment analysis
def custom_sentiwordnet_sentiment(text):
    words = word_tokenize(str(text).lower())
    pos_score = 0
    neg_score = 0
    count = 0

    for word in words:
        wn_pos = get_wordnet_pos(word)
        synsets = list(swn.senti_synsets(word, wn_pos))
        if synsets:
            s = synsets[0]
            pos_score += s.pos_score()
            neg_score += s.neg_score()
            count += 1

    if count == 0:
        final_score = 0
    else:
        final_score = pos_score - neg_score

    if final_score >= 0.5:
        sentiment = "Strong Positive"
    elif 0.05 < final_score < 0.5:
        sentiment = "Positive"
    elif -0.05 < final_score <= 0.05:
        sentiment = "Neutral"
    elif -0.5 < final_score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Strong Negative"
        
    return pd.Series([final_score, sentiment])

# Main logic
if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='unicode_escape')
    
    if 'Description' not in df.columns:
        st.error("CSV must contain a 'Description' column.")
    else:
        df['Description_cleaned'] = df['Description'].apply(clean_description)
        df[['Polarity_WordNet_Custom', 'Sentiment_WordNet_Custom']] = df['Description_cleaned'].apply(custom_sentiwordnet_sentiment)

        st.session_state['df'] = df

        st.success("✅ Data processed successfully!")
        st.write(f"🧮 Rows: {df.shape[0]} | Columns: {df.shape[1]}")
        st.dataframe(df.head())
