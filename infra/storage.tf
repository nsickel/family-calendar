resource "google_storage_bucket" "tokens" {
  project  = var.project_id
  name     = "${var.project_id}-${var.service_name}-tokens"
  location = var.region

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  # Small, precious data (OAuth refresh tokens) — don't let a stack teardown
  # silently delete it.
  force_destroy = false

  versioning {
    enabled = true
  }

  depends_on = [google_project_service.required]
}

resource "google_storage_bucket_iam_member" "cloud_run_tokens_access" {
  bucket = google_storage_bucket.tokens.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}
