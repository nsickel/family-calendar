import { useEffect, useState } from "react";
import MemberColumn from "./MemberColumn";
import TaskItem from "./TaskItem";
import type { DayData, Member, Task } from "../types";

interface Props {
  day: DayData;
  members: Member[];
  onAddTask: (date: string) => void;
  onEditTask: (task: Task) => void;
}

export default function TaskPersonDayView({ day, members, onAddTask, onEditTask }: Props) {
  const [tasks, setTasks] = useState(day.tasks);

  useEffect(() => setTasks(day.tasks), [day.tasks]);

  const removeTask = (id: string) => setTasks((prev) => prev.filter((t) => t.id !== id));

  return (
    <div
      className="grid gap-2 h-full"
      style={{ gridTemplateColumns: `repeat(${members.length}, minmax(0, 1fr))` }}
    >
      {members.map((member) => (
        <MemberColumn key={member.id} member={member} onClick={() => onAddTask(day.date)}>
          {tasks
            .filter((t) => t.assignees.some((a) => a.id === member.id))
            .map((t) => (
              <TaskItem key={t.id} task={t} onCompleted={removeTask} onEdit={onEditTask} size="lg" />
            ))}
        </MemberColumn>
      ))}
    </div>
  );
}
