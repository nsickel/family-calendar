import { CalendarDays, ListTodo } from "lucide-react";

interface Props {
  view: "calendar" | "todos";
  onChange: (view: "calendar" | "todos") => void;
}

export default function IconSidebar({ view, onChange }: Props) {
  const itemClass = (active: boolean) =>
    `w-14 h-14 rounded-2xl flex flex-col items-center justify-center gap-0.5 font-black transition-colors ${
      active ? "bg-indigo-500 text-white shadow-md" : "text-gray-400 active:bg-gray-100"
    }`;

  return (
    <div className="flex flex-col items-center gap-3 py-4 w-20 h-full bg-white/80 rounded-2xl shadow-sm">
      <button onClick={() => onChange("calendar")} className={itemClass(view === "calendar")}>
        <CalendarDays size={26} strokeWidth={2.5} />
        <span className="text-[10px] uppercase tracking-wider">Cal</span>
      </button>
      <button onClick={() => onChange("todos")} className={itemClass(view === "todos")}>
        <ListTodo size={26} strokeWidth={2.5} />
        <span className="text-[10px] uppercase tracking-wider">To-Do</span>
      </button>
    </div>
  );
}
