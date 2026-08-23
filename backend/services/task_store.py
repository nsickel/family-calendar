import uuid
from datetime import date, datetime, time, timezone
from dateutil.rrule import rrule, DAILY, WEEKLY
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from db import (
    engine,
    tasks_table,
    task_assignees_table,
    task_calendar_links_table,
    task_completions_table,
    family_members_table,
)


def create_task(family_id, title: str, start_date: date, start_time: str | None,
                 recurrence: str | None, member_ids: list[str]) -> dict:
    with engine.begin() as conn:
        row = conn.execute(
            tasks_table.insert()
            .values(
                family_id=family_id,
                title=title,
                start_date=start_date,
                start_time=start_time,
                recurrence=recurrence,
            )
            .returning(tasks_table)
        ).mappings().first()
        task_id = row["id"]
        if member_ids:
            conn.execute(
                task_assignees_table.insert(),
                [{"task_id": task_id, "member_id": mid} for mid in member_ids],
            )
    return dict(row)


def update_task(task_id, title: str, start_date: date, start_time: str | None,
                 recurrence: str | None) -> dict:
    with engine.begin() as conn:
        row = conn.execute(
            tasks_table.update()
            .where(tasks_table.c.id == task_id)
            .values(
                title=title,
                start_date=start_date,
                start_time=start_time,
                recurrence=recurrence,
                updated_at=datetime.now(timezone.utc),
            )
            .returning(tasks_table)
        ).mappings().first()
    return dict(row)


def delete_task(task_id) -> None:
    with engine.begin() as conn:
        conn.execute(delete(tasks_table).where(tasks_table.c.id == task_id))


def get_task(task_id) -> dict | None:
    try:
        uuid.UUID(str(task_id))
    except ValueError:
        return None
    with engine.connect() as conn:
        row = conn.execute(
            select(tasks_table).where(tasks_table.c.id == task_id)
        ).mappings().first()
    return dict(row) if row else None


def _assignees_for(conn, task_ids: list) -> dict:
    if not task_ids:
        return {}
    rows = conn.execute(
        select(
            task_assignees_table.c.task_id,
            family_members_table.c.id,
            family_members_table.c.name,
            family_members_table.c.emoji,
            family_members_table.c.color,
        )
        .select_from(
            task_assignees_table.join(
                family_members_table,
                family_members_table.c.id == task_assignees_table.c.member_id,
            )
        )
        .where(task_assignees_table.c.task_id.in_(task_ids))
    ).mappings().all()
    by_task: dict = {}
    for r in rows:
        by_task.setdefault(r["task_id"], []).append(
            {"id": r["id"], "name": r["name"], "emoji": r["emoji"], "color": r["color"]}
        )
    return by_task


def get_task_with_assignees(task_id) -> dict | None:
    task = get_task(task_id)
    if task is None:
        return None
    with engine.connect() as conn:
        by_task = _assignees_for(conn, [task["id"]])
    return {**task, "assignees": by_task.get(task["id"], [])}


def get_family_tasks(family_id) -> list[dict]:
    with engine.connect() as conn:
        task_rows = conn.execute(
            select(tasks_table).where(tasks_table.c.family_id == family_id)
        ).mappings().all()
        task_ids = [t["id"] for t in task_rows]
        by_task = _assignees_for(conn, task_ids)
    return [{**dict(t), "assignees": by_task.get(t["id"], [])} for t in task_rows]


def set_task_assignees(task_id, member_ids: list[str]) -> None:
    with engine.begin() as conn:
        conn.execute(delete(task_assignees_table).where(task_assignees_table.c.task_id == task_id))
        if member_ids:
            conn.execute(
                task_assignees_table.insert(),
                [{"task_id": task_id, "member_id": mid} for mid in member_ids],
            )


def get_task_links(task_id) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(
            select(task_calendar_links_table).where(task_calendar_links_table.c.task_id == task_id)
        ).mappings().all()
    return [dict(r) for r in rows]


def upsert_task_link(task_id, member_id, google_event_id: str, calendar_id: str = "primary") -> None:
    stmt = pg_insert(task_calendar_links_table).values(
        task_id=task_id,
        member_id=member_id,
        google_event_id=google_event_id,
        calendar_id=calendar_id,
        updated_at=datetime.now(timezone.utc),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["task_id", "member_id"],
        set_={
            "google_event_id": stmt.excluded.google_event_id,
            "calendar_id": stmt.excluded.calendar_id,
            "updated_at": stmt.excluded.updated_at,
        },
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def delete_task_link(task_id, member_id) -> None:
    with engine.begin() as conn:
        conn.execute(
            delete(task_calendar_links_table).where(
                task_calendar_links_table.c.task_id == task_id,
                task_calendar_links_table.c.member_id == member_id,
            )
        )


def get_completed_occurrences(task_ids: list, range_start: date, range_end: date) -> set:
    if not task_ids:
        return set()
    with engine.connect() as conn:
        rows = conn.execute(
            select(task_completions_table.c.task_id, task_completions_table.c.occurrence_date).where(
                task_completions_table.c.task_id.in_(task_ids),
                task_completions_table.c.occurrence_date >= range_start,
                task_completions_table.c.occurrence_date <= range_end,
            )
        ).mappings().all()
    return {(str(r["task_id"]), r["occurrence_date"]) for r in rows}


def mark_occurrence_complete(task_id, occurrence_date: date, completed_by=None) -> None:
    stmt = pg_insert(task_completions_table).values(
        task_id=task_id,
        occurrence_date=occurrence_date,
        completed_by=completed_by,
    )
    stmt = stmt.on_conflict_do_nothing(index_elements=["task_id", "occurrence_date"])
    with engine.begin() as conn:
        conn.execute(stmt)


def expand_occurrences(task: dict, range_start: date, range_end: date) -> list[date]:
    recurrence = task.get("recurrence")
    start_date = task["start_date"]
    if recurrence is None:
        return [start_date] if range_start <= start_date <= range_end else []

    dtstart = datetime.combine(start_date, time.min)
    if recurrence == "daily":
        rule = rrule(DAILY, dtstart=dtstart)
    elif recurrence == "weekdays":
        rule = rrule(WEEKLY, dtstart=dtstart, byweekday=(0, 1, 2, 3, 4))
    elif recurrence == "weekly":
        rule = rrule(WEEKLY, dtstart=dtstart, byweekday=start_date.weekday())
    else:
        return []

    window_start = datetime.combine(range_start, time.min)
    window_end = datetime.combine(range_end, time.max)
    return [dt.date() for dt in rule.between(window_start, window_end, inc=True)]
