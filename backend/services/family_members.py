import uuid
from sqlalchemy import select
from db import engine, family_members_table


def get_family_members(family_id) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(
            select(family_members_table)
            .where(family_members_table.c.family_id == family_id)
            .order_by(family_members_table.c.sort_order)
        ).mappings().all()
    return [dict(r) for r in rows]


def get_member(member_id) -> dict | None:
    # member_id often comes straight from request payloads / OAuth `state` —
    # reject non-UUID input here rather than letting it hit the DB as an
    # invalid-uuid-syntax error.
    try:
        uuid.UUID(str(member_id))
    except ValueError:
        return None
    with engine.connect() as conn:
        row = conn.execute(
            select(family_members_table).where(family_members_table.c.id == member_id)
        ).mappings().first()
    return dict(row) if row else None


def get_member_by_slug(family_id, slug: str) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(
            select(family_members_table).where(
                family_members_table.c.family_id == family_id,
                family_members_table.c.slug == slug,
            )
        ).mappings().first()
    return dict(row) if row else None
