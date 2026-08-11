# infra

Terraform for deploying family-calendar to Cloud Run. Provisions:

- A Cloud Run v2 service (gen2 execution environment) pulling
  `docker.io/nsickel/family-calendar:<image_tag>` directly from Docker Hub
  (public repo — no registry credentials needed).
- A private GCS bucket mounted directly into the container at `/app/tokens`
  (Cloud Run's native Cloud Storage volume mount). `backend/auth/token_store.py`
  needs no changes — it just does local file I/O against a path that now
  transparently persists to GCS instead of the container's ephemeral disk.
- Secret Manager secrets for `GOOGLE_CLIENT_SECRET` and `AUTH_PASSWORD`.
- A dedicated least-privilege service account for the Cloud Run service (secret
  access + object access on the tokens bucket only, nothing else).

Cloud Run's own IAM stays open (`allUsers` can invoke) — the app gates itself
with HTTP Basic Auth (`AUTH_USERNAME`/`AUTH_PASSWORD`), same as it already does
locally.

Deploys are manual and pinned by design: there's no default for `image_tag`,
so every rollout is `terraform apply -var="image_tag=<git-short-sha>"` with a
tag you picked, not whatever happens to be `:latest` on Docker Hub at the time.

## Prerequisites

- `gcloud auth application-default login` (or a service account key) so
  Terraform can authenticate against GCP.
- An existing GCP project with billing enabled — pass its ID as `project_id`.
- The Google OAuth client already set up per the root `README.md` (Google Cloud
  project, OAuth consent screen, Web application OAuth client ID/secret).

## Usage

```
cd infra
terraform init
```

Set variables via a gitignored `terraform.tfvars` or `TF_VAR_*` env vars — do
not commit real secrets. Example `terraform.tfvars`:

```hcl
project_id            = "your-gcp-project-id"
image_tag              = "abc1234"   # a git short SHA that was pushed to Docker Hub
google_client_id       = "....apps.googleusercontent.com"
google_client_secret   = "...."
auth_username          = "...."
auth_password           = "...."
```

### First deploy (two-step, because of the OAuth redirect URI)

Cloud Run only assigns the service's real `*.run.app` URL once it exists, but
that URL has to be registered as the OAuth redirect URI and fed back into the
app as `APP_URL`. So:

1. `terraform plan` then `terraform apply` — uses the `app_url` placeholder
   default. This creates the service and everything else.
2. Note the `service_url` output.
3. `terraform apply -var="app_url=<service_url>"` (plus your other `-var`s, or
   just add `app_url` to `terraform.tfvars`) — rolls a new revision with the
   correct `APP_URL`.
4. In Google Cloud Console (**APIs & Services → Credentials** → your OAuth
   client), add `<service_url>/auth/callback` as an authorized redirect URI.
5. Visit `<service_url>/auth/setup` and connect each family member's account.
   Tokens land in the GCS bucket (`tokens_bucket` output), so this survives
   redeploys and scale-to-zero cycles.

### Rolling out a new image

After a push to `main` publishes a new image to Docker Hub:

```
terraform apply -var="image_tag=<new-git-short-sha>"
```

### Verifying

- `terraform fmt -check && terraform validate` for static correctness.
- `curl https://<service_url>/health` → `{"status":"ok"}` (exempt from Basic Auth).
- `curl https://<service_url>/` → `401` until Basic Auth credentials are supplied.
