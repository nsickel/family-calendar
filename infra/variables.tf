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

variable "auth_username" {
  description = "Shared HTTP Basic Auth username gating the whole app."
  type        = string
}

variable "auth_password" {
  description = "Shared HTTP Basic Auth password gating the whole app."
  type        = string
  sensitive   = true
}
