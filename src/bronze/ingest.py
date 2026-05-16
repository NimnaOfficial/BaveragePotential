# ingest.py - Auto-generated
import pandas as pd
import os

BRONZE_PATH = "data/bronze/"

def ingest_all():
    print("🌩️ Starting Data Storm Ingestion...\n")
    
    files = [
        "transactions_history_final.csv",
        "outlet_master.csv",
        "outlet_coordinates.csv",
        "distributor_seasonality_details.csv",
        "holiday_list.csv"
    ]
    
    for file in files:
        file_path = os.path.join(BRONZE_PATH, file)
        
        if not os.path.exists(file_path):
            print(f"⚠️ SKIPPED: {file} not found in {BRONZE_PATH}")
            continue
            
        # Read the raw CSV
        df = pd.read_csv(file_path)
        
        # Convert name from .csv to .parquet
        output_name = file.replace(".csv", ".parquet")
        output_path = os.path.join(BRONZE_PATH, output_name)
        
        # Save as Parquet file
        df.to_parquet(output_path, index=False)
        print(f"✅ Ingested {file} → {df.shape[0]:,} rows, {df.shape[1]} cols")
    
    print("\n🥉 Bronze layer complete. Parquet files are ready for cleaning.")

if __name__ == "__main__":
    ingest_all()