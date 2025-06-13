import streamlit as st
import plotly.express as px
import pandas as pd
import requests

# --- Apply PulseIQ blue styling to headers globally ---
st.markdown("""
<style>
h1, h2, h3, h4 {
    color: #00b4d8 !important;
}
</style>
""", unsafe_allow_html=True)

st.header("📊 Sentiment Dashboard")

if 'df' in st.session_state:
    df = st.session_state['df']
    df['county_name'] = df['county_name'].str.lower()

    # 🧹 Final cleanup of week values
    df = df[pd.to_numeric(df['MMWR_WEEK'], errors='coerce').notnull()]
    df['MMWR_WEEK'] = df['MMWR_WEEK'].astype(int)
    df = df[df['MMWR_WEEK'] > 0]

    df['week'] = df['MMWR_WEEK'].apply(lambda x: f"W{int(x):02}")

    @st.cache_data
    def load_florida_geojson():
        url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
        geojson = requests.get(url).json()
        florida = {
            "type": "FeatureCollection",
            "features": [f for f in geojson["features"] if f["properties"]["STATE"] == "12"]
        }
        for f in florida["features"]:
            f["properties"]["county_name"] = f["properties"]["NAME"].lower()
        return florida

    florida_geojson = load_florida_geojson()

    sentiment_colors = {
        "Positive": "green",
        "Neutral": "blue",
        "Negative": "red"
    }

    # Tabs
    tab1, tab2 = st.tabs([
        "📈 % of Sentimental Collection",
        "🗽 County and Counties Comparison"
    ])

    with tab1:
        st.subheader("📈 % of Sentimental Collection")
        sentiment_counts = df['Sentiments_pat_ana'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig = px.pie(sentiment_counts, names='Sentiment', values='Count', hole=0.4,
                     color='Sentiment', color_discrete_map=sentiment_colors)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("📊 Weekly Sentiment Capture for Selected County")

        selected_county = st.selectbox("Select a County", sorted(df['county_name'].unique()), index=0)
        df_county = df[df['county_name'] == selected_county]

        if df_county.empty:
            st.warning("No data available for the selected county.")
        else:
            sentiment_summary = df_county.groupby(['MMWR_WEEK', 'Sentiments_pat_ana']).size().reset_index(name="Count")

            all_weeks = list(range(1, 53))
            all_sentiments = ['Positive', 'Neutral', 'Negative']
            full_index = pd.MultiIndex.from_product([all_weeks, all_sentiments], names=['MMWR_WEEK', 'Sentiments_pat_ana'])
            sentiment_summary = sentiment_summary.set_index(['MMWR_WEEK', 'Sentiments_pat_ana']).reindex(full_index, fill_value=0).reset_index()

            fig_bar = px.bar(
                sentiment_summary,
                x="MMWR_WEEK",
                y="Count",
                color="Sentiments_pat_ana",
                text="Count",
                barmode="stack",
                labels={
                    "MMWR_WEEK": "Week",
                    "Count": "Sentiment Count",
                    "Sentiments_pat_ana": "Sentiment"
                },
                color_discrete_map=sentiment_colors,
                title=f"Weekly Sentiment Trend – {selected_county.title()}"
            )

            fig_bar.update_traces(textposition="inside")
            fig_bar.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(1, 53)),
                    ticktext=[str(i) for i in range(1, 53)],
                    title="Week"
                ),
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📊 Multi County Comparison for Decision Making")
        selected_sentiment = st.selectbox("Select Sentimental trend to Compare", ['Positive', 'Neutral', 'Negative'])
        county_comparison = (
            df[df['Sentiments_pat_ana'] == selected_sentiment]
            .groupby('county_name')
            .size()
            .reset_index(name='Count')
            .sort_values(by='Count', ascending=False)
        )

        fig_cmp = px.bar(
            county_comparison,
            x='county_name',
            y='Count',
            text='Count',
            title=f"Total '{selected_sentiment}' Sentiment Reports by County",
            labels={"county_name": "County", "Count": "Total Count"},
            color_discrete_sequence=[sentiment_colors[selected_sentiment]]
        )
        fig_cmp.update_traces(textposition='outside')
        fig_cmp.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_cmp, use_container_width=True)

else:
    st.warning("⚠️ Please upload and analyze data first on the 'Upload and Analyze' page.")
