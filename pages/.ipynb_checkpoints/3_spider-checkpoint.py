import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.header("🔢 Spider Chart – Sentiment Comparison by County")

if 'df' not in st.session_state:
    st.warning("⚠️ Please upload and analyze data first on the 'Upload and Analyze' page.")
    st.stop()

# Load and prepare data
df = st.session_state['df']
df['county_name'] = df['county_name'].str.lower()
df['MMWR_WEEK'] = df['MMWR_WEEK'].astype(int)
df['Sentiments_pat_ana'] = df['Sentiments_pat_ana'].fillna('Unknown')

# Sidebar inputs
st.sidebar.subheader("🔢 Select Filters")
available_counties = sorted(df['county_name'].unique())
selected_counties = st.sidebar.multiselect("Select Counties to Compare", available_counties, default=["jackson", "miami-dade"])

# Filter weeks where selected counties have sentiment data
filtered_df = df[df['county_name'].isin(selected_counties)]
valid_weeks = (
    filtered_df[filtered_df['Sentiments_pat_ana'].notna()]
    .groupby('MMWR_WEEK')
    .size()
    .reset_index(name='Count')
)

if valid_weeks.empty:
    st.warning("No available weeks with sentiment data for selected counties.")
    st.stop()

available_weeks = sorted(valid_weeks['MMWR_WEEK'].unique())
selected_week = st.sidebar.selectbox("Select MMWR Week", available_weeks, index=len(available_weeks) - 1)

# Filter and aggregate
df_filtered = df[(df['MMWR_WEEK'] == selected_week) & (df['county_name'].isin(selected_counties))]

if df_filtered.empty:
    st.warning("No sentiment data available for the selected filters.")
    st.stop()

sentiment_order = ["Positive", "Neutral", "Negative"]
summary = df_filtered.groupby(['county_name', 'Sentiments_pat_ana']).size().unstack(fill_value=0).reindex(columns=sentiment_order, fill_value=0)

# Create Radar chart
fig = go.Figure()

for county in selected_counties:
    if county in summary.index:
        values = summary.loc[county].tolist()
        values.append(values[0])  # Close the loop

        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=sentiment_order + [sentiment_order[0]],
            fill='toself',
            name=county.title()
        ))

fig.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, summary.values.max() + 5])
    ),
    showlegend=True,
    title=f"🔢 Sentiment Distribution Radar Chart for Week {selected_week}"
)

st.plotly_chart(fig, use_container_width=True)

with st.expander("📄 View Underlying Data"):
    st.dataframe(summary.reset_index())
