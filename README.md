# family-calendar

A shared family wall-calendar: a FastAPI backend that syncs Google Calendar
and Google Tasks for multiple family members, and a React/Vite frontend
that displays a week view intended for a wall-mounted display.

> **Status: early-stage prototype.** This is still in the exploring/tinkering
> phase, not a finished product. Expect rough edges, missing tests, and
> pragmatic shortcuts taken to move fast rather than "correct" long-term
> decisions — things will get cleaned up as the shape of the app settles.

## Stack

- Backend: FastAPI (Python), Google Calendar/Tasks API via `google-api-python-client`
- Frontend: React + TypeScript + Vite + Tailwind

## Setup

### 1. Google Cloud project

The app needs a Google Cloud project with OAuth credentials that can access
each family member's Calendar and Tasks data.

1. Create (or reuse) a project at [console.cloud.google.com](https://console.cloud.google.com).
2. Enable these APIs (**APIs & Services → Library**):
   - **Google Calendar API**
   - **Google Tasks API**
3. Configure the **OAuth consent screen** (**APIs & Services → OAuth consent screen**):
   - User type: **External** (personal Google accounts, not Workspace, can't use Internal)
   - Publishing status: **Testing** is fine — this is a private family app, not something
     to submit for Google verification
   - Scopes: add `.../auth/calendar` and `.../auth/tasks` (full read/write, not the
     `.readonly` variants — the app creates/updates events and completes tasks)
   - Test users: add the Google account **email address of every family member** who
     will connect a calendar. In Testing mode, only accounts listed here can complete
     the OAuth flow.
4. Create credentials (**APIs & Services → Credentials → Create Credentials → OAuth client ID**):
   - Application type: **Web application**
   - Authorized redirect URI: `<APP_URL>/auth/callback`, e.g. `http://localhost:8000/auth/callback`
     for local dev. This must exactly match `APP_URL` in your `.env` (see below) — the
     app derives its callback URL from that variable, not a hardcoded value.
   - Save the generated **Client ID** and **Client Secret**.

### 2. Local config

```
cp .env.example .env
```

Fill in:
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — from step 1.4 above
- `APP_URL` — must match the redirect URI you registered in Google Cloud
- `SECRET_KEY` — any random string
- `TZ` — timezone for the calendar display
- `AUTH_USERNAME` / `AUTH_PASSWORD` — shared credentials gating access to the
  whole app (HTTP Basic Auth). The app refuses to start without these set.
  When deploying to Cloud Run, set them as real secrets (e.g. via Secret
  Manager or `--set-env-vars`) rather than leaving the placeholder values.

Customize family members in `backend/config.py` (currently placeholder entries).

### 3. Run it

```
docker compose up
```

- API: http://localhost:8000
- Frontend: http://localhost:5173

Then visit `http://localhost:8000/auth/setup` and connect each family member's
Google account (must be one of the test users added in step 1.3).

## Deploying to Cloud Run

Infrastructure (Cloud Run service, GCS bucket for OAuth tokens, Secret Manager
secrets) is provisioned with Terraform in [`infra/`](infra/README.md). Images
are built and pushed to Docker Hub automatically on push to `main` via
[`.github/workflows/docker-publish.yml`](.github/workflows/docker-publish.yml);
deploying a new image to Cloud Run is a separate, deliberate
`terraform apply -var="image_tag=<sha>"` step — see `infra/README.md` for the
full walkthrough, including the OAuth redirect URI setup.
