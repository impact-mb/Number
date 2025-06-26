import pandas as pd
import re

def load_asp_file(file):
    try:
        df = pd.read_excel(file)
        df.columns = df.columns.str.strip().str.replace("\n", " ", regex=True)

        # Find session column
        session_upto_col = next((col for col in df.columns if re.search(r'sessions planned up to', col, re.IGNORECASE)), None)
        session_during_col = next((col for col in df.columns if re.search(r'sessions planned during', col, re.IGNORECASE)), None)

        # Fuzzy column remapping
        column_mapping = {}
        for col in df.columns:
            if 'programlaunch' in col.lower():
                column_mapping[col] = 'ProgramLaunchName'
            elif 'funder' in col.lower():
                column_mapping[col] = 'FunderName'
            elif 'grade' in col.lower():
                column_mapping[col] = 'Grade'
            elif 'subtype' in col.lower():
                column_mapping[col] = 'ProgrameSubType'

        df = df.rename(columns=column_mapping)

        required_cols = ['ProgramLaunchName', 'FunderName', 'Grade', 'ProgrameSubType']
        if session_upto_col:
            df = df.rename(columns={session_upto_col: 'SessionsPlannedUpto'})
        if session_during_col:
            df = df.rename(columns={session_during_col: 'SessionsPlannedDuring'})

        if all(col in df.columns for col in required_cols + ['SessionsPlannedUpto']):
            return df[required_cols + ['SessionsPlannedUpto', 'SessionsPlannedDuring'] if 'SessionsPlannedDuring' in df.columns else required_cols + ['SessionsPlannedUpto']]
        else:
            return None

    except Exception as e:
        print(f"Error loading ASP file: {e}")
        return None