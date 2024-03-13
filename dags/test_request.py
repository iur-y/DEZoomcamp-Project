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
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="test-request-to-api",
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval="@daily"
) as dag:

    @task(task_id="make_request")
    def make_request(*, ip="host.docker.internal", port="5000"):
        import requests
        url = f"http://{ip}:{port}"
        print(f"Making request to {url}")
        r = requests.get(url)
        print(r.text)
        return 1

    task1 = make_request()