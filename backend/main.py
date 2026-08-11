import os
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth.basic_auth import BasicAuthMiddleware

load_dotenv()

# Explicit redirect URI avoids mismatch when accessed through a proxy (e.g. Vite dev server)
_APP_URL = os.environ.get("APP_URL", "http://localhost:8000").rstrip("/")
REDIRECT_URI = f"{_APP_URL}/auth/callback"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from auth.family_store import load_cache
    load_cache()
    yield


app = FastAPI(title="Family Calendar", lifespan=lifespan)

# Gate the whole app behind per-family HTTP Basic Auth, backed by the
# `families` table (see auth/family_store.py) so the calendar isn't publicly
# viewable once deployed.
app.add_middleware(BasicAuthMiddleware)

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
