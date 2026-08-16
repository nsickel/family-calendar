from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from db import engine, oauth_tokens_table

_UPSERT_COLUMNS = (
    "access_token",
    "refresh_token",
    "token_uri",
    "client_id",
    "client_secret",
    "scopes",
    "expiry",
    "updated_at",
)


def save_token(account_id: str, credentials: Credentials) -> None:
    expiry = credentials.expiry
    if expiry is not None and expiry.tzinfo is None:
        # google-auth's Credentials.expiry is naive UTC (see google.auth._helpers.utcnow);
        # attach tzinfo explicitly so it isn't misread as the DB session's local time.
        expiry = expiry.replace(tzinfo=timezone.utc)
    stmt = pg_insert(oauth_tokens_table).values(
        account_id=account_id,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scopes=list(credentials.scopes or []),
        expiry=expiry,
        updated_at=datetime.now(timezone.utc),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["account_id"],
        set_={col: stmt.excluded[col] for col in _UPSERT_COLUMNS},
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def load_token(account_id: str) -> Credentials | None:
    with engine.connect() as conn:
        row = conn.execute(
            select(oauth_tokens_table).where(oauth_tokens_table.c.account_id == account_id)
        ).mappings().first()
    if row is None:
        return None
    expiry = row["expiry"]
    if expiry is not None and expiry.tzinfo is not None:
        # google-auth compares Credentials.expiry against a naive UTC "now"
        # (see google.auth._helpers.utcnow), so strip the tzinfo Postgres adds back.
        expiry = expiry.astimezone(timezone.utc).replace(tzinfo=None)
    return Credentials(
        token=row["access_token"],
        refresh_token=row["refresh_token"],
        token_uri=row["token_uri"],
        client_id=row["client_id"],
        client_secret=row["client_secret"],
        scopes=row["scopes"],
        expiry=expiry,
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
