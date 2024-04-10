from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash import BashOperator

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'me',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# This DAG is triggered by dag_consume.py, not through a schedule
with DAG(
    dag_id="upload-files",
    default_args=default_args,
) as dag:
    # upload the local files, the bucket name changes after pre-init.sh runs
    # dst (destination) is like dt=2024-04-21, which creates something like:
    # gs://raw_parquet_data_zoomcamp_project/dt=2024-04-21/isodate.parquet
    # this "folder-like" structure is required for BigQuery partitioning
    upload = LocalFilesystemToGCSOperator(
        task_id="upload_parquet_to_gcs",
        src="./*.parquet",
        bucket="raw_parquet_data_zoomcamp_project",
        dst='{{macros.datetime.strptime(ds, "%Y-%m-%d").strftime("dt=%Y-%m-%d/")}}'
    )
    # Delete local files if they were uploaded to GCS
    delete = BashOperator(
        task_id="delete_parquet_files",
        bash_command="echo deleting $(ls *.parquet); rm *.parquet",
        cwd="/opt/airflow/")

    upload >> delete
