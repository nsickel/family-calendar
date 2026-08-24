# infra

Terraform for deploying family-calendar to Cloud Run. Provisions:

- A Cloud Run v2 service (gen2 execution environment) pulling
  `docker.io/nsickel/family-calendar:<image_tag>` directly from Docker Hub
  (public repo — no registry credentials needed).
- A Secret Manager secret for `DATABASE_URL`, pointing at a Supabase Postgres
  project. Supabase is provisioned separately, outside this Terraform stack
  (see Prerequisites) — all persistence (OAuth tokens, family/member config,
  per-family login credentials) lives there now, not on any Cloud Run-managed
  volume.
- A Secret Manager secret for `GOOGLE_CLIENT_SECRET`.
- A Secret Manager secret for `SECRET_KEY`, used to sign session cookies.
- A dedicated least-privilege service account for the Cloud Run service
  (secret access only, nothing else).

Cloud Run's own IAM stays open (`allUsers` can invoke) — the app gates itself
with a signed, httpOnly session cookie issued on login (`POST /auth/login`),
checked against the `families` table in Postgres (no more shared
`AUTH_USERNAME`/`AUTH_PASSWORD`, and no more browser-native Basic Auth
popup), same as it already does locally. The public SPA shell (`/`,
`/assets/*`) is intentionally reachable without a session so the login page
can render — it contains no secrets. `/api/*` and the Google-connect flow
(`/auth/setup`, `/auth/connect/*`, `/auth/callback`) still require a valid
session.

Deploys are manual and pinned by design: there's no default for `image_tag`,
so every rollout is `terraform apply -var="image_tag=<git-short-sha>"` with a
tag you picked, not whatever happens to be `:latest` on Docker Hub at the time.

## Prerequisites

- `gcloud auth application-default login` (or a service account key) so
  Terraform can authenticate against GCP.
- An existing GCP project with billing enabled — pass its ID as `project_id`.
- The Google OAuth client already set up per the root `README.md` (Google Cloud
  project, OAuth consent screen, Web application OAuth client ID/secret).
- A Supabase project (free tier) created via https://supabase.com/dashboard —
  grab the Session Pooler connection string from **Project Settings → Database
  → Connection string → Session pooler**, and pass it as
  `-var="database_url=..."`.

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
secret_key             = "...."      # random value signing session cookies, e.g. `openssl rand -hex 32`
database_url           = "postgresql://postgres.xxxx:PASSWORD@aws-0-region.pooler.supabase.com:5432/postgres"
# ^ paste Supabase's Session Pooler string as-is — db.py rewrites the
# `postgresql://` scheme to `postgresql+psycopg://` (the installed driver)
# at startup, so no manual edit is needed.
```

### First deploy (two-step, because of the OAuth redirect URI)

Cloud Run only assigns the service's real `*.run.app` URL once it exists, but
that URL has to be registered as the OAuth redirect URI and fed back into the
app as `APP_URL`. So:

1. Run the schema migration against Supabase (one-time, and again after any
   future schema change): from `backend/`, with `DATABASE_URL` pointed at the
   Supabase Session Pooler URI, run `alembic upgrade head`. This is a manual
   step, deliberately not automated in CI — matching how image rollouts here
   are already a deliberate, pinned action rather than automatic.
2. `terraform plan` then `terraform apply` — uses the `app_url` placeholder
   default. This creates the service and everything else.
3. Note the `service_url` output.
4. `terraform apply -var="app_url=<service_url>"` (plus your other `-var`s, or
   just add `app_url` to `terraform.tfvars`) — rolls a new revision with the
   correct `APP_URL`.
5. In Google Cloud Console (**APIs & Services → Credentials** → your OAuth
   client), add `<service_url>/auth/callback` as an authorized redirect URI.
6. Provision the first family (one-time): from `backend/`, with `DATABASE_URL`
   pointed at Supabase, run
   `python -m scripts.create_family --name "..." --username ... --member "slug:Name:emoji:#color" ...`
   (see root `CLAUDE.md`).
7. Visit `<service_url>/auth/setup`, log in with the family's credentials, and
   connect each family member's Google account. Tokens are stored in the
   `oauth_tokens` Postgres table, so this survives redeploys and scale-to-zero
   cycles.

### Rolling out a new image

After a push to `main` publishes a new image to Docker Hub:

```
terraform apply -var="image_tag=<new-git-short-sha>"
```

### Verifying

- `terraform fmt -check && terraform validate` for static correctness.
- `curl https://<service_url>/health` → `{"status":"ok"}` (always exempt).
- `curl https://<service_url>/` → `200` — the SPA shell (including the login
  page) is intentionally public.
- `curl https://<service_url>/api/week` → `401` until a valid session cookie
  is supplied (obtained via `POST /auth/login`).
