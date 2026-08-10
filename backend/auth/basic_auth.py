import base64
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

EXEMPT_PATHS = {"/health"}


class BasicAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, username: str, password: str):
        super().__init__(app)
        self.username = username
        self.password = password

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        if self._is_authorized(request.headers.get("authorization")):
            return await call_next(request)

        return Response(
            status_code=401,
            content="Authentication required",
            headers={"WWW-Authenticate": 'Basic realm="Family Calendar"'},
        )

    def _is_authorized(self, auth_header: str | None) -> bool:
        if not auth_header:
            return False
        scheme, _, encoded = auth_header.partition(" ")
        if scheme.lower() != "basic":
            return False
        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
        except Exception:
            return False
        username, _, password = decoded.partition(":")
        return secrets.compare_digest(username, self.username) and secrets.compare_digest(
            password, self.password
        )
