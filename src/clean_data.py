import pandas as pd
import os

def clean_sales_data():
    print("🚀 Starting the Bronze-to-Silver Data Pipeline...")

    # 1. DEFINE OUR FOLDER PATHS (Fixed to match your actual folder structure!)
    bronze_folder = 'data/bronze'
    silver_folder = 'data/silver/cleaned'
    
    # We also need a place for the rejection log
    rejected_folder = 'data/silver/rejected'
    
    raw_file_path = f'{bronze_folder}/transactions_history_final.csv' 
    
    # Check if the raw file actually exists before we start
    if not os.path.exists(raw_file_path):
        print(f"❌ ERROR: I cannot find the CSV file at {raw_file_path}")
        print("Did you put it in the Bronze folder and name it correctly?")
        return

    # 2. LOAD THE RAW DATA (The Bronze Layer)
    print("📥 Loading raw CSV data...")
    df = pd.read_csv(raw_file_path)
    print("Columns in this CSV are:", df.columns.tolist())
    
    # 3. DATA QUALITY (DQ) CHECKS
    print("🧹 Running Data Quality filters...")
    
    bad_data_condition = (
        df['Volume_Liters'].isnull() |    # Rule A: Volume is completely blank
        (df['Volume_Liters'] < 0) |       # Rule B: Volume numbers are physically impossible
        df['Outlet_ID'].isnull()          # Rule C: We don't know which shop this is
    )

    # 4. SPLIT THE DATA
    bad_data = df[bad_data_condition].copy()
    good_data = df[~bad_data_condition].copy() 

    # 5. SAVE THE BAD DATA
    print(f"⚠️ Found {len(bad_data)} rows with errors. Saving to rejection log...")
    bad_data.to_csv(f'{rejected_folder}/rejection_log.csv', index=False)

    # 6. SAVE THE GOOD DATA
    print(f"✨ Found {len(good_data)} clean rows. Saving to Silver layer as Parquet...")
    silver_file_path = f'{silver_folder}/clean_sales_data.parquet'
    good_data.to_parquet(silver_file_path, index=False)

    print("✅ Pipeline Complete! The Silver data is ready for the Gold layer.")

if __name__ == "__main__":
    clean_sales_data()