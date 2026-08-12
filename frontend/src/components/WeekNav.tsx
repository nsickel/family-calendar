import { logout } from "../api";

interface Props {
  monday: string;
  loading: boolean;
  onPrev: () => void;
  onNext: () => void;
  onToday: () => void;
  onRefresh: () => void;
}

export default function WeekNav({ monday, loading, onPrev, onNext, onToday, onRefresh }: Props) {
  const handleLogout = async () => {
    await logout();
    window.location.reload();
  };

  const d = new Date(monday);
  const end = new Date(monday);
  end.setDate(end.getDate() + 6);

  const fmt = (date: Date) =>
    date.toLocaleDateString("en-GB", { day: "numeric", month: "short" });

  return (
    <div className="flex items-center justify-between px-2 py-2 bg-white/80 rounded-2xl shadow-sm mb-3">
      <div className="flex items-center gap-2">
        <span className="text-2xl font-black text-indigo-700">🗓️</span>
        <span className="text-lg font-black text-gray-700">
          {fmt(d)} – {fmt(end)}
        </span>
        {loading && (
          <span className="text-xs text-gray-400 animate-pulse font-bold">refreshing…</span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={onPrev}
          className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-700 font-black text-lg flex items-center justify-center active:bg-indigo-200"
        >
          ‹
        </button>
        <button
          onClick={onToday}
          className="h-10 px-4 rounded-xl bg-yellow-400 text-white font-black text-sm active:bg-yellow-500"
        >
          Today
        </button>
        <button
          onClick={onNext}
          className="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-700 font-black text-lg flex items-center justify-center active:bg-indigo-200"
        >
          ›
        </button>
        <button
          onClick={onRefresh}
          className="w-10 h-10 rounded-xl bg-gray-100 text-gray-500 font-black text-lg flex items-center justify-center active:bg-gray-200"
          title="Refresh"
        >
          ↻
        </button>
        <button
          onClick={handleLogout}
          className="w-8 h-8 rounded-xl text-gray-300 text-sm flex items-center justify-center active:bg-gray-100"
          title="Log out"
        >
          ⏻
        </button>
      </div>
    </div>
  );
}
