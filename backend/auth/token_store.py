import json
import os
from datetime import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

TOKENS_DIR = Path(os.environ.get("TOKENS_DIR", "/app/tokens"))


def _token_path(account_id: str) -> Path:
    return TOKENS_DIR / f"{account_id}.json"


def save_token(account_id: str, credentials: Credentials) -> None:
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes or []),
        "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
    }
    _token_path(account_id).write_text(json.dumps(data))


def load_token(account_id: str) -> Credentials | None:
    path = _token_path(account_id)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    expiry = data.get("expiry")
    return Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
        expiry=datetime.fromisoformat(expiry) if expiry else None,
    )


def refresh_if_needed(account_id: str, credentials: Credentials) -> Credentials | None:
    try:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            save_token(account_id, credentials)
        return credentials
    except RefreshError:
        return None


def get_valid_credentials(account_id: str) -> Credentials | None:
    creds = load_token(account_id)
    if creds is None:
        return None
    return refresh_if_needed(account_id, creds)
