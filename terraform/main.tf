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
  project = var.project_id
}

resource "google_storage_bucket" "raw_data" {
  name          = "raw_parquet_data_zoomcamp_project"
  location      = var.bucket_location
  force_destroy = true
  storage_class = var.bucket_storage_class

  public_access_prevention = "enforced"
}