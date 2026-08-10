import { motion } from "framer-motion";
import type { CalendarEvent } from "../types";

interface Props {
  event: CalendarEvent;
  onClick: (event: CalendarEvent) => void;
}

export default function EventPill({ event, onClick }: Props) {
  return (
    <motion.button
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 500, damping: 28 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => onClick(event)}
      className="w-full text-left rounded-xl p-2 mb-1 min-h-[48px] flex flex-col justify-center"
      style={{
        background: event.color + "22",
        borderLeft: `4px solid ${event.color}`,
      }}
    >
      <div className="flex items-center gap-1">
        <span className="text-base leading-none">{event.emoji}</span>
        <span className="font-black text-sm leading-tight text-gray-800 truncate">{event.title}</span>
      </div>
      {!event.all_day && event.start_time && (
        <span className="text-xs font-bold mt-0.5" style={{ color: event.color }}>
          {event.start_time}{event.end_time ? ` – ${event.end_time}` : ""}
        </span>
      )}
    </motion.button>
  );
}
