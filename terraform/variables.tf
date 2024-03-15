variable "project_id" {
  type        = string
  description = "The id of your Google Cloud Project."
  # You can uncomment the line below so terraform doesn't prompt you
  # for the project id each time
  #default = <YOUR-PROJECT-ID>
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