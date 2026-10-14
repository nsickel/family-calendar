import { useState, useCallback } from "react";
import { fetchMembers } from "../api";
import type { SettingsMember } from "../types";

export function useMembers() {
  const [data, setData] = useState<SettingsMember[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await fetchMembers());
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, load };
}
