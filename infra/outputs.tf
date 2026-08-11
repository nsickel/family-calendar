output "service_url" {
  description = "Public URL of the deployed Cloud Run service. Feed this back in as -var=\"app_url=...\" (see infra/README.md) and register <service_url>/auth/callback as an authorized redirect URI in Google Cloud Console."
  value       = google_cloud_run_v2_service.app.uri
}

output "tokens_bucket" {
  description = "GCS bucket backing the /app/tokens mount."
  value       = google_storage_bucket.tokens.name
}

output "service_account_email" {
  description = "Cloud Run runtime service account."
  value       = google_service_account.cloud_run.email
}
