export interface Member {
  id: string;
  name: string;
  emoji: string;
  color: string;
  connected: boolean;
}

export interface CalendarEvent {
  id: string;
  calendar_id: string;
  account_id: string;
  title: string;
  emoji: string;
  color: string;
  date: string;
  start_time: string | null;
  end_time: string | null;
  all_day: boolean;
  source: "calendar";
}

export interface TaskAssignee {
  id: string;
  name: string;
  emoji: string;
  color: string;
}

export type TaskRecurrence = "none" | "daily" | "weekdays" | "weekly";

export interface Task {
  id: string;
  title: string;
  start_date: string;
  occurrence_date: string;
  start_time: string | null;
  recurrence: TaskRecurrence;
  assignees: TaskAssignee[];
  source: "local";
}

export interface NewTaskPayload {
  title: string;
  start_date: string;
  start_time?: string | null;
  recurrence: TaskRecurrence;
  assignee_ids: string[];
}

export interface DayData {
  date: string;
  weekday: string;
  day_number: number;
  month_name: string;
  is_today: boolean;
  events: CalendarEvent[];
  tasks: Task[];
}

export interface WeekData {
  week_start: string;
  week_end: string;
  days: DayData[];
  members: Member[];
}

export interface NewEventPayload {
  account_id: string;
  title: string;
  date: string;
  start_time?: string;
  end_time?: string;
  all_day: boolean;
}
