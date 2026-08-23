import asyncio
import logging
from datetime import date, timedelta
from services.family_members import get_family_members
from auth.token_store import get_valid_credentials
from services.calendar_service import get_events
from services.task_store import get_family_tasks, expand_occurrences, get_completed_occurrences

logger = logging.getLogger(__name__)


def _serialize_task_occurrence(task: dict, occurrence_date: date) -> dict:
    return {
        "id": str(task["id"]),
        "title": task["title"],
        "start_date": task["start_date"].isoformat(),
        "occurrence_date": occurrence_date.isoformat(),
        "start_time": task["start_time"],
        "recurrence": task["recurrence"] or "none",
        "assignees": task["assignees"],
        "source": "local",
    }


async def get_week_data(week_start: date, family_id) -> dict:
    week_end = week_start + timedelta(days=6)

    # Build connected member list
    member_status = []
    for m in get_family_members(family_id):
        creds = get_valid_credentials(str(m["id"]))
        member_status.append({**m, "connected": creds is not None, "_creds": creds})

    # Fetch all events in parallel
    event_tasks = []
    for ms in member_status:
        if ms["_creds"]:
            event_tasks.append(get_events(ms["_creds"], ms, week_start, week_end))
        else:
            event_tasks.append(_empty())

    raw_events = await asyncio.gather(*event_tasks, return_exceptions=True)

    # Flatten, logging (rather than silently dropping) any exceptions
    events: list[dict] = []
    for ms, r in zip(member_status, raw_events):
        if isinstance(r, list):
            events.extend(r)
        elif isinstance(r, Exception):
            logger.warning("Failed to fetch events for %s: %r", ms["id"], r)

    # Locally-persisted tasks: expand recurrence into this week's occurrences
    family_tasks = get_family_tasks(family_id)
    occurrences = [
        (t, d) for t in family_tasks for d in expand_occurrences(t, week_start, week_end)
    ]
    completed = get_completed_occurrences([str(t["id"]) for t, _ in occurrences], week_start, week_end)
    occurrences = [(t, d) for t, d in occurrences if (str(t["id"]), d) not in completed]

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
        day_tasks = [
            _serialize_task_occurrence(t, occ_date)
            for t, occ_date in occurrences
            if occ_date == d
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
