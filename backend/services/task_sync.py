import logging
from datetime import date, datetime, timedelta
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from auth.token_store import get_valid_credentials
from services import calendar_service, task_store

logger = logging.getLogger(__name__)

# Google API/auth failures we treat as "this member's calendar is
# unreachable right now" rather than letting them 500 the whole request —
# the task itself still persists locally and sync is retried on next save.
_SYNC_ERRORS = (HttpError, RefreshError)

TASK_EVENT_DURATION_MINUTES = 30
_ICAL_WEEKDAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def _rrule_for(recurrence: str | None, start_date: date) -> str | None:
    if recurrence == "daily":
        return "RRULE:FREQ=DAILY"
    if recurrence == "weekdays":
        return "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"
    if recurrence == "weekly":
        return f"RRULE:FREQ=WEEKLY;BYDAY={_ICAL_WEEKDAYS[start_date.weekday()]}"
    return None


def _calendar_payload(task: dict) -> dict:
    start_date = task["start_date"]
    payload = {"title": task["title"], "date": start_date.isoformat()}
    if task["start_time"]:
        payload["all_day"] = False
        payload["start_time"] = task["start_time"]
        end = datetime.strptime(task["start_time"], "%H:%M") + timedelta(minutes=TASK_EVENT_DURATION_MINUTES)
        payload["end_time"] = end.strftime("%H:%M")
    else:
        payload["all_day"] = True
    payload["recurrence"] = _rrule_for(task["recurrence"], start_date)
    return payload


async def sync_task_assignees(task: dict, member_ids: set) -> None:
    """Reconcile Calendar events so exactly `member_ids` have an event
    reflecting the task's current title/start_date/start_time/recurrence."""
    member_ids = {str(m) for m in member_ids}
    links = {str(l["member_id"]): l for l in task_store.get_task_links(task["id"])}
    existing = set(links.keys())
    payload = _calendar_payload(task)

    for member_id in existing - member_ids:
        await _delete_link(task["id"], member_id, links[member_id]["google_event_id"])
    for member_id in member_ids & existing:
        await _update_link(task["id"], member_id, links[member_id]["google_event_id"], payload)
    for member_id in member_ids - existing:
        await _create_link(task["id"], member_id, payload)


async def delete_task_calendar_events(task_id) -> None:
    """Best-effort delete every Calendar event linked to this task. Call this
    BEFORE task_store.delete_task(task_id) so links are still readable."""
    for link in task_store.get_task_links(task_id):
        await _delete_link(task_id, link["member_id"], link["google_event_id"], remove_row=False)


async def _create_link(task_id, member_id, payload) -> None:
    creds = get_valid_credentials(str(member_id))
    if not creds:
        logger.warning("Skipping calendar sync for member %s: not connected", member_id)
        return
    try:
        event = await calendar_service.create_event(creds, payload)
    except _SYNC_ERRORS:
        logger.exception("Failed to create calendar event for task %s / member %s", task_id, member_id)
        return
    task_store.upsert_task_link(task_id, member_id, event["id"])


async def _update_link(task_id, member_id, event_id, payload) -> None:
    creds = get_valid_credentials(str(member_id))
    if not creds:
        logger.warning("Skipping calendar update for member %s: not connected", member_id)
        return
    try:
        await calendar_service.update_event(creds, event_id, payload)
    except _SYNC_ERRORS:
        logger.exception("Failed to update calendar event %s for task %s", event_id, task_id)


async def _delete_link(task_id, member_id, event_id, remove_row: bool = True) -> None:
    creds = get_valid_credentials(str(member_id))
    if creds:
        try:
            await calendar_service.delete_event(creds, event_id)
        except _SYNC_ERRORS:
            logger.exception("Failed to delete calendar event %s for task %s", event_id, task_id)
    if remove_row:
        task_store.delete_task_link(task_id, member_id)
