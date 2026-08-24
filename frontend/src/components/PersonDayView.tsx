import MemberColumn from "./MemberColumn";
import EventPill from "./EventPill";
import type { DayData, Member, CalendarEvent } from "../types";

interface Props {
  day: DayData;
  members: Member[];
  onAddEvent: (date: string) => void;
  onEditEvent: (event: CalendarEvent) => void;
}

export default function PersonDayView({ day, members, onAddEvent, onEditEvent }: Props) {
  return (
    <div
      className="grid gap-2 h-full"
      style={{ gridTemplateColumns: `repeat(${members.length}, minmax(0, 1fr))` }}
    >
      {members.map((member) => (
        <MemberColumn key={member.id} member={member} onClick={() => onAddEvent(day.date)}>
          {day.events
            .filter((ev) => ev.account_id === member.id)
            .map((ev) => (
              <EventPill key={ev.id} event={ev} onClick={onEditEvent} />
            ))}
        </MemberColumn>
      ))}
    </div>
  );
}
