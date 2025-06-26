import streamlit as st
import pandas as pd

def generate_pivot_tables(df, subtype):
    if 'DistrictName' in df.columns and 'ChildId' in df.columns:
        pivot = (
            df.groupby('DistrictName')['ChildId'].nunique()
            .reset_index(name='Count of ChildId')
        )
        pivot.loc[len(pivot.index)] = ['Grand Total', pivot['Count of ChildId'].sum()]
        st.markdown("### 📋 ProgramSubType Summary Table")
        st.dataframe(pivot, use_container_width=True)

    if 'RegularSessions' in df.columns:
        def categorize(val):
            if subtype == 'CLC':
                if pd.isna(val) or val == 0: return '0'
                elif val <= 4: return '1-4'
                else: return '5 & above'
            else:
                if pd.isna(val) or val == 0: return 'Cat0'
                elif val in [1, 2]: return 'Cat1-2'
                else: return 'Cat3&above'

        df['SessionCategory'] = df['RegularSessions'].apply(categorize)
        cat_table = (
            df.groupby(['DistrictName', 'SessionCategory'])['ChildId']
            .nunique().reset_index()
            .pivot(index='DistrictName', columns='SessionCategory', values='ChildId')
            .fillna(0).astype(int)
        )
        cat_table.loc['Grand Total'] = cat_table.sum()
        st.markdown("### 🧮 RegularSessions Category-wise Summary Table")
        st.dataframe(cat_table, use_container_width=True)

    if 'SummerCampSessions' in df.columns:
        summer_table = (
            df.groupby('DistrictName')['SummerCampSessions']
            .sum().reset_index(name='Total SummerCampSessions')
        )
        st.markdown("### ☀️ SummerCampSessions - District wise")
        st.dataframe(summer_table, use_container_width=True)
