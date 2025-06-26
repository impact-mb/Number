import streamlit as st
import pandas as pd

def render_cumulative_tabulation(planner_df, delivery_df):
    st.header("\U0001F4CA Cumulative Report")

    if planner_df is None or delivery_df is None:
        st.warning("Please upload both Delivery and Annual Session Planner files to see the cumulative report.")
        return

    delivery_df = delivery_df.copy()

    if 'ClassOftheChildAttendingsch' in delivery_df.columns:
        delivery_df = delivery_df.rename(columns={'ClassOftheChildAttendingsch': 'Grade'})

    if 'ProgrameSubType' in planner_df.columns:
        planner_df = planner_df.rename(columns={'ProgrameSubType': 'ProgramSubType'})

    delivery_df['Grade'] = delivery_df['Grade'].astype(str)
    planner_df['Grade'] = planner_df['Grade'].astype(str)

    # Grade filter
    if 'Grade' in planner_df.columns:
        all_grades = sorted(planner_df['Grade'].dropna().unique())
        selected_grades = st.sidebar.multiselect(
            "Select Grade (All selected by default)", options=all_grades, default=all_grades
        )
        planner_df = planner_df[planner_df['Grade'].isin(selected_grades)]

    if 'ChildId' not in delivery_df.columns:
        st.error("❌ 'ChildId' column is missing in Delivery Data. Cannot compute outreach.")
        return

    if 'RegularSessions' not in delivery_df.columns:
        st.error("❌ 'RegularSessions' column is missing in Delivery Data. Cannot compute attended sessions.")
        return

    with st.expander("🧪 Debug Info"):
        st.write("Planner Data Sample")
        st.dataframe(planner_df.head())
        st.write("Delivery Data Sample")
        st.dataframe(delivery_df.head())

    # Step 1: Sum RegularSessions attended by each child
    session_counts = delivery_df.groupby(
        ['ProgramLaunchName', 'Grade', 'ProgramSubType', 'ChildId']
    )['RegularSessions'].sum().reset_index(name='TotalRegularSessionAttended')

    # Step 1a: Count 0 and 1 sessions attended
    session_0_1 = delivery_df.groupby(
        ['ProgramLaunchName', 'Grade', 'ProgramSubType', 'ChildId']
    )['RegularSessions'].sum().reset_index()
    session_0_1['0 Session Attended'] = (session_0_1['RegularSessions'] == 0).astype(int)
    session_0_1['1 Session Attended'] = (session_0_1['RegularSessions'] == 1).astype(int)

    session_0_1_summary = session_0_1.groupby(['ProgramLaunchName', 'Grade', 'ProgramSubType']).agg({
        '0 Session Attended': 'sum',
        '1 Session Attended': 'sum'
    }).reset_index()

    # Step 2: Merge session counts with planner
    merged = pd.merge(
        planner_df,
        session_counts,
        how='left',
        on=['ProgramLaunchName', 'Grade', 'ProgramSubType']
    )

    # Step 3: Compare sessions attended with SessionsPlannedUpto
    merged['MeetsTarget'] = merged['TotalRegularSessionAttended'] >= merged['SessionsPlannedUpto']

    # Step 4: Count number of children meeting or exceeding target and total outreach
    summary = merged.groupby(['ProgramLaunchName', 'Grade', 'ProgramSubType'], as_index=False).agg({
        'SessionsPlannedUpto': 'first',
        'MeetsTarget': 'sum',
        'ChildId': pd.Series.nunique
    }).rename(columns={
        'MeetsTarget': 'ChildrenMeetingTarget',
        'ChildId': 'TotalOutreach'
    })

    # Merge session attendance counts
    summary = pd.merge(summary, session_0_1_summary, on=['ProgramLaunchName', 'Grade', 'ProgramSubType'], how='left')

    # Step 5: Calculate % Achievement
    summary['%Achievement'] = (summary['ChildrenMeetingTarget'] / summary['TotalOutreach']) * 100
    summary['%Achievement'] = summary['%Achievement'].round(2)

    st.markdown("### \U0001F3AF Children Meeting Planned Session Targets")
    st.dataframe(summary, use_container_width=True)