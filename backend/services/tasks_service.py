import asyncio
import os
from datetime import date, datetime, timezone, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

_LOCAL_TZ_OFFSET = int(os.environ.get("TZ_OFFSET_HOURS", "1"))


def _build_service(credentials: Credentials):
    return build("tasks", "v1", credentials=credentials, cache_discovery=False)


def _parse_due_date(due_str: str | None) -> str | None:
    if not due_str:
        return None
    # Google Tasks returns due as RFC3339 at midnight UTC
    dt = datetime.fromisoformat(due_str.replace("Z", "+00:00"))
    # Shift to local time so "Monday midnight UTC" → correct local date
    local_dt = dt + timedelta(hours=_LOCAL_TZ_OFFSET)
    return local_dt.date().isoformat()


def _normalize_task(item: dict, tasklist_id: str, member: dict) -> dict:
    return {
        "id": item["id"],
        "tasklist_id": tasklist_id,
        "account_id": member["id"],
        "title": item.get("title", "(no title)"),
        "emoji": member["emoji"],
        "color": member["color"],
        "completed": item.get("status") == "completed",
        "due": _parse_due_date(item.get("due")),
        "source": "tasks",
    }


async def get_tasks(credentials: Credentials, member: dict, start_dt: date, end_dt: date) -> list[dict]:
    def _fetch():
        service = _build_service(credentials)
        tasklists = service.tasklists().list(maxResults=20).execute()
        tasks = []
        for tl in tasklists.get("items", []):
            tl_id = tl["id"]
            result = (
                service.tasks()
                .list(
                    tasklist=tl_id,
                    showCompleted=False,
                    showHidden=False,
                    maxResults=100,
                )
                .execute()
            )
            for item in result.get("items", []):
                task = _normalize_task(item, tl_id, member)
                due = task["due"]
                # Include tasks due within the week, or tasks with no due date shown on current day
                if due is None or (start_dt.isoformat() <= due <= end_dt.isoformat()):
                    tasks.append(task)
        return tasks

    return await asyncio.get_event_loop().run_in_executor(None, _fetch)


async def complete_task(credentials: Credentials, tasklist_id: str, task_id: str) -> dict:
    def _complete():
        service = _build_service(credentials)
        task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        task["status"] = "completed"
        return service.tasks().update(tasklist=tasklist_id, task=task_id, body=task).execute()

    return await asyncio.get_event_loop().run_in_executor(None, _complete)
