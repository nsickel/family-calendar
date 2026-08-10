import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createEvent, updateEvent } from "../api";
import type { Member, CalendarEvent } from "../types";

interface Props {
  isOpen: boolean;
  prefillDate?: string;
  editEvent?: CalendarEvent;
  members: Member[];
  onClose: () => void;
  onSaved: () => void;
}

export default function AddEventModal({ isOpen, prefillDate, editEvent, members, onClose, onSaved }: Props) {
  const connectedMembers = members.filter((m) => m.connected);
  const [title, setTitle] = useState("");
  const [date, setDate] = useState("");
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("10:00");
  const [allDay, setAllDay] = useState(false);
  const [accountId, setAccountId] = useState(connectedMembers[0]?.id ?? "");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (editEvent) {
      setTitle(editEvent.title);
      setDate(editEvent.date);
      setStartTime(editEvent.start_time ?? "09:00");
      setEndTime(editEvent.end_time ?? "10:00");
      setAllDay(editEvent.all_day);
      setAccountId(editEvent.account_id);
    } else {
      setTitle("");
      setDate(prefillDate ?? new Date().toISOString().slice(0, 10));
      setStartTime("09:00");
      setEndTime("10:00");
      setAllDay(false);
      setAccountId(connectedMembers[0]?.id ?? "");
    }
    setError("");
  }, [isOpen, editEvent, prefillDate]);

  const handleSave = async () => {
    if (!title.trim() || !accountId) {
      setError("Please fill in the title and select a family member.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      if (editEvent) {
        await updateEvent(editEvent.id, { account_id: accountId, title, date, start_time: startTime, end_time: endTime });
      } else {
        await createEvent({ account_id: accountId, title, date, start_time: startTime, end_time: endTime, all_day: allDay });
      }
      onSaved();
      onClose();
    } catch (e) {
      console.error(e);
      setError("Something went wrong. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/40 z-40"
            onClick={onClose}
          />
          <motion.div
            initial={{ y: "100%", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: "100%", opacity: 0 }}
            transition={{ type: "spring", stiffness: 400, damping: 35 }}
            className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl p-6 shadow-2xl max-h-[90vh] overflow-y-auto"
          >
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-2xl font-black text-gray-800">
                {editEvent ? "✏️ Edit Event" : "➕ Add Event"}
              </h2>
              <button
                onClick={onClose}
                className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 font-black active:bg-gray-200"
              >
                ✕
              </button>
            </div>

            {/* Who is this for? */}
            <div className="mb-4">
              <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">For who?</label>
              <div className="flex gap-2 flex-wrap">
                {connectedMembers.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setAccountId(m.id)}
                    className="text-2xl p-3 rounded-2xl transition-all"
                    style={{
                      background: accountId === m.id ? m.color + "33" : "#f5f5f5",
                      border: `3px solid ${accountId === m.id ? m.color : "transparent"}`,
                      transform: accountId === m.id ? "scale(1.15)" : "scale(1)",
                    }}
                    title={m.name}
                  >
                    {m.emoji}
                  </button>
                ))}
              </div>
            </div>

            {/* Title */}
            <div className="mb-4">
              <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">What?</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Football practice ⚽"
                className="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
                autoFocus
              />
            </div>

            {/* Date */}
            <div className="mb-4">
              <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">When?</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
              />
            </div>

            {/* All day toggle */}
            <div className="mb-4 flex items-center gap-3">
              <button
                onClick={() => setAllDay(!allDay)}
                className={`w-14 h-7 rounded-full transition-colors ${allDay ? "bg-indigo-400" : "bg-gray-200"}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform mx-1 ${allDay ? "translate-x-7" : "translate-x-0"}`} />
              </button>
              <span className="font-bold text-gray-700">All day</span>
            </div>

            {/* Times */}
            {!allDay && (
              <div className="flex gap-3 mb-4">
                <div className="flex-1">
                  <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">Start</label>
                  <input
                    type="time"
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="w-full border-2 border-gray-200 rounded-2xl p-3 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
                  />
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">End</label>
                  <input
                    type="time"
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="w-full border-2 border-gray-200 rounded-2xl p-3 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
                  />
                </div>
              </div>
            )}

            {error && (
              <p className="text-red-500 font-bold text-sm mb-3">{error}</p>
            )}

            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full h-16 rounded-2xl bg-indigo-500 text-white font-black text-xl active:bg-indigo-600 disabled:opacity-50"
            >
              {saving ? "Saving…" : "Save 🎉"}
            </button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
