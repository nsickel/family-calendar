interface Props {
  mode: "week" | "day";
  onChange: (mode: "week" | "day") => void;
}

export default function LayoutToggle({ mode, onChange }: Props) {
  const itemClass = (active: boolean) =>
    `h-10 px-4 rounded-xl font-black text-sm transition-colors ${
      active ? "bg-indigo-500 text-white" : "text-indigo-400 active:bg-indigo-50"
    }`;

  return (
    <div className="flex items-center gap-1 bg-indigo-100 rounded-xl p-1">
      <button onClick={() => onChange("week")} className={itemClass(mode === "week")}>
        Week
      </button>
      <button onClick={() => onChange("day")} className={itemClass(mode === "day")}>
        Day
      </button>
    </div>
  );
}
