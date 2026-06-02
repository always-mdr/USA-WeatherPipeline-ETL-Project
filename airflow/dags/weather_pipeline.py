import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

from scripts.extract_weather import run_extraction
from scripts.load_to_iceberg import setup_and_load_iceberg

# Set PyIceberg environment variables dynamically to use absolute paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
os.environ['PYICEBERG_CATALOG__DEFAULT__URI'] = f"sqlite:///{PROJECT_ROOT}/pyiceberg_catalog.db"
os.environ['PYICEBERG_CATALOG__DEFAULT__WAREHOUSE'] = f"file://{PROJECT_ROOT}/data/iceberg_warehouse"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'weather_lakehouse_pipeline',
    default_args=default_args,
    description='A simple data pipeline for extracting weather data and loading into Iceberg, followed by dbt.',
    schedule=timedelta(days=1),
    catchup=False,
) as dag:

    def extract_task(**kwargs):
        output_dir = os.path.join(PROJECT_ROOT, 'data', 'raw')
        parquet_path = run_extraction(output_dir=output_dir)
        # Pass the path to the next task
        kwargs['ti'].xcom_push(key='parquet_path', value=parquet_path)
        print(f"Extraction successful: {parquet_path}")

    def load_iceberg_task(**kwargs):
        ti = kwargs['ti']
        parquet_path = ti.xcom_pull(task_ids='extract_weather_data', key='parquet_path')
        print(f"Loading {parquet_path} to Iceberg...")
        setup_and_load_iceberg(parquet_path)

    extract_op = PythonOperator(
        task_id='extract_weather_data',
        python_callable=extract_task
    )

    load_iceberg_op = PythonOperator(
        task_id='load_to_iceberg',
        python_callable=load_iceberg_task
    )

    # Note: We need to point dbt to the right profiles directory
    # We will create the dbt project in dbt_weather
    dbt_run_op = BashOperator(
        task_id='dbt_run',
        bash_command=f"cd {PROJECT_ROOT}/dbt_weather && ../venv/bin/dbt run --profiles-dir .",
    )

    extract_op >> load_iceberg_op >> dbt_run_op
