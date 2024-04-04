terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.19.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project_id
}

# Enable APIs
##==##==##==##==##==##==##==##==##==##==##==##
resource "google_project_service" "scheduler_api" {
  project            = var.project_id
  service            = "cloudscheduler.googleapis.com"
  disable_on_destroy = true
}
resource "google_project_service" "resource_manager_api" {
  project            = var.project_id
  service            = "cloudresourcemanager.googleapis.com"
  disable_on_destroy = true
}
resource "google_project_service" "artifact_api" {
  project            = var.project_id
  service            = "artifactregistry.googleapis.com"
  disable_on_destroy = true
}
resource "google_project_service" "compute_engine_api" {
  project            = var.project_id
  service            = "compute.googleapis.com"
  disable_on_destroy = true
}
resource "google_project_service" "cloudrun_api" {
  project            = var.project_id
  service            = "run.googleapis.com"
  disable_on_destroy = true
}
##==##==##==##==##==##==##==##==##==##==##==##

# This bucket is intended to be used by the producer to write data
# and the API to read and hand out data
resource "google_storage_bucket" "api_producer_data" {
  name          = "api_producer_data_zoomcamp_project"
  location      = var.bucket_location
  force_destroy = true
  storage_class = var.bucket_storage_class

  public_access_prevention = "enforced"
}

# This bucket is used by Airflow to write the data retrieved from
# calling the API
resource "google_storage_bucket" "raw_data" {
  name          = "raw_parquet_data_zoomcamp_project"
  location      = var.bucket_location
  force_destroy = true
  storage_class = var.bucket_storage_class

  public_access_prevention = "enforced"
}

# In BigQuery, {dataset <=> schema} of PostgreSQL
resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = "videogame_dataset"
  description                = "Contains sales data for videogames"
  location                   = var.dataset_location
  delete_contents_on_destroy = true
}

# dbt needs a table to transform the data, so we make a raw data table
resource "google_bigquery_table" "raw_data_table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "raw_videogame_table"
  # which is partitioned for optimized costs and efficiency
  external_data_configuration {
    # if autodetect = true, then files must exist in the bucket before creating this table
    # and if autodetect = false, we must provide a schema for the columns of the table
    autodetect    = false
    source_format = "PARQUET"
    source_uris   = ["gs://${google_storage_bucket.raw_data.name}/*.parquet"]
    hive_partitioning_options {
      # the objects in the bucket follow this naming convention, for example:
      # gs://bucketname/dt=2024-04-01/morecharacters.parquet
      # it's like having multiple folders: dt=2024-04-01, dt=2024-04-02, dt=2024-04-03, ...
      # so we tell BigQuery to use these folders for partitioning and treat them like a DATE
      source_uri_prefix = "gs://${google_storage_bucket.raw_data.name}/{dt:DATE}"
      # true here means queries are required to use `WHERE dt = somedate`
      require_partition_filter = true
      # "CUSTOM" is used to explicitly tell BigQuery dt is a date
      # ({dt:DATE} in the line above), instead of leaving up to BigQuery to infer what dt is
      mode = "CUSTOM"
    }
    # Terraform docs state that you can't provide a schema for parquet files, which is not true.
    schema = jsonencode([
      {
        "name" : "Name",
        "type" : "STRING"
      },
      {
        "name" : "Platform",
        "type" : "STRING"
      },
      {
        "name" : "Genre",
        "type" : "STRING"
      },
      {
        "name" : "Publisher",
        "type" : "STRING"
      },
      {
        "name" : "NA_Sales",
        "type" : "INTEGER"
      },
      {
        "name" : "EU_Sales",
        "type" : "INTEGER"
      },
      {
        "name" : "JP_Sales",
        "type" : "INTEGER"
      },
      {
        "name" : "Other_Sales",
        "type" : "INTEGER"
      },
      {
        "name" : "Global_Sales",
        "type" : "INTEGER"
      },
      {
        "name" : "Date",
        "type" : "STRING"
      },
      {
        "name" : "Refunds",
        "type" : "INTEGER"
      }
    ])
  }
  depends_on = [google_bigquery_dataset.dataset]
}

resource "google_artifact_registry_repository" "my-repo" {
  location      = var.artifact_registry_location
  repository_id = "zoomcamp-repository"
  description   = "Holds images for the data source API, dbt and data producer"
  format        = "docker"
}

# app
resource "google_cloud_run_v2_service" "app" {
  name     = "cloudrun-api"
  location = var.app_location
  # traffic from all IP addresses on the internet is allowed
  ingress = "INGRESS_TRAFFIC_ALL"

  template {
    execution_environment = "EXECUTION_ENVIRONMENT_GEN1"
    containers {
      image = "${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/zoomcamp-repository/app:1.0"
      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
      ports {
        container_port = 5000
      }
    }
    scaling {
      max_instance_count = 2
    }

    service_account = var.service_account_principal
  }
  # Impose that the producer (which uploads data to GCS) must exist before the app
  depends_on = [google_cloud_scheduler_job.data-producer-job]
}

