# family-calendar

Shared family wall-calendar app, multi-tenant: each family has its own login
and sees only its own members' calendars. FastAPI backend syncs Google
Calendar/Tasks per family member (config lives in Postgres, see
`backend/services/family_members.py`); React/Vite frontend displays a week
view for wall-mounted display.

## Run

```
docker compose up
```

- Backend: FastAPI, `backend/main.py`, served on :8000
- Frontend: Vite dev server, `frontend/`, served on :5173
- Postgres: `db` service (local `postgres:16` container), served on :5432

Local (non-docker) dev:
```
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

## Config

Copy `.env.example` to `.env` and fill in Google OAuth credentials and
`DATABASE_URL` (in prod, a Supabase Postgres Session Pooler URI; in local
`docker compose` dev, the `db` service's connection string is already set for
you in `docker-compose.yml`).

Persistence (OAuth tokens, family/member config, per-family login
credentials) lives entirely in Postgres — see `backend/db.py` for the schema
and `infra/README.md` for the production (Supabase) setup.

One-time setup after `docker compose up`:
```
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.create_family \
  --name "Your Family" --username yourfamily \
  --member "svenja:Svenja:👩:#FF6B9D" \
  --member "nils:Nils:👨:#4ECDC4" \
  --member "emelie:Emelie:👧:#FF6B9D"
```
Then log in at `/auth/setup` with those credentials and connect each family
member's Google account (per-member OAuth tokens land in the `oauth_tokens`
table).

There's no public self-service signup — `create_family.py` (admin-run, once
per new family) is the only way to provision a family. Login is per-family
HTTP Basic Auth backed by the `families` table, not a single shared
`AUTH_USERNAME`/`AUTH_PASSWORD` env var.
