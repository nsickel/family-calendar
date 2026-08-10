import type { WeekData, NewEventPayload } from "./types";

const BASE = "";

export async function fetchWeek(date?: string): Promise<WeekData> {
  const url = date ? `/api/week?date=${date}` : "/api/week";
  const res = await fetch(BASE + url);
  if (!res.ok) throw new Error(`Failed to fetch week: ${res.status}`);
  return res.json();
}

export async function createEvent(payload: NewEventPayload): Promise<void> {
  const res = await fetch(BASE + "/api/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to create event: ${res.status}`);
}

export async function updateEvent(eventId: string, payload: Partial<NewEventPayload> & { account_id: string }): Promise<void> {
  const res = await fetch(BASE + `/api/events/${eventId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to update event: ${res.status}`);
}

export async function completeTask(taskId: string, accountId: string, tasklistId: string): Promise<void> {
  const res = await fetch(BASE + `/api/tasks/${taskId}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ account_id: accountId, tasklist_id: tasklistId }),
  });
  if (!res.ok) throw new Error(`Failed to complete task: ${res.status}`);
}
