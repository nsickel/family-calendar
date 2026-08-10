import { useState, useEffect, useCallback, useRef } from "react";
import { fetchWeek } from "../api";
import type { WeekData } from "../types";

const REFRESH_INTERVAL = 5 * 60 * 1000;

function getMondayOf(dateStr?: string): string {
  const d = dateStr ? new Date(dateStr) : new Date();
  const day = d.getDay();
  const diff = (day === 0 ? -6 : 1 - day);
  d.setDate(d.getDate() + diff);
  return d.toISOString().slice(0, 10);
}

export function useWeekData() {
  const [monday, setMonday] = useState(() => getMondayOf());
  const [data, setData] = useState<WeekData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const load = useCallback(async (date: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchWeek(date);
      setData(result);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(monday);
    timerRef.current = setInterval(() => load(monday), REFRESH_INTERVAL);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [monday, load]);

  const goNextWeek = () => {
    const d = new Date(monday);
    d.setDate(d.getDate() + 7);
    setMonday(d.toISOString().slice(0, 10));
  };

  const goPrevWeek = () => {
    const d = new Date(monday);
    d.setDate(d.getDate() - 7);
    setMonday(d.toISOString().slice(0, 10));
  };

  const goToday = () => setMonday(getMondayOf());

  const refresh = () => load(monday);

  return { data, loading, error, monday, goNextWeek, goPrevWeek, goToday, refresh };
}
