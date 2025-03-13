resource "google_cloud_scheduler_job" "daily_trigger" {
  name        = "${var.application}-daily"
  description = "dfc scheduler trigger project data load"
  schedule    = "*/10 * * * *"
  project     = google_cloudfunctions2_function.project_info.project
  region      = google_cloudfunctions2_function.project_info.location

  http_target {
    uri         = google_cloudfunctions2_function.project_info.service_config[0].uri
    http_method = "POST"
    oidc_token {
      audience              = "${google_cloudfunctions2_function.project_info.service_config[0].uri}/"
      service_account_email = google_service_account.project_info.email
    }
  }
}