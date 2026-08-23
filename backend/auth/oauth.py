import os
from google_auth_oauthlib.flow import Flow
from config import GOOGLE_SCOPES

# Members who previously connected still have the now-removed `tasks` scope
# on their Google grant; since /auth/connect uses include_granted_scopes,
# Google echoes that extra scope back on reconnect even though we only ask
# for `calendar`. oauthlib treats any scope mismatch as a hard error unless
# told to relax — this is the documented fix (not a security bypass, just
# stops oauthlib from rejecting a superset of the requested scope).
os.environ.setdefault("OAUTHLIB_RELAX_TOKEN_SCOPE", "1")


def build_flow(account_id: str, redirect_uri: str) -> Flow:
    client_config = {
        "web": {
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "redirect_uris": [redirect_uri],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=GOOGLE_SCOPES,
        state=account_id,
    )
    flow.redirect_uri = redirect_uri
    return flow
