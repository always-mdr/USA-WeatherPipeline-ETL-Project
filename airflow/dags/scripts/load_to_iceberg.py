import os
import pyarrow.parquet as pq
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    TimestampType,
    StringType,
    DoubleType,
    NestedField,
)

def setup_and_load_iceberg(parquet_path):
    """Create Iceberg table if not exists and load data."""
    # Ensure warehouse directory exists
    os.makedirs(os.path.abspath("data/iceberg_warehouse"), exist_ok=True)
    
    # Load the local sqlite catalog configuration
    # PyIceberg automatically reads .pyiceberg.yaml or env vars
    catalog = load_catalog("default")
    
    # Create namespace if it doesn't exist
    try:
        catalog.create_namespace("weather")
        print("Created namespace 'weather'")
    except Exception as e:
        print(f"Namespace might already exist: {e}")
        
    # Define schema matching our pandas output
    schema = Schema(
        NestedField(field_id=1, name="date", field_type=TimestampType(), required=False),
        NestedField(field_id=2, name="city", field_type=StringType(), required=False),
        NestedField(field_id=3, name="temp_max_c", field_type=DoubleType(), required=False),
        NestedField(field_id=4, name="temp_min_c", field_type=DoubleType(), required=False),
        NestedField(field_id=5, name="precipitation_mm", field_type=DoubleType(), required=False),
        NestedField(field_id=6, name="wind_speed_max_kmh", field_type=DoubleType(), required=False)
    )
    
    table_name = "weather.historical"
    try:
        table = catalog.load_table(table_name)
        print(f"Table {table_name} found.")
    except Exception:
        # Create table if it doesn't exist
        print(f"Table {table_name} not found. Creating it.")
        table = catalog.create_table(
            table_name,
            schema=schema
        )
    
    # Load the parquet file
    print(f"Reading {parquet_path}...")
    df = pq.read_table(parquet_path)
    
    # Append to Iceberg table
    print("Appending data to Iceberg table...")
    table.append(df)
    print("Data successfully loaded to Iceberg.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        setup_and_load_iceberg(sys.argv[1])
    else:
        print("Please provide the parquet file path.")
