# dq_checks.py
import pandas as pd
import numpy as np

# A global list to hold all our bad data from every table
rejection_log_data = []

def log_rejections(bad_df, reason, table_name):
    """Helper function to add bad rows to our master rejection log."""
    if not bad_df.empty:
        # Create a small summary for the log
        log_entry = pd.DataFrame({
            'Table': table_name,
            'Reason': reason,
            'Rejected_Row_Count': len(bad_df)
        }, index=[0])
        rejection_log_data.append(log_entry)
        print(f"  ⚠️ {len(bad_df)} rows rejected: {reason}")

def check_duplicates(df, subset, table_name):
    bad_df = df[df.duplicated(subset=subset, keep='first')]
    good_df = df.drop_duplicates(subset=subset, keep='first')
    log_rejections(bad_df, f"Duplicate keys in {subset}", table_name)
    return good_df, bad_df

def check_nulls(df, columns, table_name):
    bad_df = df[df[columns].isnull().any(axis=1)]
    good_df = df.dropna(subset=columns)
    log_rejections(bad_df, f"Null values found in {columns}", table_name)
    return good_df, bad_df

def check_value_range(df, column, min_val, max_val, table_name):
    # If the column doesn't exist, just return the df safely
    if column not in df.columns:
        print(f"  ℹ️ Column {column} not found in {table_name}, skipping range check.")
        return df, pd.DataFrame()
        
    bad_df = df[(df[column] < min_val) | (df[column] > max_val)]
    good_df = df[(df[column] >= min_val) & (df[column] <= max_val)]
    log_rejections(bad_df, f"{column} out of bounds ({min_val} to {max_val})", table_name)
    return good_df, bad_df

def check_referential_integrity(df, col, ref_df, ref_col, table_name):
    # Ensure IDs in 'df' actually exist in the reference table 'ref_df'
    valid_ids = ref_df[ref_col].unique()
    bad_df = df[~df[col].isin(valid_ids)]
    good_df = df[df[col].isin(valid_ids)]
    log_rejections(bad_df, f"Invalid {col} - Not found in master list", table_name)
    return good_df, bad_df

def check_coordinates(df, lat_col, lon_col, table_name):
    # Sri Lanka roughly falls between Lat: 5.9 to 9.9 and Lon: 79.5 to 81.9
    bad_lat = (df[lat_col] < 5.0) | (df[lat_col] > 10.0)
    bad_lon = (df[lon_col] < 79.0) | (df[lon_col] > 82.0)
    
    bad_df = df[bad_lat | bad_lon]
    good_df = df[~(bad_lat | bad_lon)]
    log_rejections(bad_df, "Coordinates out of Sri Lanka range", table_name)
    return good_df, bad_df

def check_date_format(df, col, table_name):
    # Try to convert to datetime. If it fails, it turns into 'NaT' (Not a Time)
    temp_dates = pd.to_datetime(df[col], errors='coerce')
    bad_df = df[temp_dates.isnull()]
    good_df = df[~temp_dates.isnull()]
    log_rejections(bad_df, f"Invalid date format in {col}", table_name)
    return good_df, bad_df

def save_rejection_log():
    """Saves the summary of all bad data to a CSV."""
    if rejection_log_data:
        final_log = pd.concat(rejection_log_data, ignore_index=True)
        final_log.to_csv("rejection_log_summary.csv", index=False)
        print(f"\n📝 Rejection log saved to 'rejection_log_summary.csv' with {len(final_log)} rules triggered.")
    else:
        print("\n📝 No errors found! Rejection log is empty.")