# USA Weather Analysis Data Engineering Pipeline

An end-to-end modern data stack pipeline extracting historical weather data for 15 major US cities, leveraging Apache Airflow, Apache Iceberg (PyIceberg), DuckDB, dbt, and Streamlit.

## Features
- **Data Extraction**: Pulls historical daily weather data from the [Open-Meteo API](https://open-meteo.com/).
- **Data Lakehouse**: Loads the raw parquet files into an **Apache Iceberg** table format using a local SQLite catalog and PyIceberg.
- **Transformations**: Transforms the raw data into monthly aggregates using **DuckDB**. (Initially configured with `dbt-duckdb`, currently bypassing dbt to use DuckDB Iceberg Extension natively due to a Python 3.14 conflict with `mashumaro`).
- **Orchestration**: Managed locally with **Apache Airflow**.
- **Dashboard**: Interactive visualizations built with **Streamlit** and Plotly.

## Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/always-mdr/USA-WeatherPipeline-ETL-Project.git
   cd USA-WeatherPipeline-ETL-Project
   ```

2. **Initialize the Environment:**
   ```bash
   make setup
   ```

3. **Run the Data Pipeline (Extraction & Load):**
   ```bash
   # Make sure Airflow is initialized or run scripts manually:
   ./venv/bin/python airflow/dags/scripts/extract_weather.py
   
   # Load to Iceberg (ensure absolute paths are used for environment variables)
   export PYICEBERG_CATALOG__DEFAULT__URI="sqlite:///$(pwd)/pyiceberg_catalog.db"
   export PYICEBERG_CATALOG__DEFAULT__WAREHOUSE="file://$(pwd)/data/iceberg_warehouse"
   ./venv/bin/python airflow/dags/scripts/load_to_iceberg.py data/raw/<parquet_file_name>
   ```

4. **Launch the Dashboard:**
   ```bash
   ./venv/bin/streamlit run dashboard/app.py
   ```
