import os

# Define the folders
folders = [
    "data/bronze",
    "data/silver/cleaned",
    "data/silver/rejected",
    "data/gold",
    "data/poi_cache",
    "src/bronze",
    "src/silver",
    "src/gold",
    "src/modeling",
    "notebooks",
    "outputs",
    "report"
]

# Define the starter files
files = [
    "src/bronze/ingest.py",
    "src/silver/dq_checks.py",
    "src/silver/clean_pipeline.py",
    "src/gold/poi_scraper.py",
    "src/gold/feature_engineering.py",
    "src/modeling/potential_model.py",
    "notebooks/01_EDA.ipynb",
    "README.md",
    "requirements.txt"
]

print("🌩️ Initializing Data Storm 7.0 Workspace...")

# Create directories
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"📁 Created folder: {folder}")

# Create blank files
for file in files:
    if not os.path.exists(file):
        with open(file, 'w') as f:
            # Add a quick comment so the file isn't entirely empty
            f.write(f"# {file.split('/')[-1]} - Auto-generated\n")
        print(f"📄 Created file: {file}")

print("\n✅ Workspace built! Move your raw CSVs into 'data/bronze/' and you are ready to code.")