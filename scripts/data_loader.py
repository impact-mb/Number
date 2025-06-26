import pandas as pd

def load_data(file):
    return pd.read_excel(file, sheet_name=0)

class DataAnalyzer:
    def __init__(self, df):
        self.df = df
        self.duplicate_count = 0

    def remove_duplicates(self):
        if all(col in self.df.columns for col in ['DistrictName', 'ProgramSubType', 'ChildId']):
            self.df['unique_id'] = (
                self.df['DistrictName'].astype(str) + '_' +
                self.df['ProgramSubType'].astype(str) + '_' +
                self.df['ChildId'].astype(str)
            )
            duplicates = self.df.duplicated(subset='unique_id')
            self.duplicate_count = duplicates.sum()
            self.df = self.df[~duplicates].drop(columns='unique_id')
        return self.df