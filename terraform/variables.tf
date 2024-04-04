variable "project_id" {
  type        = string
  description = "The id of your Google Cloud Project."
  # Uncomment the line below and replace
  # default = REPLACE
}

variable "service_account_principal" {
  type        = string
  description = "IAM principal (e-mail) to be used for authentication to Cloud Run services"
  # Uncomment the line below and replace
  # default = REPLACE
}

variable "credentials" {
  type        = string
  description = "Pathname to your Google Cloud service account key file"
  default     = "../creds/my-creds.json"
}

variable "bucket_location" {
  type        = string
  description = "GCS bucket location"
  default     = "us-east1"
}

variable "bucket_storage_class" {
  type        = string
  description = "The storage class for the bucket, e.g. STANDARD, COLDLINE, ARCHIVE"
  default     = "STANDARD"
}

variable "dataset_location" {
  type        = string
  description = "BigQuery dataset location"
  default     = "us-east1"
}

variable "artifact_registry_location" {
  type        = string
  description = "Artifact Registry location"
  default     = "us-east1"
}

variable "app_location" {
  type        = string
  description = "API service location"
  default     = "us-east1"
}

variable "compute_engine_zone" {
  type        = string
  description = "Zone for VM instance"
  default     = "us-east1-b"
}