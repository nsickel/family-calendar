from sqlalchemy import select
from db import engine, families_table

_cache: dict[str, dict] = {}


def load_cache() -> None:
    with engine.connect() as conn:
        rows = conn.execute(
            select(families_table.c.username, families_table.c.id, families_table.c.password_hash)
        ).all()
    _cache.clear()
    for username, family_id, password_hash in rows:
        _cache[username] = {"family_id": family_id, "password_hash": password_hash}


def get_family_by_username(username: str) -> dict | None:
    cached = _cache.get(username)
    if cached is not None:
        return cached

    with engine.connect() as conn:
        row = conn.execute(
            select(families_table.c.id, families_table.c.password_hash).where(
                families_table.c.username == username
            )
        ).first()
    if row is None:
        return None

    family = {"family_id": row.id, "password_hash": row.password_hash}
    _cache[username] = family
    return family
