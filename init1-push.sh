#!/bin/bash

# init1-push.sh: build and push Docker images to Artifact Registry

# check if pre-init.sh was executed
if [ ! -e "./pre-init-done" ]; then
	echo "You must execute pre-init.sh first" 2>&1;
	exit 1
fi

# save current directory
HOMEDIR=$(pwd)

# check if docker is running
docker ps > /dev/null
if [ $? -ne 0 ]; then
	echo "Docker is not running, launch it before proceeding" 2>&1;
	exit 1
fi

# check for my-creds.json
if [ ! -e "$HOMEDIR/creds/my-creds.json" ]; then
	echo "File ${HOMEDIR}/creds/my-creds.json not found" 2>&1;
	exit 1
fi

# download terraform's google provider
cd terraform
terraform init

# validate .tf files
terraform validate
if [ $? -ne 0 ]; then
	echo "Either main.tf of variables.tf has invalid configuration" 2>&1;
	exit 1
fi
cd "$HOMEDIR"

# extract project_id from variables.tf
project_id=$(sed -n "/variable \"project_id\"/{:begin;n;s/.*default[^\"]*\"\(.*\)\".*/\1/p;t;b begin}" terraform/variables.tf)

# replace the database with the project_id in dbt/my_zoomcamp_project/models/properties.yml
sed -i "s/REPLACE/${project_id}/" "$HOMEDIR"/dbt/my_zoomcamp_project/models/properties.yml

# build dbt image
echo "Building Docker image for the dbt container"
docker build -f docker/Dockerfile-dbt -t dbt:1.7 .

# build app image
echo "Building Docker image for the API application"
docker build -f docker/Dockerfile-app -t app:1.0 .

# build producer image
echo "Building Docker image for the data producer"
docker build -f docker/Dockerfile-producer -t producer:1.0 .

# create artifact registry repository to store Docker images
echo "Creating Artifact Registry repository"
cd terraform
terraform apply -auto-approve -target="google_project_service.resource_manager_api"
echo "Waiting a bit to make sure the API is enabled"
for i in {9..0}; do echo -n $i; sleep 1; echo -ne "\b"; done; echo ""
terraform apply -auto-approve -target="google_project_service.artifact_api"
echo "Waiting a bit to make sure the API is enabled"
for i in {19..10}; do echo -n $i; sleep 1; echo -ne "\b\b"; done; echo -ne "\b\b  "; echo -ne "\b\b"
for i in {9..0}; do echo -n $i; sleep 1; echo -ne "\b\b"; done; echo ""
terraform apply -auto-approve -target="google_artifact_registry_repository.my-repo"
cd "$HOMEDIR"

# get the location of the artifact registry from variables.tf
artifact_location=$(sed -n "/variable \"artifact/{:begin;n;s/.*default[^\"]*\"\(.*\)\".*/\1/p;t;b begin}" terraform/variables.tf)

# log in to us-east1 artifact registry
cat creds/my-creds.json | docker login -u _json_key --password-stdin "https://${artifact_location}-docker.pkg.dev"

# tag all images as a push requisite
docker tag app:1.0 "${artifact_location}-docker.pkg.dev/${project_id}/zoomcamp-repository/app:1.0"
docker tag producer:1.0 "${artifact_location}-docker.pkg.dev/${project_id}/zoomcamp-repository/producer:1.0"
docker tag dbt:1.7 "${artifact_location}-docker.pkg.dev/${project_id}/zoomcamp-repository/dbt:1.7"

# push them to artifact registry
echo "Pushing API application Docker image to Artifact Registry"
docker push "${artifact_location}-docker.pkg.dev/${project_id}/zoomcamp-repository/app:1.0"

echo "Pushing data producer Docker image to Artifact Registry"
docker push "${artifact_location}-docker.pkg.dev/${project_id}/zoomcamp-repository/producer:1.0"

echo "Pushing dbt Docker image to Artifact Registry"
docker push "${artifact_location}-docker.pkg.dev/${project_id}/zoomcamp-repository/dbt:1.7"

# Enable other APIs
cd terraform

terraform apply -auto-approve -target="google_project_service.scheduler_api"
terraform apply -auto-approve -target="google_project_service.compute_engine_api"
terraform apply -auto-approve -target="google_project_service.cloudrun_api"
terraform apply -auto-approve -target="google_project_service.bigquery_api"

echo "Waiting a bit to make sure the APIs are enabled"
for i in {15..10}; do echo -n $i; sleep 1; echo -ne "\b\b"; done; echo -ne "\b\b  "; echo -ne "\b\b"
for i in {9..0}; do echo -n $i; sleep 1; echo -ne "\b\b"; done; echo -e "\b\bDone"

# Create
cd "$HOMEDIR"
touch init1-done

echo "init1-push completed successfully"
echo "You can proceed to run init2-apply once the time is right"
