#!/bin/bash

# init2-apply.sh: does terraform apply interactively after enabling more APIs

# check if init1-push.sh was executed
if [ ! -e "./init1-done" ]; then
	echo "You must execute init1-push.sh first" 2>&1;
	exit 1
fi

cd terraform

terraform apply -auto-approve -target="google_project_service.scheduler_api"
terraform apply -auto-approve -target="google_project_service.compute_engine_api"
terraform apply -auto-approve -target="google_project_service.cloudrun_api"
terraform apply -auto-approve -target="google_project_service.bigquery_api"

echo "Waiting a bit to make sure the APIs are enabled"
for i in {19..10}; do echo -n $i; sleep 1; echo -ne "\b\b"; done; echo -ne "\b\b  "; echo -ne "\b\b"
for i in {9..0}; do echo -n $i; sleep 1; echo -ne "\b\b"; done; echo ""

terraform apply

