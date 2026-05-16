import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
import os

def classify_constraints(row):
    """Re-calculating constraints for the visualizer"""
    if row.get('is_plateau', 0) == 1 and row.get('avg_orders_per_month', 5) < 4:
        return 'SUPPLY_CONSTRAINED'
    elif row.get('is_growing', 0) == 1:
        return 'DEMAND_LIMITED'
    else:
        return 'GROWTH_STAGE'

def generate_report_visuals():
    print("🎨 Generating presentation visuals for the final report...")
    os.makedirs("outputs/visuals", exist_ok=True)
    
    try:
        preds = pd.read_csv("outputs/teamname_predictions.csv") # UPDATE TO YOUR REAL CSV NAME IF YOU CHANGED IT
        coords = pd.read_parquet("data/silver/cleaned/coordinates_clean.parquet")
        features = pd.read_parquet("data/gold/final_feature_matrix.parquet")
        
        # Calculate the constraint types on the fly!
        features['constraint_type'] = features.apply(classify_constraints, axis=1)
        
        # Merge them all for visualization
        df = preds.merge(coords, on='Outlet_ID', how='left')
        df = df.merge(features[['Outlet_ID', 'Outlet_Type', 'constraint_type', 'max_observed_volume']], on='Outlet_ID', how='left')
        
    except Exception as e:
        print(f"❌ Error loading data for visuals: {e}")
        return

    # ── 1. The Geographic Heatmap ──
    print("   -> Generating Geographic Heatmap...")
    m = folium.Map(location=[7.8731, 80.7718], zoom_start=8, tiles='CartoDB positron')
    
    map_data = df.dropna(subset=['Latitude', 'Longitude', 'Maximum_Monthly_Liters'])
    heat_data = list(zip(map_data['Latitude'], map_data['Longitude'], map_data['Maximum_Monthly_Liters']))
    
    HeatMap(heat_data, radius=12, blur=15, max_zoom=1).add_to(m)
    m.save('outputs/visuals/latent_demand_heatmap.html')
    print("      (Tip: Open the HTML file in your browser and take a screenshot for your PDF!)")

    # ── 2. Constraint Breakdown Bar Chart ──
    print("   -> Generating Constraint Analysis Chart...")
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")
    
    ax = sns.countplot(data=df, x='constraint_type', palette='viridis', order=['SUPPLY_CONSTRAINED', 'DEMAND_LIMITED', 'GROWTH_STAGE'])
    plt.title('Outlet Constraint Signatures (Why aren\'t they selling more?)', fontsize=14, fontweight='bold')
    plt.xlabel('Constraint Classification', fontsize=12)
    plt.ylabel('Number of Outlets', fontsize=12)
    
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='bottom', fontsize=11, color='black', xytext=(0, 5),
                    textcoords='offset points')
        
    plt.tight_layout()
    plt.savefig('outputs/visuals/constraint_breakdown.png', dpi=300)
    
    print("\n✅ Visuals generated successfully in 'outputs/visuals/'!")

if __name__ == "__main__":
    generate_report_visuals()