import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# --- Set wide layout and apply PulseIQ header color styling ---
st.set_page_config(layout="wide")
st.markdown("""
<style>
h1, h2, h3, h4 {
    color: #00b4d8 !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🗺️ Florida County Sentiment – Trend Flow")

if 'df' in st.session_state:
    df = st.session_state['df'].copy()
    df['county_name'] = df['county_name'].str.lower()

    # Cleanup and ensure week formatting
    df = df[pd.to_numeric(df['MMWR_WEEK'], errors='coerce').notnull()]
    df['MMWR_WEEK'] = df['MMWR_WEEK'].astype(int)
    df = df[df['MMWR_WEEK'] > 0]
    df['week'] = df['MMWR_WEEK'].apply(lambda x: f"W{int(x):02}")

    sentiment_colors = {
        "Positive": "green",
        "Neutral": "blue",
        "Negative": "red"
    }

    # Load Florida GeoJSON
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    geojson = requests.get(url).json()
    florida_geo = {
        "type": "FeatureCollection",
        "features": [f for f in geojson["features"] if f["properties"]["STATE"] == "12"]
    }
    for f in florida_geo["features"]:
        f["properties"]["county_name"] = f["properties"]["NAME"].lower()

    # Create full county-week grid
    all_weeks = sorted(df['MMWR_WEEK'].unique())
    week_map = {w: f"W{int(w):02}" for w in all_weeks}
    df['week'] = df['MMWR_WEEK'].map(week_map)
    all_counties = sorted(df['county_name'].unique())
    full_index = pd.MultiIndex.from_product([all_counties, all_weeks], names=['county_name', 'MMWR_WEEK'])
    df_full = pd.DataFrame(index=full_index).reset_index()
    df_full['week'] = df_full['MMWR_WEEK'].map(week_map)

    # Merge most common sentiment per county per week
    agg_df = df.groupby(['county_name', 'MMWR_WEEK'])['Sentiments_pat_ana'].agg(
        lambda x: x.mode().iloc[0] if not x.mode().empty else None
    ).reset_index()
    df_full = df_full.merge(agg_df, on=['county_name', 'MMWR_WEEK'], how='left')

    # Forward fill for gaps
    df_full['Sentiments Trends'] = df_full.groupby('county_name')['Sentiments_pat_ana'].ffill()
    df_full['Sentiments Trends'] = pd.Categorical(
        df_full['Sentiments Trends'],
        categories=["Positive", "Neutral", "Negative"],
        ordered=True
    )

    # Choropleth
    fig_map = px.choropleth_mapbox(
        df_full,
        geojson=florida_geo,
        locations='county_name',
        featureidkey="properties.county_name",
        color='Sentiments Trends',
        category_orders={"Sentiments Trends": ["Positive", "Neutral", "Negative"]},
        color_discrete_map=sentiment_colors,
        animation_frame='week',
        mapbox_style="carto-positron",
        center={"lat": 27.8, "lon": -81.7},
        zoom=5.5,
        opacity=0.75,
        title="🗺️ Weekly Sentiment Trends Across Florida Counties"
    )

    fig_map.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        legend_title_text="Sentiment"
    )

    st.plotly_chart(fig_map, use_container_width=True)

else:
    st.warning("⚠️ Please upload and analyze data first on the 'Upload and Analyze' page.")
