import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { createTask, updateTask, deleteTask } from "../api";
import type { Member, Task, TaskRecurrence } from "../types";

interface Props {
  isOpen: boolean;
  prefillDate?: string;
  editTask?: Task;
  members: Member[];
  onClose: () => void;
  onSaved: () => void;
}

const RECURRENCE_OPTIONS: { value: TaskRecurrence; label: string }[] = [
  { value: "none", label: "Once" },
  { value: "daily", label: "Daily" },
  { value: "weekdays", label: "Weekdays" },
  { value: "weekly", label: "Weekly" },
];

export default function TaskEditorModal({ isOpen, prefillDate, editTask, members, onClose, onSaved }: Props) {
  const connectedMembers = members.filter((m) => m.connected);
  const [title, setTitle] = useState("");
  const [startDate, setStartDate] = useState("");
  const [hasTime, setHasTime] = useState(false);
  const [startTime, setStartTime] = useState("09:00");
  const [recurrence, setRecurrence] = useState<TaskRecurrence>("none");
  const [assigneeIds, setAssigneeIds] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (editTask) {
      setTitle(editTask.title);
      setStartDate(editTask.start_date);
      setHasTime(!!editTask.start_time);
      setStartTime(editTask.start_time ?? "09:00");
      setRecurrence(editTask.recurrence);
      setAssigneeIds(editTask.assignees.map((a) => a.id));
    } else {
      setTitle("");
      setStartDate(prefillDate ?? new Date().toISOString().slice(0, 10));
      setHasTime(false);
      setStartTime("09:00");
      setRecurrence("none");
      setAssigneeIds(connectedMembers[0] ? [connectedMembers[0].id] : []);
    }
    setError("");
  }, [isOpen, editTask, prefillDate]);

  const toggleAssignee = (id: string) =>
    setAssigneeIds((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));

  const handleSave = async () => {
    if (!title.trim() || assigneeIds.length === 0) {
      setError("Please fill in the title and select at least one family member.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const payload = {
        title,
        start_date: startDate,
        start_time: hasTime ? startTime : null,
        recurrence,
        assignee_ids: assigneeIds,
      };
      if (editTask) {
        await updateTask(editTask.id, payload);
      } else {
        await createTask(payload);
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

  const handleDelete = async () => {
    if (!editTask) return;
    setSaving(true);
    setError("");
    try {
      await deleteTask(editTask.id);
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
                {editTask ? "✏️ Edit Task" : "➕ Add Task"}
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
                    onClick={() => toggleAssignee(m.id)}
                    className="text-2xl p-3 rounded-2xl transition-all"
                    style={{
                      background: assigneeIds.includes(m.id) ? m.color + "33" : "#f5f5f5",
                      border: `3px solid ${assigneeIds.includes(m.id) ? m.color : "transparent"}`,
                      transform: assigneeIds.includes(m.id) ? "scale(1.15)" : "scale(1)",
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
                placeholder="e.g. Clean up room 🧹"
                className="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
                autoFocus
              />
            </div>

            {/* Start date */}
            <div className="mb-4">
              <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">When?</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
              />
            </div>

            {/* Recurrence */}
            <div className="mb-4">
              <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">Repeat?</label>
              <div className="flex gap-2 flex-wrap">
                {RECURRENCE_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    onClick={() => setRecurrence(opt.value)}
                    className="px-4 py-2 rounded-2xl font-bold text-sm transition-all"
                    style={{
                      background: recurrence === opt.value ? "#6366f133" : "#f5f5f5",
                      border: `2px solid ${recurrence === opt.value ? "#6366f1" : "transparent"}`,
                      color: recurrence === opt.value ? "#4338ca" : "#374151",
                    }}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Time toggle */}
            <div className="mb-4 flex items-center gap-3">
              <button
                onClick={() => setHasTime(!hasTime)}
                className={`w-14 h-7 rounded-full transition-colors ${hasTime ? "bg-indigo-400" : "bg-gray-200"}`}
              >
                <div className={`w-5 h-5 bg-white rounded-full shadow transition-transform mx-1 ${hasTime ? "translate-x-7" : "translate-x-0"}`} />
              </button>
              <span className="font-bold text-gray-700">Set a time</span>
            </div>

            {hasTime && (
              <div className="mb-4">
                <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">Time</label>
                <input
                  type="time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full border-2 border-gray-200 rounded-2xl p-3 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
                />
              </div>
            )}

            {error && (
              <p className="text-red-500 font-bold text-sm mb-3">{error}</p>
            )}

            <div className="flex gap-3">
              {editTask && (
                <button
                  onClick={handleDelete}
                  disabled={saving}
                  className="h-16 px-6 rounded-2xl bg-red-100 text-red-500 font-black text-lg active:bg-red-200 disabled:opacity-50"
                >
                  Delete
                </button>
              )}
              <button
                onClick={handleSave}
                disabled={saving}
                className="flex-1 h-16 rounded-2xl bg-indigo-500 text-white font-black text-xl active:bg-indigo-600 disabled:opacity-50"
              >
                {saving ? "Saving…" : "Save 🎉"}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
