#!/bin/bash
# Install Docker:
# Reference: https://docs.docker.com/engine/install/ubuntu/

word="REPLACE"
num="REPLACE"

# Uninstall conflicting packages
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done

# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install the latest version
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Check status
sudo docker run hello-world
if [ $? -eq 0 ]; then echo "Docker installed successfully"; else echo "Something went wrong while installing Docker" 2>&1; exit 1; fi


# Create a directory for Airflow
mkdir airflow && cd airflow
homedir=$(pwd)

# Download necessary files for Airflow
curl -O https://raw.githubusercontent.com/iur-y/DEZoomcamp-Project/main/compose.yml
curl -O https://raw.githubusercontent.com/iur-y/DEZoomcamp-Project/main/docker/Dockerfile-airflow

mkdir -p ./dags ./logs ./plugins ./config ./ssl
cd ./dags

curl -O https://raw.githubusercontent.com/iur-y/DEZoomcamp-Project/main/dags/consume_api.py
curl -O https://raw.githubusercontent.com/iur-y/DEZoomcamp-Project/main/dags/dag_consume.py
curl -O https://raw.githubusercontent.com/iur-y/DEZoomcamp-Project/main/dags/dag_upload_gcs.py

# Replace bucket name in dag_upload.gcs.py
sed -i "s/raw_parquet_data_zoomcamp_project/&_${word}_${num}/" ./dag_upload_gcs.py

# Generate SSL certificates if you wish to access the Airflow web server
cd "${homedir}/ssl"
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout private_key.key -out certificate.crt -subj "/C=/ST=/L=/O=/CN="
cd "$homedir"

# Prepare .env file
echo -e "AIRFLOW_UID=$(id -u)" > .env

# Append the root URL of the API into .env
echo "API_URL=$(gcloud run services list --filter=cloudrun-api --format='value(URL)')" >> .env

# Initialize and start Airflow
sudo docker compose up airflow-init
sudo docker compose up -d

