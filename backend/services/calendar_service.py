import asyncio
from datetime import datetime, date, timezone
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def _build_service(credentials: Credentials):
    return build("calendar", "v3", credentials=credentials, cache_discovery=False)


def _normalize_event(item: dict, member: dict) -> dict:
    start = item.get("start", {})
    end = item.get("end", {})
    all_day = "date" in start and "dateTime" not in start

    if all_day:
        start_time = None
        end_time = None
        event_date = start["date"]
    else:
        dt_start = datetime.fromisoformat(start["dateTime"])
        dt_end = datetime.fromisoformat(end["dateTime"])
        start_time = dt_start.strftime("%H:%M")
        end_time = dt_end.strftime("%H:%M")
        event_date = dt_start.date().isoformat()

    return {
        "id": item["id"],
        "calendar_id": item.get("_calendar_id", "primary"),
        "account_id": member["id"],
        "title": item.get("summary", "(no title)"),
        "emoji": member["emoji"],
        "color": member["color"],
        "date": event_date,
        "start_time": start_time,
        "end_time": end_time,
        "all_day": all_day,
        "source": "calendar",
    }


async def get_events(credentials: Credentials, member: dict, start_dt: date, end_dt: date) -> list[dict]:
    def _fetch():
        service = _build_service(credentials)
        time_min = datetime.combine(start_dt, datetime.min.time()).isoformat() + "Z"
        time_max = datetime.combine(end_dt, datetime.max.time()).isoformat() + "Z"
        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
                maxResults=250,
            )
            .execute()
        )
        events = []
        for item in result.get("items", []):
            item["_calendar_id"] = "primary"
            events.append(_normalize_event(item, member))
        return events

    return await asyncio.get_event_loop().run_in_executor(None, _fetch)


async def create_event(credentials: Credentials, payload: dict) -> dict:
    def _create():
        service = _build_service(credentials)
        body: dict = {"summary": payload["title"]}
        if payload.get("all_day"):
            body["start"] = {"date": payload["date"]}
            body["end"] = {"date": payload.get("end_date", payload["date"])}
        else:
            body["start"] = {"dateTime": f"{payload['date']}T{payload['start_time']}:00", "timeZone": "Europe/Berlin"}
            body["end"] = {"dateTime": f"{payload['date']}T{payload['end_time']}:00", "timeZone": "Europe/Berlin"}
        return service.events().insert(calendarId="primary", body=body).execute()

    return await asyncio.get_event_loop().run_in_executor(None, _create)


async def update_event(credentials: Credentials, event_id: str, payload: dict) -> dict:
    def _update():
        service = _build_service(credentials)
        existing = service.events().get(calendarId="primary", eventId=event_id).execute()
        if "title" in payload:
            existing["summary"] = payload["title"]
        if "start_time" in payload:
            existing["start"] = {"dateTime": f"{payload['date']}T{payload['start_time']}:00", "timeZone": "Europe/Berlin"}
            existing["end"] = {"dateTime": f"{payload['date']}T{payload['end_time']}:00", "timeZone": "Europe/Berlin"}
        return service.events().update(calendarId="primary", eventId=event_id, body=existing).execute()

    return await asyncio.get_event_loop().run_in_executor(None, _update)
