from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.main import run_pipeline

with DAG(
    "data_migration_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    run = PythonOperator(
        task_id="run_pipeline",
        python_callable=run_pipeline
    )
