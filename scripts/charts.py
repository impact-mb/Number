import streamlit as st
import plotly.express as px

def plot_gender_distribution(df, subtype):
    if 'DistrictName' in df.columns and 'Gender' in df.columns:
        gender_df = df[df['Gender'].isin(['Male', 'Female'])].copy()
        summary = (
            gender_df.groupby(['DistrictName', 'Gender'])
            .size().reset_index(name='Count')
        )
        fig = px.bar(
            summary, x='DistrictName', y='Count', color='Gender', text='Count',
            color_discrete_map={'Male': '#2986cc', 'Female': '#c90076'},
            barmode='group', title=f'Gender Distribution in {subtype} by District'
        )
        fig.update_traces(textposition='inside')
        fig.update_layout(xaxis_title='District', yaxis_title='Number of Children')
        st.plotly_chart(fig, use_container_width=True)