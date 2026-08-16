from sqlalchemy import select

from db import engine, families_table


def get_family_by_username(username: str) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(
            select(families_table.c.id, families_table.c.password_hash).where(
                families_table.c.username == username
            )
        ).first()
    if row is None:
        return None
    return {"family_id": row.id, "password_hash": row.password_hash}
