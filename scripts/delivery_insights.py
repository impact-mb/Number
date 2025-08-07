import streamlit as st
import pandas as pd
import plotly.express as px

def render_session_attendance_by_date(df):
    st.markdown("### 📅 Session Attendance by Date & Curriculum")

    df['SessionHeldOn'] = pd.to_datetime(df['SessionHeldOn'], errors='coerce')
    df = df.dropna(subset=['SessionHeldOn', 'ChildID', 'CurriculumCode'])
    df['SessionDate'] = df['SessionHeldOn'].dt.date

    min_date = df['SessionDate'].min()
    max_date = df['SessionDate'].max()
    selected_date = st.date_input("Select Session Date", value=min_date, min_value=min_date, max_value=max_date)

    filtered_df = df[df['SessionDate'] == selected_date]

    # 🔍 Inline Filters (2 rows of 3 columns each)
    col1, col2, col3 = st.columns(3)
    col4, col5, col6 = st.columns(3)

    def apply_multiselect(col_obj, label, column):
        if column in filtered_df.columns:
            options = filtered_df[column].dropna().unique()
            selected = col_obj.multiselect(f"{label}", options, default=list(options))
            return filtered_df[filtered_df[column].isin(selected)]
        return filtered_df

    filtered_df = apply_multiselect(col1, "Region", "REGIONNAME")
    filtered_df = apply_multiselect(col2, "State", "STATENAME")
    filtered_df = apply_multiselect(col3, "District", "DISTRICTNAME")
    filtered_df = apply_multiselect(col4, "Program SubType", "ProgramSubType")
    filtered_df = apply_multiselect(col5, "Funder Name", "FunderName")
    filtered_df = apply_multiselect(col6, "Program Launch Name", "PROGRAMLAUNCHNAME")

    if filtered_df.empty:
        st.warning("No sessions found for the selected filters.")
        return

    # 🧮 Group data
    merged_summary = (
        filtered_df.groupby(['REGIONNAME', 'STATENAME', 'DISTRICTNAME', 'CurriculumCode', 'Gender'])['ChildID']
        .nunique()
        .reset_index(name='UniqueChildrenAttended')
    )

    # 📊 Bar Chart
    fig = px.bar(
        merged_summary,
        x='UniqueChildrenAttended',
        y='CurriculumCode',
        color='Gender',
        text='UniqueChildrenAttended',
        orientation='h',
        color_discrete_map={'Male': '#2986cc', 'Female': '#c90076'},
        barmode='stack',
        title=f"Session Attendance on {selected_date}"
    )
    fig.update_layout(xaxis_title="Unique Children Attended", yaxis_title="Curriculum Code")
    fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

    # 📋 Summary Table
    pivot_table = merged_summary.pivot_table(
        index=['REGIONNAME', 'STATENAME', 'DISTRICTNAME', 'CurriculumCode'],
        columns='Gender',
        values='UniqueChildrenAttended',
        fill_value=0
    ).reset_index()

    if 'Male' in pivot_table.columns and 'Female' in pivot_table.columns:
        pivot_table = pivot_table[['REGIONNAME', 'STATENAME', 'DISTRICTNAME', 'CurriculumCode', 'Male', 'Female']]

    st.markdown("#### 📋 Summary Table")
    st.dataframe(pivot_table, use_container_width=True)

    # 📊 Statistics
    st.markdown("### 🧮 Summary Statistics")
    st.write({
        "Total Curriculum Sessions": pivot_table['CurriculumCode'].nunique(),
        "Total Children Attended": int(pivot_table[['Male', 'Female']].sum().sum())
    })
