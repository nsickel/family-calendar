import TaskDayColumn from "./TaskDayColumn";
import type { WeekData, Task } from "../types";

interface Props {
  data: WeekData;
  onAddTask: (date: string) => void;
  onEditTask: (task: Task) => void;
}

export default function TodosView({ data, onAddTask, onEditTask }: Props) {
  return (
    <div className="grid grid-cols-7 gap-2 h-full">
      {data.days.map((day) => (
        <TaskDayColumn key={day.date} day={day} onAddTask={onAddTask} onEditTask={onEditTask} />
      ))}
    </div>
  );
}
