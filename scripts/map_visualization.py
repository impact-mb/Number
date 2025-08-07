import streamlit as st
import pandas as pd
import plotly.express as px

def render_india_map(df):
    st.markdown("### 🗺️ District-Wise Session Attendance Map")

    required_cols = ['STATENAME', 'DISTRICTNAME', 'ChildID']
    if not all(col in df.columns for col in required_cols):
        st.warning("Missing columns required for mapping: STATENAME, DISTRICTNAME, or ChildID")
        return

    map_df = df.groupby(['STATENAME']).agg({
        'ChildID': pd.Series.nunique
    }).reset_index().rename(columns={'ChildID': 'UniqueChildrenAttended'})

    fig = px.choropleth(
        map_df,
        locations="STATENAME",
        locationmode="country names",
        color="UniqueChildrenAttended",
        hover_name="STATENAME",
        color_continuous_scale="Plasma",
        title="Session Attendance by State"
    )
    st.plotly_chart(fig, use_container_width=True)
