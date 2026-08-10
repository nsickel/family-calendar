# family-calendar

Shared family wall-calendar app. FastAPI backend syncs Google Calendar/Tasks
per family member (see `backend/config.py`); React/Vite frontend displays a
week view for wall-mounted display.

## Run

```
docker compose up
```

- Backend: FastAPI, `backend/main.py`, served on :8000
- Frontend: Vite dev server, `frontend/`, served on :5173

Local (non-docker) dev:
```
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

## Config

Copy `.env.example` to `.env` and fill in Google OAuth credentials.
Per-member OAuth tokens are stored in `tokens/` (gitignored) after connecting
each account via the backend's auth flow.
