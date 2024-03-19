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

resource "google_storage_bucket" "raw_data" {
  name          = "raw_parquet_data_zoomcamp_project"
  location      = var.bucket_location
  force_destroy = true
  storage_class = var.bucket_storage_class

  public_access_prevention = "enforced"
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                 = "videogame_dataset"
  description                = "Contains sales data for videogames"
  location                   = var.dataset_location
  delete_contents_on_destroy = true
}

resource "google_bigquery_table" "raw_data_table" {
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = "raw_videogame_table"

  external_data_configuration {
    autodetect    = true
    source_format = "PARQUET"
    source_uris   = ["gs://${google_storage_bucket.raw_data.name}/*.parquet"]
    hive_partitioning_options {
      source_uri_prefix = "gs://${google_storage_bucket.raw_data.name}/{dt:DATE}"
      require_partition_filter = true
      mode = "CUSTOM"
    }
  }
}