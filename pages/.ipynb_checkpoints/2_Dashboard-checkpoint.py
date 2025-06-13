import streamlit as st
import plotly.express as px
import pandas as pd
import requests

st.header("📊 Sentiment Dashboard – TextBlob")

if 'df' in st.session_state:
    df = st.session_state['df']
    df['county_name'] = df['county_name'].str.lower()
    df['MMWR_WEEK'] = df['MMWR_WEEK'].astype(int)  # Ensure numeric sorting
    df['week'] = df['MMWR_WEEK'].apply(lambda x: f"W{int(x):02}")  # For display

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
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Donut Chart", 
        "📊 Histogram", 
        "🧾 Raw Data", 
        "🗽 Florida Map", 
        "🖱️Interactive Map + Trends"
    ])

    with tab1:
        st.subheader("Sentiment Distribution (Donut)")
        sentiment_counts = df['Sentiments_pat_ana'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig = px.pie(sentiment_counts, names='Sentiment', values='Count', hole=0.4,
                     color='Sentiment', color_discrete_map=sentiment_colors)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Polarity Score Histogram")
        fig2 = px.histogram(df, x='Polarity_pat_ana', nbins=30)
        st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        st.subheader("Raw Data Preview")
        st.dataframe(df.head(50))

    with tab4:
        st.subheader("🗽 Weekly County-wise Sentiment Trends (Animated + Drill-down)")

        df_viz = df.copy()
        all_weeks = sorted(df_viz['MMWR_WEEK'].unique())
        week_map = {week: f"W{int(week):02}" for week in all_weeks}
        df_viz['week'] = df_viz['MMWR_WEEK'].map(week_map)
        all_counties = sorted(df_viz['county_name'].unique())

        full_index = pd.MultiIndex.from_product([all_counties, all_weeks], names=['county_name', 'MMWR_WEEK'])
        df_full = pd.DataFrame(index=full_index).reset_index()
        df_full['week'] = df_full['MMWR_WEEK'].map(week_map)

        agg_df = df_viz.groupby(['county_name', 'MMWR_WEEK'])['Sentiments_pat_ana'].agg(
            lambda x: x.mode().iloc[0] if not x.mode().empty else None
        ).reset_index()

        df_full = df_full.merge(agg_df, on=['county_name', 'MMWR_WEEK'], how='left')
        df_full['Sentiments Trends'] = df_full.groupby('county_name')['Sentiments_pat_ana'].ffill()
        df_full['Sentiments Trends'] = pd.Categorical(df_full['Sentiments Trends'],
                                                      categories=["Positive", "Neutral", "Negative"],
                                                      ordered=True)

        fig_anim = px.choropleth_mapbox(
            df_full,
            geojson=florida_geojson,
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
            title="Weekly Sentiment Flow (County-wise) – Florida 2022"
        )
        fig_anim.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, legend_title_text="Sentiment")
        st.plotly_chart(fig_anim, use_container_width=True, config={"scrollZoom": True})

        # --- Interactivity Section ---
        st.markdown("### 🔍 Explore Sentiment Trends")
        mode = st.radio("Analyze by:", ["County", "Week"], horizontal=True)

        if mode == "County":
            st.subheader("📈 Weekly Sentiment Trends by County")
    
            # Remove invalid week entries
            df_viz = df_viz[df_viz['MMWR_WEEK'] > 0]
    
            selected_counties = st.multiselect("Select County/Counties", sorted(all_counties), default=["jackson"])
    
            if selected_counties:
                filtered_df = df_viz[df_viz['county_name'].isin(selected_counties)]
    
                sentiment_weekly = (
                    filtered_df.groupby(['MMWR_WEEK', 'county_name', 'Sentiments_pat_ana'])
                    .size()
                    .reset_index(name="Count")
                )
                sentiment_weekly['week_label'] = sentiment_weekly['MMWR_WEEK'].apply(lambda x: f"W{int(x):02}")
    
                fig = px.line(
                    sentiment_weekly,
                    x="MMWR_WEEK",
                    y="Count",
                    color="Sentiments_pat_ana",         # Color by sentiment
                    line_dash="Sentiments_pat_ana",     # Dash by sentiment
                    line_group="county_name",           # Distinguish counties
                    markers=True,
                    hover_data={"week_label": True, "MMWR_WEEK": False},
                    labels={
                        "MMWR_WEEK": "Week",
                        "Count": "Sentiment Count",
                        "county_name": "County",
                        "Sentiments_pat_ana": "Sentiment"
                    },
                    title="📉 Weekly Sentiment Trends by County"
                )
    
                # Custom colors and dash styles
                sentiment_colors = {
                    "Positive": "green",
                    "Neutral": "blue",
                    "Negative": "red"
                }
                dash_map = {
                    "Positive": "solid",
                    "Neutral": "dash",
                    "Negative": "dot"
                }
    
                for trace in fig.data:
                    sentiment = trace.name.lower()
                    for key in sentiment_colors:
                        if key.lower() in sentiment:
                            trace.line.color = sentiment_colors[key]
                            trace.line.dash = dash_map[key]
    
                fig.update_layout(
                    xaxis=dict(tickmode="linear", tick0=1, dtick=1, title="MMWR Week"),
                    xaxis_tickangle=-45
                )
    
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("👈 Please select at least one county to display the trend.")


        elif mode == "Week":
            selected_week_num = st.selectbox("Select a Week", sorted(all_weeks))
            selected_week = f"W{int(selected_week_num):02}"
            week_df = df_viz[df_viz['MMWR_WEEK'] == selected_week_num].copy()

            sentiment_by_county = week_df.groupby(['county_name', 'Sentiments_pat_ana']).size().unstack(fill_value=0)
            st.subheader(f"Sentiment Distribution in **{selected_week}**")
            st.bar_chart(sentiment_by_county)

    with tab5:
        st.subheader("📉 Weekly Sentiment Trend for Selected County")

        available_counties = df['county_name'].dropna().str.lower().unique()
        selected_county = st.selectbox("Select County", sorted(available_counties))

        df_county = df[df['county_name'].str.lower() == selected_county.lower()].copy()

        if df_county.empty:
            st.warning("No data available for the selected county.")
        else:
            df_county['MMWR_WEEK'] = df_county['MMWR_WEEK'].astype(int)
            df_county['week_label'] = df_county['MMWR_WEEK'].apply(lambda x: f"W{int(x):02}")

            sentiment_by_week = df_county.groupby(['MMWR_WEEK', 'Sentiments_pat_ana']).size().unstack(fill_value=0).reset_index()
            sentiment_by_week = sentiment_by_week.sort_values("MMWR_WEEK")

            sentiment_long = sentiment_by_week.melt(
                id_vars="MMWR_WEEK",
                var_name="Sentiment",
                value_name="Count"
            )
            sentiment_long["week_label"] = sentiment_long["MMWR_WEEK"].apply(lambda x: f"W{int(x):02}")

            fig_county = px.line(
                sentiment_long,
                x="MMWR_WEEK",
                y="Count",
                color="Sentiment",
                markers=True,
                hover_data={"week_label": True, "MMWR_WEEK": False},
                labels={
                    "MMWR_WEEK": "Week",
                    "Count": "Sentiment Count",
                    "Sentiment": "Sentiment"
                },
                title=f"📉 Weekly Sentiment Trend – {selected_county.title()}"
            )

            for sentiment, color in sentiment_colors.items():
                fig_county.for_each_trace(
                    lambda trace: trace.update(line=dict(color=color))
                    if sentiment in trace.name else ()
                )

            fig_county.update_layout(
                xaxis=dict(tickmode="linear", tick0=1, dtick=1, title="MMWR Week"),
                xaxis_tickangle=-45
            )

            st.plotly_chart(fig_county, use_container_width=True)

            with st.expander("📄 View Raw Trend Data"):
                st.dataframe(sentiment_by_week)

else:
    st.warning("⚠️ Please upload and analyze data first on the 'Upload and Analyze' page.")
