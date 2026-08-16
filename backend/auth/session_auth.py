import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from auth.session_cookie import SESSION_COOKIE_NAME, verify_session_token

EXEMPT_PATHS = {"/health", "/auth/login", "/auth/logout"}


def _requires_session(path: str) -> bool:
    if path in EXEMPT_PATHS:
        return False
    if path.startswith("/api/"):
        return True
    if path.startswith("/auth/"):
        return True
    return False


class SessionAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not _requires_session(request.url.path):
            return await call_next(request)

        token = request.cookies.get(SESSION_COOKIE_NAME)
        family_id_str = verify_session_token(token) if token else None
        if family_id_str is None:
            return JSONResponse({"error": "authentication required"}, status_code=401)

        request.state.family_id = uuid.UUID(family_id_str)
        return await call_next(request)
