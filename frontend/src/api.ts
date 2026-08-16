import type { WeekData, NewEventPayload } from "./types";

const BASE = "";

type UnauthorizedHandler = () => void;
let onUnauthorized: UnauthorizedHandler | null = null;

export function setUnauthorizedHandler(fn: UnauthorizedHandler): void {
  onUnauthorized = fn;
}

async function apiFetch(url: string, opts: RequestInit = {}): Promise<Response> {
  const res = await fetch(url, { ...opts, credentials: "same-origin" });
  if (res.status === 401) {
    onUnauthorized?.();
  }
  return res;
}

export async function fetchWeek(date?: string): Promise<WeekData> {
  const url = date ? `/api/week?date=${date}` : "/api/week";
  const res = await apiFetch(BASE + url);
  if (!res.ok) throw new Error(`Failed to fetch week: ${res.status}`);
  return res.json();
}

export async function createEvent(payload: NewEventPayload): Promise<void> {
  const res = await apiFetch(BASE + "/api/events", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to create event: ${res.status}`);
}

export async function updateEvent(eventId: string, payload: Partial<NewEventPayload> & { account_id: string }): Promise<void> {
  const res = await apiFetch(BASE + `/api/events/${eventId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Failed to update event: ${res.status}`);
}

export async function completeTask(taskId: string, accountId: string, tasklistId: string): Promise<void> {
  const res = await apiFetch(BASE + `/api/tasks/${taskId}/complete`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ account_id: accountId, tasklist_id: tasklistId }),
  });
  if (!res.ok) throw new Error(`Failed to complete task: ${res.status}`);
}

export interface LoginError {
  error: string;
  retry_after?: number;
}

export async function login(username: string, password: string): Promise<LoginError | null> {
  const res = await fetch(BASE + "/auth/login", {
    method: "POST",
    credentials: "same-origin",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (res.ok) return null;
  return res.json();
}

export async function logout(): Promise<void> {
  await fetch(BASE + "/auth/logout", { method: "POST", credentials: "same-origin" });
}
