import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { completeTask } from "../api";
import { useConfetti } from "../hooks/useConfetti";
import type { Task } from "../types";

interface Props {
  task: Task;
  onCompleted: (taskId: string) => void;
}

export default function TaskItem({ task, onCompleted }: Props) {
  const [done, setDone] = useState(false);
  const { fire } = useConfetti();

  const handleCheck = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const rect = e.target.getBoundingClientRect();
    setDone(true);
    fire(rect.x + rect.width / 2, rect.y + rect.height / 2);
    try {
      await completeTask(task.id, task.account_id, task.tasklist_id);
      setTimeout(() => onCompleted(task.id), 800);
    } catch {
      setDone(false);
    }
  };

  return (
    <AnimatePresence>
      {!done && (
        <motion.label
          exit={{ opacity: 0, x: 40, scale: 0.8 }}
          transition={{ duration: 0.3 }}
          className="flex items-center gap-2 p-1.5 rounded-lg cursor-pointer min-h-[44px] active:bg-black/5"
          style={{ color: task.color }}
        >
          <input
            type="checkbox"
            checked={false}
            onChange={handleCheck}
            className="w-5 h-5 rounded accent-current cursor-pointer flex-shrink-0"
            style={{ accentColor: task.color }}
          />
          <span className="text-sm leading-none">{task.emoji}</span>
          <span className="text-sm font-bold text-gray-700 leading-tight">{task.title}</span>
        </motion.label>
      )}
    </AnimatePresence>
  );
}
