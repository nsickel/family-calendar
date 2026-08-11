import base64

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from auth.family_store import get_family_by_username
from auth.hashing import verify_password

EXEMPT_PATHS = {"/health"}


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        family = self._authorize(request.headers.get("authorization"))
        if family is None:
            return Response(
                status_code=401,
                content="Authentication required",
                headers={"WWW-Authenticate": 'Basic realm="Family Calendar"'},
            )

        request.state.family_id = family["family_id"]
        return await call_next(request)

    def _authorize(self, auth_header: str | None) -> dict | None:
        if not auth_header:
            return None
        scheme, _, encoded = auth_header.partition(" ")
        if scheme.lower() != "basic":
            return None
        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
        except Exception:
            return None
        username, _, password = decoded.partition(":")

        family = get_family_by_username(username)
        if family is None:
            return None
        if not verify_password(password, family["password_hash"]):
            return None
        return family
