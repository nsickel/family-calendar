resource "google_secret_manager_secret" "google_client_secret" {
  project   = var.project_id
  secret_id = "${var.service_name}-google-client-secret"

  replication {
    auto {}
  }

  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret_version" "google_client_secret" {
  secret      = google_secret_manager_secret.google_client_secret.id
  secret_data = var.google_client_secret
}

resource "google_secret_manager_secret_iam_member" "google_client_secret_access" {
  secret_id = google_secret_manager_secret.google_client_secret.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_secret_manager_secret" "auth_password" {
  project   = var.project_id
  secret_id = "${var.service_name}-auth-password"

  replication {
    auto {}
  }

  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret_version" "auth_password" {
  secret      = google_secret_manager_secret.auth_password.id
  secret_data = var.auth_password
}

resource "google_secret_manager_secret_iam_member" "auth_password_access" {
  secret_id = google_secret_manager_secret.auth_password.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}
