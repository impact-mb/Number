import pandas as pd
import numpy as np

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.df = self._remove_duplicates()

    def _remove_duplicates(self):
        if all(col in self.df.columns for col in ['DistrictName', 'ProgramSubType', 'ChildId']):
            self.df['unique_id'] = self.df['DistrictName'].astype(str) + '_' + \
                                   self.df['ProgramSubType'].astype(str) + '_' + \
                                   self.df['ChildId'].astype(str)
            self.df['dup_tag'] = self.df.duplicated(subset='unique_id', keep='first')
            self.duplicate_count = self.df['dup_tag'].sum()
            print(f"Number of duplicate records based on DistrictName, ProgramSubType, and ChildId: {self.duplicate_count}")
            return self.df[~self.df['dup_tag']].copy()
        self.duplicate_count = 0
        return self.df

    def get_summary_stats(self):
        return {
            'Total Rows': len(self.df),
            'Total Columns': len(self.df.columns),
            'Missing Values': self.df.isnull().sum().sum(),
            'Duplicate Rows': self.df.duplicated().sum(),
            'Memory Usage (MB)': round(self.df.memory_usage(deep=True).sum() / 1024**2, 2)
        }

    def get_key_metrics(self):
        return {
            'Unique Districts': self.df['DistrictName'].nunique() if 'DistrictName' in self.df.columns else 'N/A',
            'Program Types': self.df['ProgramSubType'].value_counts().to_dict() if 'ProgramSubType' in self.df.columns else {},
            'Unique Group IDs': self.df['GroupId'].nunique() if 'GroupId' in self.df.columns else 'N/A'
        }

    def gender_distribution_by_district(self):
        if 'Gender' in self.df.columns and 'DistrictName' in self.df.columns:
            gender_df = self.df[self.df['Gender'].isin(['Male', 'Female'])]
            return gender_df.groupby(['DistrictName', 'Gender']).size().reset_index(name='Count')
        return pd.DataFrame()

    def session_category_distribution(self):
        if 'RegularSessions' in self.df.columns and 'DistrictName' in self.df.columns:
            df = self.df.copy()
            df['SessionCategory'] = df['RegularSessions'].apply(lambda x:
                '0' if pd.isna(x) or x == 0 else
                '1-2' if x <= 2 else
                '3+')
            summary = df.groupby(['DistrictName', 'SessionCategory']).size().reset_index(name='Count')
            return summary
        return pd.DataFrame()