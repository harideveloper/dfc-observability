resource "google_bigquery_dataset" "projects" {
  dataset_id    = "observability" 
  friendly_name = "Project Info for DFC Projects"
  description   = "Dataset for storing GCP project details"
  location      = "EU"
}

resource "google_bigquery_table" "projects" {
  dataset_id = google_bigquery_dataset.projects.dataset_id
  table_id   = "project_info"
  deletion_protection = false
  schema = file("schema/project_info.json")
  time_partitioning {
    type = "DAY"
    field = "ingestion_time"
    expiration_ms = 7776000000  # 90-days
  }
  clustering = ["project_id"]
}