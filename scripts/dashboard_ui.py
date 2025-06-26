import streamlit as st
import pandas as pd
from charts import plot_gender_distribution
from tables import generate_pivot_tables

class Dashboard:
    def __init__(self, df, analyzer, asp_df=None):
        self.df = df
        self.analyzer = analyzer
        self.asp_df = asp_df  # You can use it later if needed

    def render(self):
        if 'ClassOftheChildAttendingsch' in self.df.columns:
            self.df = self.df.rename(columns={'ClassOftheChildAttendingsch': 'Grade'})

        if hasattr(self.analyzer, 'duplicate_count') and self.analyzer.duplicate_count > 0:
            st.warning(
                f"Number of duplicate records based on DistrictName, ProgramSubType, and ChildId: "
                f"{self.analyzer.duplicate_count} (duplicates were removed)"
            )

        try:
            if 'ProgramSubType' in self.df.columns:
                subtypes = self.df['ProgramSubType'].dropna().unique().tolist()
                selected_subtype = st.sidebar.radio("Select Program Type", subtypes)
                df_filtered = self.df[self.df['ProgramSubType'] == selected_subtype].copy()

                # Handle Grade filtering
                if 'Grade' in df_filtered.columns:
                    grades = sorted(df_filtered['Grade'].dropna().unique())
                    grades = [str(int(float(g))) for g in grades if str(g).replace('.', '', 1).isdigit()]
                    selected_grades = st.sidebar.multiselect(
                        "Select Grade (All selected by default)", options=grades, default=grades
                    )
                    df_filtered = df_filtered[df_filtered['Grade'].astype(str).isin(selected_grades)]

                st.header(f"📘 Program: {selected_subtype}")

                # Summary Details
                funder_names = df_filtered['FunderName'].dropna().unique()
                launch_names = df_filtered['ProgramLaunchName'].dropna().unique()
                ym_count = df_filtered['YMName'].nunique()
                tmo_names = df_filtered['TMOName'].dropna().unique()
                state_names = df_filtered['StateName'].dropna().unique()
                district_names = df_filtered['DistrictName'].dropna().unique()
                total = len(df_filtered)
                gender_counts = df_filtered['Gender'].value_counts()
                male = gender_counts.get('Male', 0)
                female = gender_counts.get('Female', 0)

                # Summary Text Block
                st.success(
                    f"{', '.join(funder_names)} is implementing {selected_subtype}.\n"
                    f"There are {len(launch_names)} unique Program Launch Names: {', '.join(launch_names)}.\n"
                    f"We are working in the states of {', '.join(state_names)} and districts of {', '.join(district_names)}.\n"
                    f"This program currently has {ym_count} unique YM(s) under TMO(s): {', '.join(tmo_names)}."
                )

                # Gender totals
                st.info(
                    f"Total children enrolled in {selected_subtype}: {total} (Male - {male}, Female - {female})"
                )

                # Charts and Tables
                plot_gender_distribution(df_filtered, selected_subtype)
                generate_pivot_tables(df_filtered, selected_subtype)

        except Exception as e:
            st.error(f"Error in summary generation: {e}")