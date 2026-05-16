# clean_pipeline.py
import pandas as pd
import os
from dq_checks import *

def run_silver_pipeline():
    print("🥈 Starting Silver Layer Cleaning Pipeline...\n")
    
    # Ensure the save directories exist so the script doesn't crash
    os.makedirs("data/silver/cleaned", exist_ok=True)
    
    # ── Load Bronze ──
    try:
        transactions = pd.read_parquet("data/bronze/transactions_history_final.parquet")
        outlets      = pd.read_parquet("data/bronze/outlet_master.parquet")
        coords       = pd.read_parquet("data/bronze/outlet_coordinates.parquet")
        seasonality  = pd.read_parquet("data/bronze/distributor_seasonality_details.parquet")
        holidays     = pd.read_parquet("data/bronze/holiday_list.parquet")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}. Did you run the Bronze ingestion first?")
        return

    # ── TRANSACTIONS ──
    print("\n--- Cleaning Transactions ---")
    t, r = check_duplicates(transactions, ['Outlet_ID', 'Year', 'Month', 'SKU_ID'], 'transactions')
    t, r = check_nulls(t, ['Outlet_ID', 'Year', 'Month', 'SKU_ID', 'Volume_Liters'], 'transactions')
    t, r = check_value_range(t, 'Volume_Liters', 0.001, 100000, 'transactions')
    t, r = check_value_range(t, 'Year', 2000, 2025, 'transactions')
    t, r = check_value_range(t, 'Month', 1, 12, 'transactions')
    t, r = check_referential_integrity(t, 'Outlet_ID', outlets, 'Outlet_ID', 'transactions')
    t.to_parquet("data/silver/cleaned/transactions_clean.parquet", index=False)
    
    # ── OUTLETS ──
    print("\n--- Cleaning Outlets ---")
    o, r = check_duplicates(outlets, ['Outlet_ID'], 'outlet_master')
    o, r = check_nulls(o, ['Outlet_ID', 'Outlet_Size', 'Cooler_Count', 'Outlet_Type'], 'outlet_master')
    o.to_parquet("data/silver/cleaned/outlet_master_clean.parquet", index=False)

    # ── COORDINATES ──
    print("\n--- Cleaning Coordinates ---")
    c, r = check_duplicates(coords, ['Outlet_ID'], 'coordinates')
    c, r = check_coordinates(c, 'Latitude', 'Longitude', 'coordinates')
    c, r = check_referential_integrity(c, 'Outlet_ID', outlets, 'Outlet_ID', 'coordinates')
    c.to_parquet("data/silver/cleaned/coordinates_clean.parquet", index=False)

    # ── SEASONALITY ──
    print("\n--- Cleaning Seasonality ---")
    # Make sure the columns match your Kaggle dataset. I used Seasonality_Factor for both here to be safe!
    s, r = check_duplicates(seasonality, ['Distributor_ID', 'Year', 'Month'], 'seasonality')
    s, r = check_value_range(s, 'Seasonality_Factor', 0.1, 5.0, 'seasonality')
    s.to_parquet("data/silver/cleaned/seasonality_clean.parquet", index=False)

    # ── HOLIDAYS ──
    print("\n--- Cleaning Holidays ---")
    h, r = check_duplicates(holidays, ['Date', 'Holiday_Name', 'Holiday_Type'], 'holidays')
    h, r = check_date_format(h, 'Date', 'holidays')
    h.to_parquet("data/silver/cleaned/holidays_clean.parquet", index=False)

    # ── SAVE REJECTION LOG ──
    save_rejection_log()
    print("\n✅ Silver layer complete. Pristine data is ready for the Gold layer.")

if __name__ == "__main__":
    run_silver_pipeline()