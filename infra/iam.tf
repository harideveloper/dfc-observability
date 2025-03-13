// builder sa
resource "google_service_account" "builder" {
  account_id   = "${var.application}-builder"
  display_name = "custom service account for observability services"
}

resource "google_project_iam_member" "builder_build_permissions" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.builder.email}"
}

resource "google_project_iam_member" "builder_log_permissions" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.builder.email}"
}

resource "google_storage_bucket_iam_member" "dfc_builder_permissions" {
  bucket = "gcf-v2-sources-${var.project_number}-europe-west2"
  role   = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.builder.email}"
}

// project info sa
resource "google_service_account" "project_info" {
  account_id   = "project-info"
  display_name = "custom service account for project info service"
}

resource "google_project_iam_member" "project_info_log_permissions" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.project_info.email}"
}

resource "google_project_iam_member" "project_info_metric_creator_permissions" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.project_info.email}"
}

resource "google_project_iam_member" "project_info_bq_editor_permissions" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.project_info.email}"
}

# resource "google_project_iam_member" "project_info_resource_manager_permissions" {
#   project = var.project_id
#   role    = "roles/resourcemanager.projectViewer"
#   member  = "serviceAccount:${google_service_account.project_info.email}"
# }

resource "google_folder_iam_member" "project_info_folder_viewer_permissions" {
  folder = var.folder  
  role   = "roles/resourcemanager.folderViewer"
  member  = "serviceAccount:${google_service_account.project_info.email}"
}




