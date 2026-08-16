variable "project_id" {
  description = "GCP project ID to deploy into."
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run and the tokens bucket."
  type        = string
  default     = "europe-west3"
}

variable "service_name" {
  description = "Name of the Cloud Run service."
  type        = string
  default     = "family-calendar"
}

variable "image_tag" {
  description = "Tag of nsickel/family-calendar on Docker Hub to deploy (e.g. a git short SHA). No default on purpose — every rollout is a deliberate choice."
  type        = string
}

variable "app_url" {
  description = <<-EOT
    Public URL of the service, used to build the OAuth redirect URI (APP_URL env var).
    Cloud Run only assigns the real *.run.app URL after first apply, so the first
    apply uses a placeholder; re-apply with the real service_url output afterwards.
  EOT
  type        = string
  default     = "https://placeholder.invalid"
}

variable "tz" {
  description = "Timezone for the calendar display (TZ env var)."
  type        = string
  default     = "Europe/Berlin"
}

variable "max_instance_count" {
  description = "Upper bound on Cloud Run instances, as a cost ceiling."
  type        = number
  default     = 2
}

variable "google_client_id" {
  description = "OAuth client ID from the Google Cloud project set up per the main README (not sensitive)."
  type        = string
}

variable "google_client_secret" {
  description = "OAuth client secret from the Google Cloud project set up per the main README."
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Random secret used to sign session cookies (auth/session_cookie.py). Generate with e.g. `openssl rand -hex 32`."
  type        = string
  sensitive   = true
}

variable "database_url" {
  description = <<-EOT
    Postgres connection string for the Supabase project (Session Pooler URI,
    e.g. postgresql+psycopg://postgres.xxxx:PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres).
    Created manually in the Supabase dashboard — not managed by this Terraform stack.
  EOT
  type        = string
  sensitive   = true
}
