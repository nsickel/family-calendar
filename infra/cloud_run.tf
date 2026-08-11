resource "google_cloud_run_v2_service" "app" {
  project  = var.project_id
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account       = google_service_account.cloud_run.email
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"

    scaling {
      min_instance_count = 0
      max_instance_count = var.max_instance_count
    }

    volumes {
      name = "tokens"
      gcs {
        bucket    = google_storage_bucket.tokens.name
        read_only = false
      }
    }

    containers {
      image = "docker.io/nsickel/family-calendar:${var.image_tag}"

      ports {
        container_port = 8000
      }

      volume_mounts {
        name       = "tokens"
        mount_path = "/app/tokens"
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }

      env {
        name  = "TZ"
        value = var.tz
      }

      env {
        name  = "APP_URL"
        value = var.app_url
      }

      env {
        name  = "AUTH_USERNAME"
        value = var.auth_username
      }

      env {
        name  = "GOOGLE_CLIENT_ID"
        value = var.google_client_id
      }

      env {
        name = "AUTH_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.auth_password.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GOOGLE_CLIENT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.google_client_secret.secret_id
            version = "latest"
          }
        }
      }
    }
  }

  depends_on = [
    google_project_service.required,
    google_storage_bucket_iam_member.cloud_run_tokens_access,
    google_secret_manager_secret_iam_member.google_client_secret_access,
    google_secret_manager_secret_iam_member.auth_password_access,
  ]
}

# App gates itself with HTTP Basic Auth, so Cloud Run's own IAM layer is left
# open — allUsers may invoke, the app's basic_auth middleware is the real gate.
resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  project  = google_cloud_run_v2_service.app.project
  location = google_cloud_run_v2_service.app.location
  name     = google_cloud_run_v2_service.app.name

  role   = "roles/run.invoker"
  member = "allUsers"
}
