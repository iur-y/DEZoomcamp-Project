#!/bin/bash

# terminate1.sh: non interactively terminates all resources that produce and store data, keeps buckets and tables

cd terraform

# destroy the producer job, producer scheduler, API application and VM with airflow
terraform destroy -auto-approve -target="google_cloud_run_v2_job.data-producer-job"

# destroy the dbt job and dbt scheduler
terraform destroy -auto-approve -target="google_cloud_run_v2_job.dbt-job"