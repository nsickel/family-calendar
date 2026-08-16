import os

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SECRET_KEY = os.environ["SECRET_KEY"]

SESSION_COOKIE_NAME = "fc_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 30  # 30 days — single trusted wall-mounted device

_serializer = URLSafeTimedSerializer(SECRET_KEY, salt="fc-session-v1")


def create_session_token(family_id) -> str:
    return _serializer.dumps({"family_id": str(family_id)})


def verify_session_token(token: str) -> str | None:
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE_SECONDS)
    except (BadSignature, SignatureExpired):
        return None
    return data.get("family_id")
