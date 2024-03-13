from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
from airflow.decorators import task

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'me',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id="first-try-at-downloading-files",
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval="@daily"
) as dag:

    @task(task_id="download_files")
    def download_files():
        import consume_api

    task1 = download_files()