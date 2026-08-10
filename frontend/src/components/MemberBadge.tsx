import type { Member } from "../types";

interface Props {
  member: Member;
  size?: "sm" | "md";
}

export default function MemberBadge({ member, size = "md" }: Props) {
  const sizeClass = size === "sm" ? "text-sm px-2 py-0.5" : "text-base px-3 py-1";
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-bold ${sizeClass}`}
      style={{ background: member.color + "33", color: member.color, border: `2px solid ${member.color}` }}
    >
      <span>{member.emoji}</span>
      <span>{member.name}</span>
    </span>
  );
}
