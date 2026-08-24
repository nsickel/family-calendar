import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { completeTask } from "../api";
import { useConfetti } from "../hooks/useConfetti";
import type { Task } from "../types";

interface Props {
  task: Task;
  onCompleted: (taskId: string) => void;
  onEdit: (task: Task) => void;
  size?: "sm" | "lg";
}

export default function TaskItem({ task, onCompleted, onEdit, size = "sm" }: Props) {
  const isLg = size === "lg";
  const [done, setDone] = useState(false);
  const { fire } = useConfetti();
  const accentColor = task.assignees[0]?.color ?? "#6b7280";

  const handleCheck = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const rect = e.target.getBoundingClientRect();
    setDone(true);
    fire(rect.x + rect.width / 2, rect.y + rect.height / 2);
    try {
      await completeTask(task.id, task.occurrence_date);
      setTimeout(() => onCompleted(task.id), 800);
    } catch {
      setDone(false);
    }
  };

  return (
    <AnimatePresence>
      {!done && (
        <motion.div
          exit={{ opacity: 0, x: 40, scale: 0.8 }}
          transition={{ duration: 0.3 }}
          className={`flex items-center rounded-lg ${
            isLg ? "gap-2.5 p-2.5 mb-2 min-h-[56px]" : "gap-2 p-1.5 min-h-[44px]"
          }`}
          style={
            isLg
              ? { background: accentColor + "33", borderLeft: `6px solid ${accentColor}` }
              : undefined
          }
        >
          <input
            type="checkbox"
            checked={false}
            onChange={handleCheck}
            className={`${isLg ? "w-6 h-6" : "w-5 h-5"} rounded cursor-pointer flex-shrink-0`}
            style={{ accentColor }}
          />
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onEdit(task);
            }}
            className="flex items-center gap-1 flex-1 text-left active:bg-black/5 rounded-lg"
          >
            <span className="flex -space-x-1">
              {task.assignees.map((a) => (
                <span key={a.id} title={a.name} className={`${isLg ? "text-base" : "text-sm"} leading-none`}>
                  {a.emoji}
                </span>
              ))}
            </span>
            <span className={`${isLg ? "text-base" : "text-sm"} font-bold text-gray-700 leading-tight`}>{task.title}</span>
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
