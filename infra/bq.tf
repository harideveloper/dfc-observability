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

  schema = <<EOF
[
  {"name": "project_id", "type": "STRING", "mode": "REQUIRED"},
  {"name": "name", "type": "STRING", "mode": "REQUIRED"},
  {"name": "parent", "type": "STRING", "mode": "NULLABLE"},
  {"name": "display_name", "type": "STRING", "mode": "NULLABLE"},
  {"name": "state", "type": "STRING", "mode": "NULLABLE"},
  {"name": "create_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
  {"name": "update_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
  {"name": "ingestion_time", "type": "TIMESTAMP", "mode": "NULLABLE"},
  {"name": "etag", "type": "STRING", "mode": "NULLABLE"},
  {
    "name": "labels",
    "type": "RECORD",
    "mode": "REPEATED",
    "fields": [
      {"name": "key", "type": "STRING", "mode": "NULLABLE"},
      {"name": "value", "type": "STRING", "mode": "NULLABLE"}
    ]
  }
]
EOF
  time_partitioning {
    type = "DAY"
    field = "ingestion_time"
    expiration_ms = null 
  }

  clustering = ["project_id"]
}