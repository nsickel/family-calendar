import os
from google_auth_oauthlib.flow import Flow
from config import GOOGLE_SCOPES


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
