from airflow import DAG
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
from airflow.decorators import task
from airflow.models import Variable
from airflow.operators.dagrun_operator import TriggerDagRunOperator

# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'me',
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id="download-files",
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval="@daily"
) as dag:

    @task(task_id="download_files")
    def download_files(ti=None):
        import os
        import asyncio
        from consume_api import coordinator

        # API URL
        ENDPOINT = os.environ["API_URL"] + "/data"

        # For the first run, call the API with start="beginning"
        timestamp = Variable.get(key="timestamp", default_var="beginning")

        print(f"Calling API with argument start={timestamp}")
        # next_timestamp is None when API responds with no data
        next_timestamp = asyncio.run(
            coordinator(url=ENDPOINT,
                        params={'start': timestamp}))

        # If there was data returned from API, update the Airflow variable
        if next_timestamp:
            Variable.set(key="timestamp", value=next_timestamp,
                description="Timestamp to be used the next time this DAG runs")
        # Push either a timestamp or "None" to XComs, to decide if the
        # upload-files DAG should be triggered or not
        print(f"Pushing '{next_timestamp}' to XComs")
        ti.xcom_push(key="have_upload_data", value=f"{next_timestamp}")
    
    # Branching task. When the API responds with no data, then there's no need
    # to trigger the upload-files DAG
    @task.branch(task_id="branch_upload_task")
    def branch_func(ti=None):
        xcom_value = ti.xcom_pull(task_ids="download_files")
        if xcom_value != "None":
            return "trigger-upload-dag"
        else:
            return None # This means no downstream task should run

    trigger_op = TriggerDagRunOperator(task_id="trigger-upload-dag",
                                       trigger_dag_id="upload-files")
    branch_op = branch_func()
    download_files_op = download_files()

    download_files_op >> branch_op >> trigger_op