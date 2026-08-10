import DayColumn from "./DayColumn";
import type { WeekData, CalendarEvent } from "../types";

interface Props {
  data: WeekData;
  onAddEvent: (date: string) => void;
  onEditEvent: (event: CalendarEvent) => void;
}

export default function WeekGrid({ data, onAddEvent, onEditEvent }: Props) {
  return (
    <div className="grid grid-cols-7 gap-2 h-full">
      {data.days.map((day) => (
        <DayColumn
          key={day.date}
          day={day}
          onAddEvent={onAddEvent}
          onEditEvent={onEditEvent}
        />
      ))}
    </div>
  );
}
