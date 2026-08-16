import threading
import time

MAX_ATTEMPTS = 5
LOCKOUT_SECONDS = 15 * 60

_lock = threading.Lock()
_state: dict[str, dict] = {}  # username(lower) -> {"failures": int, "locked_until": float | None}


def is_locked_out(username: str) -> tuple[bool, int]:
    key = username.lower()
    with _lock:
        entry = _state.get(key)
        if not entry or not entry.get("locked_until"):
            return False, 0
        remaining = entry["locked_until"] - time.monotonic()
        if remaining <= 0:
            _state.pop(key, None)
            return False, 0
        return True, int(remaining)


def record_failure(username: str) -> None:
    key = username.lower()
    with _lock:
        entry = _state.setdefault(key, {"failures": 0, "locked_until": None})
        entry["failures"] += 1
        if entry["failures"] >= MAX_ATTEMPTS:
            entry["locked_until"] = time.monotonic() + LOCKOUT_SECONDS
            entry["failures"] = 0


def record_success(username: str) -> None:
    with _lock:
        _state.pop(username.lower(), None)
