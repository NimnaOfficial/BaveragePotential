# feature_engineering.py - Auto-generated
import pandas as pd
import numpy as np
from scipy import stats
import os

def build_transaction_features(transactions):
    print("   -> Calculating volume trends and consistency...")
    
    # 1. Handle the split Year/Month columns we discovered in the Silver layer
    transactions['YearMonth'] = pd.to_datetime(transactions[['Year', 'Month']].assign(DAY=1)).dt.to_period('M')
    
    # 2. Monthly aggregations per outlet
    monthly = (transactions
               .groupby(['Outlet_ID', 'YearMonth'])['Volume_Liters']
               .sum()
               .reset_index())
    
    features = monthly.groupby('Outlet_ID')['Volume_Liters'].agg(
        mean_monthly_volume     = 'mean',
        median_monthly_volume   = 'median',
        max_observed_volume     = 'max',       
        std_monthly_volume      = 'std',
        total_active_months     = 'count'
    ).reset_index()
    
    # Fill NaN standard deviations (happens if an outlet only has 1 month of data)
    features['std_monthly_volume'] = features['std_monthly_volume'].fillna(0)
    
    # 3. Volume trend (slope of linear regression on monthly volumes)
    def compute_slope(volumes):
        if len(volumes) < 3:
            return 0
        x = np.arange(len(volumes))
        slope, _, _, _, _ = stats.linregress(x, volumes)
        return slope
    
    trend = (monthly.groupby('Outlet_ID')['Volume_Liters']
             .apply(compute_slope)
             .reset_index()
             .rename(columns={'Volume_Liters': 'volume_trend_slope'}))
    
    features = features.merge(trend, on='Outlet_ID', how='left')
    
    # 4. Consistency Score (Coefficient of Variation)
    features['cv_score'] = features['std_monthly_volume'] / (features['mean_monthly_volume'] + 1)
    
    # 5. Plateau indicator: If volume barely changes (cv < 0.1), it's likely supply-constrained
    features['is_plateau'] = (features['cv_score'] < 0.1).astype(int)
    
    # 6. Growth indicator
    features['is_growing'] = (features['volume_trend_slope'] > 0).astype(int)
    
    return features

def build_constraint_features(transactions):
    print("   -> Building supply constraint indicators...")
    transactions['YearMonth'] = pd.to_datetime(transactions[['Year', 'Month']].assign(DAY=1)).dt.to_period('M')
    
    # Order frequency per month (how many separate rows/SKUs they buy)
    order_freq = (transactions
                  .groupby(['Outlet_ID', 'YearMonth'])
                  .size()
                  .reset_index(name='orders_per_month'))
    
    avg_order_freq = (order_freq.groupby('Outlet_ID')['orders_per_month']
                     .mean()
                     .reset_index()
                     .rename(columns={'orders_per_month': 'avg_orders_per_month'}))
    
    # Average order size
    avg_order_size = (transactions
                      .groupby('Outlet_ID')['Volume_Liters']
                      .mean()
                      .reset_index()
                      .rename(columns={'Volume_Liters': 'avg_order_size_liters'}))
    
    constraint_features = avg_order_freq.merge(avg_order_size, on='Outlet_ID', how='left')
    return constraint_features

def run_gold_pipeline():
    print("🥇 Starting Gold Layer Feature Engineering...\n")
    
    # ── 1. Load Silver Data ──
    try:
        transactions = pd.read_parquet("data/silver/cleaned/transactions_clean.parquet")
        outlets      = pd.read_parquet("data/silver/cleaned/outlet_master_clean.parquet")
        # Handle the seasonality column dynamically regardless of what it's named
        seasonality  = pd.read_parquet("data/silver/cleaned/seasonality_clean.parquet")
        holidays     = pd.read_parquet("data/silver/cleaned/holidays_clean.parquet")
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find clean data. {e}")
        return

    # ── 2. Build Features ──
    txn_features = build_transaction_features(transactions)
    constraint_features = build_constraint_features(transactions)
    
    # ── 3. Merge Base Matrix ──
    print("   -> Merging final feature matrix...")
    feature_matrix = outlets.merge(txn_features, on='Outlet_ID', how='left')
    feature_matrix = feature_matrix.merge(constraint_features, on='Outlet_ID', how='left')
    
    # ── 4. Map Outlets to Distributors using Transactions ──
    print("   -> Mapping outlets to their respective Distributor IDs from transactions...")
    outlet_dist_map = transactions[['Outlet_ID', 'Distributor_ID']].drop_duplicates()
    feature_matrix = feature_matrix.merge(outlet_dist_map, on='Outlet_ID', how='left')
    
    # ── 5. Apply January Seasonality using the correct index column name ──
    print("   -> Merging January seasonality indexes...")
    jan_seasonality = seasonality[seasonality['Month'] == 1][['Distributor_ID', 'Seasonality_Index']]
    jan_seasonality = jan_seasonality.rename(columns={'Seasonality_Index': 'jan_seasonality_factor'})
    
    feature_matrix = feature_matrix.merge(jan_seasonality, on='Distributor_ID', how='left')
    
    # ── 5. Conditional POI Merge (In case your mate isn't done yet) ──
    poi_path = "data/gold/poi_features.parquet"
    if os.path.exists(poi_path):
        print("   -> 📍 POI Data found! Merging geographic features...")
        poi = pd.read_parquet(poi_path)
        feature_matrix = feature_matrix.merge(poi, on='Outlet_ID', how='left')
    else:
        print("   -> ⚠️ POI Data not found yet. Skipping POI merge for now.")

    # ── 6. Save Gold Matrix ──
    feature_matrix.to_parquet("data/gold/final_feature_matrix.parquet", index=False)
    print(f"\n✅ Gold layer complete! Generated {feature_matrix.shape[1]} features for {feature_matrix.shape[0]} outlets.")

if __name__ == "__main__":
    run_gold_pipeline()