# poi_engine.py
import requests
import pandas as pd

def fetch_osm_pois(amenity_type, timeout=120):
    print(f"🗺 Querying OpenStreetMap for: {amenity_type}...")
    
    # Using the primary reliable mirror
    overpass_url = "https://overpass.kumi.systems/api/interpreter"
    
    # OPTIMIZED QUERY: We ask for only nodes (exact points) to speed up server processing drastically
    query = f"""
    [out:json][timeout:{timeout}];
    node["amenity"="{amenity_type}"](5.9,79.5,9.9,81.9);
    out;
    """
    
    headers = {
        'User-Agent': 'DataStorm7_FastPipeline_Bot/2.0 (nima_dev@example.com)',
        'Accept-Encoding': 'gzip, deflate'
    }
    
    try:
        response = requests.post(overpass_url, data={'data': query}, headers=headers, timeout=timeout)
        
        if response.status_code != 200:
            print(f"⚠️ Main server busy (Status {response.status_code}). Trying backup engine...")
            response = requests.post("https://overpass-api.de/api/interpreter", data={'data': query}, headers=headers, timeout=timeout)

        data = response.json()
        elements = data.get('elements', [])
        
        poi_list = []
        for element in elements:
            lat = element.get('lat')
            lon = element.get('lon')
            tags = element.get('tags', {})
            name = tags.get('name', f"Unnamed {amenity_type}")
            
            if lat and lon:
                poi_list.append({
                    'POI_Name': name,
                    'POI_Type': amenity_type,
                    'Latitude': lat,
                    'Longitude': lon
                })
                
        df = pd.DataFrame(poi_list)
        print(f"✅ Successfully extracted {len(df)} locations for {amenity_type}!")
        return df
        
    except Exception as e:
        print(f"❌ Server timeout or error for {amenity_type}. It's busy right now.")
        return pd.DataFrame()