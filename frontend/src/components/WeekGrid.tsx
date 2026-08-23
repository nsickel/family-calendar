import DayColumn from "./DayColumn";
import type { WeekData, CalendarEvent, Task } from "../types";

interface Props {
  data: WeekData;
  onAddEvent: (date: string) => void;
  onEditEvent: (event: CalendarEvent) => void;
  onAddTask: (date: string) => void;
  onEditTask: (task: Task) => void;
}

export default function WeekGrid({ data, onAddEvent, onEditEvent, onAddTask, onEditTask }: Props) {
  return (
    <div className="grid grid-cols-7 gap-2 h-full">
      {data.days.map((day) => (
        <DayColumn
          key={day.date}
          day={day}
          onAddEvent={onAddEvent}
          onEditEvent={onEditEvent}
          onAddTask={onAddTask}
          onEditTask={onEditTask}
        />
      ))}
    </div>
  );
}
