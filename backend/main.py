import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth.session_auth import SessionAuthMiddleware

# Explicit redirect URI avoids mismatch when accessed through a proxy (e.g. Vite dev server)
_APP_URL = os.environ.get("APP_URL", "http://localhost:8000").rstrip("/")
REDIRECT_URI = f"{_APP_URL}/auth/callback"


app = FastAPI(title="Family Calendar")

# Gate /api/* and /auth/* (except login/logout) behind a signed session
# cookie, backed by the `families` table (see auth/family_store.py) so the
# calendar isn't publicly viewable once deployed. The SPA shell itself
# (`/`, `/assets/*`) stays public so the login page can render.
app.add_middleware(SessionAuthMiddleware)

# Mount static files if the React build exists (production)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir)) if templates_dir.exists() else None


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/week")
async def week(request: Request, date: str | None = None):
    from services.aggregator import get_week_data
    from datetime import date as date_cls, timedelta

    if date:
        week_start = date_cls.fromisoformat(date)
        # Snap to Monday
        week_start = week_start - timedelta(days=week_start.weekday())
    else:
        today = date_cls.today()
        week_start = today - timedelta(days=today.weekday())

    return await get_week_data(week_start, request.state.family_id)


@app.post("/api/events")
async def create_event(request: Request, payload: dict):
    from googleapiclient.errors import HttpError
    from services.calendar_service import create_event as svc_create
    from services.family_members import get_member
    from auth.token_store import get_valid_credentials

    member = get_member(payload["account_id"])
    if member is None or member["family_id"] != request.state.family_id:
        return JSONResponse({"error": "account not found"}, status_code=404)

    creds = get_valid_credentials(payload["account_id"])
    if not creds:
        return JSONResponse({"error": "account not connected"}, status_code=400)
    try:
        return await svc_create(creds, payload)
    except HttpError:
        return JSONResponse(
            {"error": "Google rejected the request — try reconnecting this account at /auth/setup"},
            status_code=502,
        )


@app.put("/api/events/{event_id}")
async def update_event(event_id: str, request: Request, payload: dict):
    from googleapiclient.errors import HttpError
    from services.calendar_service import update_event as svc_update
    from services.family_members import get_member
    from auth.token_store import get_valid_credentials

    member = get_member(payload["account_id"])
    if member is None or member["family_id"] != request.state.family_id:
        return JSONResponse({"error": "account not found"}, status_code=404)

    creds = get_valid_credentials(payload["account_id"])
    if not creds:
        return JSONResponse({"error": "account not connected"}, status_code=400)
    try:
        return await svc_update(creds, event_id, payload)
    except HttpError:
        return JSONResponse(
            {"error": "Google rejected the request — try reconnecting this account at /auth/setup"},
            status_code=502,
        )


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: str, request: Request, payload: dict):
    from googleapiclient.errors import HttpError
    from services.tasks_service import complete_task as svc_complete
    from services.family_members import get_member
    from auth.token_store import get_valid_credentials

    member = get_member(payload["account_id"])
    if member is None or member["family_id"] != request.state.family_id:
        return JSONResponse({"error": "account not found"}, status_code=404)

    creds = get_valid_credentials(payload["account_id"])
    if not creds:
        return JSONResponse({"error": "account not connected"}, status_code=400)
    try:
        return await svc_complete(creds, payload["tasklist_id"], task_id)
    except HttpError:
        return JSONResponse(
            {"error": "Google rejected the request — try reconnecting this account at /auth/setup"},
            status_code=502,
        )


# Auth routes
@app.post("/auth/login")
async def login(payload: dict):
    from auth.family_store import get_family_by_username
    from auth.hashing import verify_password
    from auth.rate_limit import is_locked_out, record_failure, record_success
    from auth.session_cookie import (
        SESSION_COOKIE_NAME,
        SESSION_MAX_AGE_SECONDS,
        create_session_token,
    )

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    locked, retry_after = is_locked_out(username)
    if locked:
        return JSONResponse(
            {"error": "too many failed attempts", "retry_after": retry_after},
            status_code=429,
        )

    family = get_family_by_username(username)
    if family is None or not verify_password(password, family["password_hash"]):
        record_failure(username)
        return JSONResponse({"error": "invalid username or password"}, status_code=401)

    record_success(username)
    resp = JSONResponse({"status": "ok"})
    resp.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_token(family["family_id"]),
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=_APP_URL.startswith("https://"),
        samesite="lax",
        path="/",
    )
    return resp


@app.post("/auth/logout")
async def logout():
    from auth.session_cookie import SESSION_COOKIE_NAME

    resp = JSONResponse({"status": "ok"})
    resp.delete_cookie(SESSION_COOKIE_NAME, path="/")
    return resp


@app.get("/auth/setup", response_class=HTMLResponse)
async def auth_setup(request: Request):
    from services.family_members import get_family_members
    from auth.token_store import get_valid_credentials
    members = [
        {**m, "connected": get_valid_credentials(str(m["id"])) is not None}
        for m in get_family_members(request.state.family_id)
    ]
    html = _setup_page(members, str(request.base_url))
    return HTMLResponse(html)


@app.get("/auth/connect/{slug}")
async def auth_connect(slug: str, request: Request):
    from services.family_members import get_member_by_slug
    from auth.oauth import build_flow
    from fastapi.responses import RedirectResponse

    member = get_member_by_slug(request.state.family_id, slug)
    if member is None:
        return JSONResponse({"error": "unknown member"}, status_code=404)

    flow = build_flow(str(member["id"]), REDIRECT_URI)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return RedirectResponse(auth_url)


@app.get("/auth/callback")
async def auth_callback(code: str, state: str, request: Request):
    from services.family_members import get_member
    from auth.oauth import build_flow
    from auth.token_store import save_token
    from fastapi.responses import RedirectResponse

    member = get_member(state)
    if member is None or member["family_id"] != request.state.family_id:
        return JSONResponse({"error": "invalid or mismatched account"}, status_code=403)

    flow = build_flow(state, REDIRECT_URI)
    flow.fetch_token(code=code)
    save_token(state, flow.credentials)
    return RedirectResponse("/auth/setup")


# Serve React app for all unmatched routes (production SPA)
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_spa(full_path: str):
    index = static_dir / "index.html"
    if index.exists():
        return HTMLResponse(index.read_text())
    return HTMLResponse("<h1>Family Calendar API</h1><p>Visit <a href='/auth/setup'>/auth/setup</a> to connect Google accounts.</p>")


def _setup_page(members: list, base_url: str) -> str:
    rows = ""
    for m in members:
        status = "✅ Connected" if m["connected"] else "❌ Not connected"
        label = "Reconnect" if m["connected"] else "Connect"
        btn = f'<a href="/auth/connect/{m["slug"]}" style="margin-left:12px;padding:8px 16px;background:#4285F4;color:white;border-radius:8px;text-decoration:none">{label}</a>'
        rows += f'<tr><td style="padding:12px;font-size:1.5rem">{m["emoji"]}</td><td style="padding:12px;font-weight:700">{m["name"]}</td><td style="padding:12px">{status}{btn}</td></tr>'
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Family Calendar — Auth Setup</title>
<style>body{{font-family:sans-serif;max-width:600px;margin:40px auto;padding:0 20px}}
table{{border-collapse:collapse;width:100%}}td{{border-bottom:1px solid #eee}}</style>
</head><body>
<h1>🗓️ Family Calendar Setup</h1>
<p>Connect each family member's Google account once. Tokens are stored in Postgres.</p>
<table>{rows}</table>
<p style="margin-top:24px"><a href="/">← Back to calendar</a></p>
</body></html>"""
