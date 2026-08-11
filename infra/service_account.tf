resource "google_service_account" "cloud_run" {
  project      = var.project_id
  account_id   = "${var.service_name}-run"
  display_name = "Cloud Run runtime SA for ${var.service_name}"

  depends_on = [google_project_service.required]
}
