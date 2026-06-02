.PHONY: setup airflow-init dbt-init clean

setup:
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	mkdir -p data/raw data/iceberg_warehouse dbt_weather airflow/dags

airflow-init:
	export AIRFLOW_HOME=$$(pwd)/airflow && \
	./venv/bin/airflow db migrate

dbt-init:
	# We will manually create the dbt profiles and project files

clean:
	rm -rf venv data airflow dbt_weather *.duckdb .iceberg*
