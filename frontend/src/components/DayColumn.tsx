import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import EventPill from "./EventPill";
import TaskItem from "./TaskItem";
import type { DayData, CalendarEvent, Task } from "../types";

interface Props {
  day: DayData;
  onAddEvent: (date: string) => void;
  onEditEvent: (event: CalendarEvent) => void;
  onAddTask: (date: string) => void;
  onEditTask: (task: Task) => void;
}

export default function DayColumn({ day, onAddEvent, onEditEvent, onAddTask, onEditTask }: Props) {
  const [tasks, setTasks] = useState(day.tasks);

  useEffect(() => setTasks(day.tasks), [day.tasks]);

  const removeTask = (id: string) => setTasks((prev) => prev.filter((t) => t.id !== id));

  const isToday = day.is_today;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className={`flex flex-col rounded-2xl p-2 min-h-0 overflow-hidden ${
        isToday
          ? "bg-yellow-50 border-4 border-yellow-400 shadow-lg"
          : "bg-white/70 border border-gray-200"
      }`}
      onClick={() => onAddEvent(day.date)}
    >
      {/* Day header */}
      <div className="mb-2 text-center">
        <div className={`text-xs font-black uppercase tracking-wider ${isToday ? "text-yellow-600" : "text-gray-400"}`}>
          {day.weekday.slice(0, 3)}
        </div>
        <div
          className={`text-2xl font-black leading-none ${isToday ? "text-yellow-600" : "text-gray-700"}`}
        >
          {day.day_number}
        </div>
        {isToday && (
          <div className="text-[10px] font-black text-yellow-500 uppercase tracking-widest mt-0.5">
            Today
          </div>
        )}
      </div>

      {/* Events */}
      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-hide" onClick={(e) => e.stopPropagation()}>
        {day.events.map((ev) => (
          <EventPill key={ev.id} event={ev} onClick={onEditEvent} />
        ))}
      </div>

      {/* Tasks */}
      <div
        className="border-t border-dashed border-gray-200 mt-1 pt-1"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-1">
          <span className="text-[10px] font-black text-gray-400 uppercase tracking-wider">Tasks</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onAddTask(day.date);
            }}
            className="text-xs font-black text-indigo-400 active:text-indigo-600 px-1"
          >
            + Task
          </button>
        </div>
        {tasks.map((t) => (
          <TaskItem key={t.id} task={t} onCompleted={removeTask} onEdit={onEditTask} />
        ))}
      </div>
    </motion.div>
  );
}
