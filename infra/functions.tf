// File Accessor UI 
resource "google_storage_bucket" "project_info" {
  name                        = "${var.project_id}-${var.application}-bucket"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}

data "archive_file" "project_info" {
  type        = "zip"
  source_dir  = "${path.module}/../app/service/project_info"
  output_path = "${path.module}/function-project-info.zip"

  excludes = [
    "**/__pycache__",
    "**/*.pyc",
    "**/test_*.py",
    "**/*.log",
    "**/*.pytest_cache",
    "**/*.coverage"
  ]
}

resource "google_storage_bucket_object" "project_info" {
  name         = "function.zip"
  bucket       = google_storage_bucket.project_info.name
  source       = data.archive_file.project_info.output_path
  content_type = "application/zip"
}

resource "google_cloudfunctions2_function" "project_info" {
  name     = "project-info"
  location = var.region

  build_config {
    runtime         = "python312"
    entry_point     = "main"
    service_account = google_service_account.builder.name
    source {
      storage_source {
        bucket = google_storage_bucket.project_info.name
        object = google_storage_bucket_object.project_info.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256M"
    timeout_seconds    = 120

    # environment_variables = {
    #   LANDING_BUCKET = google_storage_bucket.landing.name
    # }

    environment_variables = {
      # BQ_TABLE   = google_bigquery_table.projects.friendly_name
      BQ_TABLE    = "${var.project_id}.${google_bigquery_dataset.projects.dataset_id}.${google_bigquery_table.projects.table_id}"
      FOLDER_ID   = var.folder
      GCP_PROJECT = var.project_id
    }

    vpc_connector                 = google_vpc_access_connector.connector.id
    vpc_connector_egress_settings = "ALL_TRAFFIC"
    # ingress_settings = "ALLOW_INTERNAL_ONLY"
    service_account_email = google_service_account.project_info.email
  }

  depends_on = [
    google_storage_bucket.project_info,
    google_service_account.project_info,
    google_vpc_access_connector.connector,
    google_bigquery_dataset.projects,
    google_bigquery_table.projects
  ]
}


resource "google_cloud_run_service_iam_binding" "project_info_invokers" {
  location = google_cloudfunctions2_function.project_info.location
  project  = google_cloudfunctions2_function.project_info.project
  service  = google_cloudfunctions2_function.project_info.name
  role     = "roles/run.invoker"
  members = [
    "allUsers",
  ]
}