# Even though we allow traffic from all IP addresses, this data block and the resource
# below are what make the application not require any authentication from clients, i.e. Airflow
data "google_iam_policy" "public" {
  binding {
    role = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_service_iam_policy" "public" {
  location = google_cloud_run_v2_service.app.location
  project  = google_cloud_run_v2_service.app.project
  service  = google_cloud_run_v2_service.app.name

  policy_data = data.google_iam_policy.public.policy_data

  depends_on = [google_cloud_run_v2_service.app]
}

# VM
resource "google_compute_instance" "default" {
  name         = "my-vm-instance"
  machine_type = "e2-standard-2"
  zone         = var.compute_engine_zone

  tags = ["demo-vm-instance"]

  # Waits for data source API to start, so the startup script
  # used for Airflow can get its IP to make the API requests 
  depends_on = [google_cloud_run_v2_service.app]

  # Only required for testing purposes
  # metadata = {
  #   ssh-keys =
  # }

  metadata_startup_script = file("./startup-script.sh")

  boot_disk {
    initialize_params {
      image = "ubuntu-2204-jammy-v20240319"
      size  = 30 # 30 GB disk
    }
  }

  # Might fail if the Google Project doesn't have the default network?
  network_interface {
    network = "default"

    # Assigns a public IP to the machine, so you can access Airflow webserver on port 8080
    access_config {
      // Ephemeral public IP
    }
  }

  # What service account to attach to the VM instance
  service_account {
    # Google recommends custom service accounts that have cloud-platform scope and permissions granted via IAM Roles.
    email  = var.service_account_principal
    scopes = ["cloud-platform"]
  }
}


# This is for allowing only one IP address to checkout the Airflow webserver
# Uncomment the resource below and put your IP address in the source_ranges
# lines if you want to connect to the Airflow web server
################## EXAMPLE ##################
#   source_ranges = ["123.456.789.012/32"]
#############################################

# resource "google_compute_firewall" "rules" {
#   project = var.project_id
#   name    = "my-firewall-rule"
#   network = "default"

#   allow {
#     protocol = "tcp"
#     ports    = ["8080"]
#   }
#   direction     = "INGRESS"
#   source_ranges = ["<your-ip-address-here>/32"]
# }

# dbt job
resource "google_cloud_run_v2_job" "dbt-job" {
  name     = "dbt-job"
  location = var.dataset_location # same location as BigQuery dataset

  template {
    template {
      containers {
        image = "${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/zoomcamp-repository/dbt:1.7"
      }
      service_account = var.service_account_principal
    }
  }
}

# Schedule the dbt job
# I built the dbt Docker image with the idea of
# running this dbt job once per day in mind (after the end of the day)
# where all the data for that day had already been collected by Airflow
# But since whoever replicates this project should not have to wait until
# around midnight to run the code, I made it so that this job runs every 20 mins
# Which also means it should be terminated after running once to avoid duplicate data
# this is what the partial-destroy.sh script is for
resource "google_cloud_scheduler_job" "dbt-job" {
  name             = "schedule-dbt"
  description      = "Schedule for running the dbt container"
  schedule         = "*/20 * * * *" # every 20 mins
  attempt_deadline = "120s"
  region           = var.dataset_location

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "POST"
    uri         = "https://${google_cloud_run_v2_job.dbt-job.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.dbt-job.name}:run"

    oauth_token {
      service_account_email = var.service_account_principal
    }
  }

  depends_on = [resource.google_cloud_run_v2_job.dbt-job]
}

# Data producer job
resource "google_cloud_run_v2_job" "data-producer-job" {
  name     = "data-producer-job"
  location = var.dataset_location # same location as BigQuery dataset

  template {
    template {
      containers {
        image = "${var.artifact_registry_location}-docker.pkg.dev/${var.project_id}/zoomcamp-repository/producer:1.0"
      }
      service_account = var.service_account_principal
    }
  }
  depends_on = [google_artifact_registry_repository.my-repo, google_storage_bucket.api_producer_data]
}

# Schedule the data producer job
resource "google_cloud_scheduler_job" "data-producer-job" {
  name             = "schedule-producer"
  description      = "Schedule for running the data producer container"
  schedule         = "*/2 * * * *" # every 2 mins
  attempt_deadline = "30s"
  region           = var.dataset_location

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "POST"
    uri         = "https://${google_cloud_run_v2_job.data-producer-job.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.data-producer-job.name}:run"

    oauth_token {
      service_account_email = var.service_account_principal
    }
  }

  depends_on = [resource.google_cloud_run_v2_job.data-producer-job]
}