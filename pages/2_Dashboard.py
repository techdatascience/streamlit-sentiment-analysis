import streamlit as st
import plotly.express as px
import pandas as pd
import requests

st.header("📊 Sentiment Dashboard")

if 'df' in st.session_state:
    df = st.session_state['df']
    df['county_name'] = df['county_name'].str.lower()  # Ensure lowercase for matching

    # Load Florida counties GeoJSON (cached to avoid re-downloading)
    @st.cache_data
    def load_florida_geojson():
        url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
        all_counties = requests.get(url).json()
        florida = {
            "type": "FeatureCollection",
            "features": [f for f in all_counties["features"] if f["properties"]["STATE"] == "12"]
        }
        for feature in florida['features']:
            feature['properties']['county_name'] = feature['properties']['NAME'].lower()
        return florida

    florida_geojson = load_florida_geojson()

    # Sentiment color mapping
    sentiment_colors = {
        "Strong Positive": "darkgreen",
        "Positive": "lightgreen",
        "Neutral": "gray",
        "Negative": "orange",
        "Strong Negative": "red"
    }

    # Define tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Donut Chart", "📊 Histogram", "🧾 Raw Data", "🗺️ Florida Map"])

    # --- Donut Chart ---
    with tab1:
        st.subheader("Sentiment Distribution (Donut)")
        sentiment_counts = df['Sentiment_WordNet_Custom'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig = px.pie(sentiment_counts, names='Sentiment', values='Count', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    # --- Histogram ---
    with tab2:
        st.subheader("Polarity Score Histogram")
        fig2 = px.histogram(df, x='Polarity_WordNet_Custom', nbins=30, title="Polarity Score Distribution")
        st.plotly_chart(fig2, use_container_width=True)

    # --- Raw Data ---
    with tab3:
        st.subheader("Raw Data Preview")
        st.dataframe(df.head(50))

    # --- Florida County Map ---
    with tab4:
        st.subheader("County-wise Sentiment Map of Florida")
        try:
            fig3 = px.choropleth_mapbox(
                df,
                geojson=florida_geojson,
                locations='county_name',
                featureidkey="properties.county_name",
                color='Sentiment_WordNet_Custom',
                color_discrete_map=sentiment_colors,
                mapbox_style="carto-positron",
                center={"lat": 27.8, "lon": -81.7},
                zoom=5.5,
                opacity=0.7,
                title="County-wise Sentiment Analysis in Florida (2022)"
            )
            fig3.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
            st.plotly_chart(fig3, use_container_width=True)
        except Exception as e:
            st.error(f"Error generating map: {e}")

else:
    st.warning("⚠️ Please upload and analyze data first on the 'Upload and Analyze' page.")




# import streamlit as st
# import plotly.express as px
# import pandas as pd

# st.header("📊 Sentiment Dashboard")

# if 'df' in st.session_state:
#     df = st.session_state['df']
    
#     # Define tabs
#     tab1, tab2, tab3 = st.tabs(["📈 Donut Chart", "📊 Histogram", "🧾 Raw Data"])

#     # --- Donut Chart ---
#     with tab1:
#         st.subheader("Sentiment Distribution (Donut)")
#         sentiment_counts = df['Sentiment_WordNet_Custom'].value_counts().reset_index()
#         sentiment_counts.columns = ['Sentiment', 'Count']
#         fig = px.pie(sentiment_counts, names='Sentiment', values='Count', hole=0.4)
#         st.plotly_chart(fig, use_container_width=True)

#     # --- Histogram ---
#     with tab2:
#         st.subheader("Polarity Score Histogram")
#         fig2 = px.histogram(df, x='Polarity_WordNet_Custom', nbins=30, title="Polarity Score Distribution")
#         st.plotly_chart(fig2, use_container_width=True)

#     # --- Raw Data ---
#     with tab3:
#         st.subheader("Raw Data Preview")
#         st.dataframe(df.head(50))

# else:
#     st.warning("⚠️ Please upload and analyze data first on the 'Upload and Analyze' page.")


# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import requests

# st.header("📊 Sentiment Dashboard")

# # Load DataFrame from session state
# df = st.session_state.get('df')
# if df is None:
#     st.warning("Please upload and analyze data first on the 'Upload and Analyze' page.")
#     st.stop()

# # Ensure case consistency
# df['state_name'] = df['state_name'].str.title()
# df['county_name'] = df['county_name'].str.lower()

# # Load US counties GeoJSON (only once)
# @st.cache_data
# def load_geojson():
#     url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
#     return requests.get(url).json()

# counties_geojson = load_geojson()

# # Filter Florida
# florida_geojson = {
#     "type": "FeatureCollection",
#     "features": [f for f in counties_geojson["features"] if f["properties"]["STATE"] == "12"]
# }
# for feature in florida_geojson['features']:
#     feature['properties']['county_name'] = feature['properties']['NAME'].lower()

# # Colors for sentiment
# sentiment_colors = {
#     "Strong Positive": "darkgreen",
#     "Positive": "lightgreen",
#     "Neutral": "gray",
#     "Negative": "orange",
#     "Strong Negative": "red"
# }

# # === UI for Drilldown ===
# st.subheader("🗺️ Florida County Sentiment Map")

# selected_state = st.selectbox("Select State", sorted(df['state_name'].unique()))
# state_df = df[df['state_name'] == selected_state]

# selected_county = st.selectbox("Select County", sorted(state_df['county_name'].unique()))
# county_df = state_df[state_df['county_name'] == selected_county]

# fig = px.choropleth_map(
#     state_df,
#     geojson=florida_geojson,
#     locations='county_name',
#     featureidkey="properties.county_name",
#     color='Sentiment_WordNet_Custom',
#     color_discrete_map=sentiment_colors,
#     center={"lat": 27.8, "lon": -81.7},
#     zoom=6,
#     opacity=0.7,
#     title=f"County-wise Sentiment in {selected_state}"
# )

# fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
# st.plotly_chart(fig, use_container_width=True)

# # Optional: Show filtered table
# with st.expander("See data for selected county"):
#     st.dataframe(county_df)

# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import requests

# # Assuming df is loaded somewhere above or passed into this file:
# df = st.session_state.get('df')
# if df is None:
#     st.warning("Upload and analyze data first!")
#     st.stop()

# # Fix capitalization for consistency
# df['state_name'] = df['state_name'].str.title()
# df['county_name'] = df['county_name'].str.lower()

# # Load GeoJSON once
# @st.cache_data
# def load_geojson():
#     url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
#     return requests.get(url).json()

# counties_geojson = load_geojson()

# # Filter to Florida counties (STATE == '12')
# florida_geojson = {
#     "type": "FeatureCollection",
#     "features": [f for f in counties_geojson["features"] if f["properties"]["STATE"] == "12"]
# }
# for f in florida_geojson["features"]:
#     f["properties"]["county_name"] = f["properties"]["NAME"].lower()

# # Sentiment colors
# sentiment_colors = {
#     "Strong Positive": "darkgreen",
#     "Positive": "lightgreen",
#     "Neutral": "gray",
#     "Negative": "orange",
#     "Strong Negative": "red"
# }

# # === Tabs ===
# tab = st.sidebar.radio("Navigate to", ["Summary", "Graphs", "Other Tabs..."])

# if tab == "Summary":
#     st.header("Summary stats and info here")
#     # Your existing summary/dashboard code

# elif tab == "Graphs":
#     st.header("🗺️ Florida County-wise Sentiment Map")

#     # Filter data for Florida state - assuming 'state_name' for Florida is 'Florida'
#     florida_df = df[df['state_name'] == "Florida"]

#     fig = px.choropleth_map(
#         florida_df,
#         geojson=florida_geojson,
#         locations='county_name',
#         featureidkey="properties.county_name",
#         color='Sentiment_WordNet_Custom',
#         color_discrete_map=sentiment_colors,
#         center={"lat": 27.8, "lon": -81.7},
#         zoom=6,
#         opacity=0.7,
#         title="County-wise Sentiment Analysis in Florida"
#     )
#     fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

#     st.plotly_chart(fig, use_container_width=True)

# # Add more elif tabs for your other dashboard sections if needed

