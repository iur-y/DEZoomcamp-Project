# download terraform's google provider
cd terraform && terraform init # && terraform plan

# setup airflow initialization steps as per docker quickstart docs
mkdir ./dags ./logs ./plugins
echo -e "AIRFLOW_UID=$(id -u)" > .env # necessary for linux
docker compose up airflow-init

