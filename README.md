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

## Running it

```
docker compose up
```

- API: http://localhost:8000
- Frontend: http://localhost:5173

You'll need a `.env` file (see `.env.example`) with Google OAuth credentials
configured in Google Cloud Console.
