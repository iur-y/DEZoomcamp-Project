from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow import DAG
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago

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
    task1 = LocalFilesystemToGCSOperator(
        src="./*.parquet",
        bucket="raw_parquet_data_zoomcamp_project",
        dst="/2024/03/13/" # just missing to figure out how to pass the connection, I think copy creds file to airflow container and export GOOGLE_APPLICATION_CREDENTIALS
    )