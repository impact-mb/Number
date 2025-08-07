import pandas as pd

def load_data(file):
    """Load Excel file (sheet 0) into DataFrame."""
    return pd.read_excel(file, sheet_name=0)

def load_generic_file(file):
    """Auto-detect file type and load it (CSV or Excel)."""
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file, sheet_name=0)
    else:
        return pd.DataFrame()  # Return empty DataFrame for unsupported files

class DataAnalyzer:
    """Handles duplicate removal and data checks."""

    def __init__(self, df):
        self.df = df
        self.duplicate_count = 0

    def remove_duplicates(self):
        """Remove duplicates based on DistrictName + ProgramSubType + ChildId."""
        required_cols = ['DistrictName', 'ProgramSubType', 'ChildId']
        if all(col in self.df.columns for col in required_cols):
            self.df['unique_id'] = (
                self.df['DistrictName'].astype(str) + '_' +
                self.df['ProgramSubType'].astype(str) + '_' +
                self.df['ChildId'].astype(str)
            )
            duplicates = self.df.duplicated(subset='unique_id')
            self.duplicate_count = duplicates.sum()
            self.df = self.df[~duplicates].drop(columns='unique_id')
        return self.df