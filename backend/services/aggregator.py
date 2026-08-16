import asyncio
import logging
from datetime import date, timedelta
from services.family_members import get_family_members
from auth.token_store import get_valid_credentials
from services.calendar_service import get_events
from services.tasks_service import get_tasks

logger = logging.getLogger(__name__)


async def get_week_data(week_start: date, family_id) -> dict:
    week_end = week_start + timedelta(days=6)

    # Build connected member list
    member_status = []
    for m in get_family_members(family_id):
        creds = get_valid_credentials(str(m["id"]))
        member_status.append({**m, "connected": creds is not None, "_creds": creds})

    # Fetch all events and tasks in parallel
    event_tasks = []
    task_tasks = []
    for ms in member_status:
        if ms["_creds"]:
            event_tasks.append(get_events(ms["_creds"], ms, week_start, week_end))
            task_tasks.append(get_tasks(ms["_creds"], ms, week_start, week_end))
        else:
            event_tasks.append(_empty())
            task_tasks.append(_empty())

    all_results = await asyncio.gather(*event_tasks, *task_tasks, return_exceptions=True)

    n = len(member_status)
    raw_events = all_results[:n]
    raw_tasks = all_results[n:]

    # Flatten, logging (rather than silently dropping) any exceptions
    events: list[dict] = []
    tasks: list[dict] = []
    for ms, r in zip(member_status, raw_events):
        if isinstance(r, list):
            events.extend(r)
        elif isinstance(r, Exception):
            logger.warning("Failed to fetch events for %s: %r", ms["id"], r)
    for ms, r in zip(member_status, raw_tasks):
        if isinstance(r, list):
            tasks.extend(r)
        elif isinstance(r, Exception):
            logger.warning("Failed to fetch tasks for %s: %r", ms["id"], r)

    # Build day buckets
    days = []
    today = date.today()
    for i in range(7):
        d = week_start + timedelta(days=i)
        d_str = d.isoformat()
        day_events = sorted(
            [e for e in events if e["date"] == d_str],
            key=lambda e: (e["start_time"] or "00:00"),
        )
        # Tasks with a due date on this day, plus tasks with no due date shown on today
        day_tasks = [
            t for t in tasks
            if t["due"] == d_str or (t["due"] is None and d == today)
        ]
        days.append({
            "date": d_str,
            "weekday": d.strftime("%A"),
            "day_number": d.day,
            "month_name": d.strftime("%B"),
            "is_today": d == today,
            "events": day_events,
            "tasks": day_tasks,
        })

    members_out = [
        {"id": ms["id"], "name": ms["name"], "emoji": ms["emoji"], "color": ms["color"], "connected": ms["connected"]}
        for ms in member_status
    ]

    return {
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "days": days,
        "members": members_out,
    }


async def _empty():
    return []
