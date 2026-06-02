import os
import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timedelta

# Constants
CITIES = {
    'NYC': {'lat': 40.7128, 'lon': -74.0060},
    'LA': {'lat': 34.0522, 'lon': -118.2437},
    'SFO': {'lat': 37.7749, 'lon': -122.4194},
    'CHICAGO': {'lat': 41.8781, 'lon': -87.6298},
    'DALLAS': {'lat': 32.7767, 'lon': -96.7970},
    'ATLANTA': {'lat': 33.7490, 'lon': -84.3880},
    'MIAMI': {'lat': 25.7617, 'lon': -80.1918},
    'NASHVILLE': {'lat': 36.1627, 'lon': -86.7816},
    'MEMPHIS': {'lat': 35.1495, 'lon': -90.0490},
    'AUSTIN': {'lat': 30.2672, 'lon': -97.7431},
    'SAN_ANTONIO': {'lat': 29.4241, 'lon': -98.4936},
    'PHOENIX': {'lat': 33.4484, 'lon': -112.0740},
    'SEATTLE': {'lat': 47.6062, 'lon': -122.3321},
    'WASHINGTON_DC': {'lat': 38.9072, 'lon': -77.0369},
    'BOSTON': {'lat': 42.3601, 'lon': -71.0589}
}

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"

def extract_city_data(city_name, lat, lon, start_date, end_date):
    """Fetch historical weather data for a single city."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "wind_speed_10m_max"],
        "timezone": "auto"
    }
    
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    
    daily = data.get('daily', {})
    if not daily:
        return pd.DataFrame()
        
    df = pd.DataFrame({
        'date': pd.to_datetime(daily['time']),
        'city': city_name,
        'temp_max_c': daily.get('temperature_2m_max', []),
        'temp_min_c': daily.get('temperature_2m_min', []),
        'precipitation_mm': daily.get('precipitation_sum', []),
        'wind_speed_max_kmh': daily.get('wind_speed_10m_max', [])
    })
    return df

def run_extraction(output_dir='data/raw'):
    """Extract data for all cities and save to Parquet."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate dates (past 1 year up to yesterday for faster demo)
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"Extracting data from {start_date} to {end_date}...")
    
    all_data = []
    for city, coords in CITIES.items():
        print(f"Fetching data for {city}...")
        df = extract_city_data(city, coords['lat'], coords['lon'], start_date, end_date)
        all_data.append(df)
        
    # Combine all cities
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Save to Parquet
    output_path = os.path.join(output_dir, f"weather_extract_{end_date}.parquet")
    table = pa.Table.from_pandas(final_df)
    pq.write_table(table, output_path)
    print(f"Extraction complete. Data saved to {output_path}")
    
    return output_path

if __name__ == "__main__":
    # For testing independently
    run_extraction()
