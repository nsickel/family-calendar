import { motion } from "framer-motion";
import type { ReactNode } from "react";
import type { Member } from "../types";

interface Props {
  member: Member;
  onClick: () => void;
  children: ReactNode;
}

export default function MemberColumn({ member, onClick, children }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="flex flex-col rounded-2xl p-2 min-h-0 overflow-hidden bg-white/70 border border-gray-200"
      style={{ borderTop: `4px solid ${member.color}` }}
      onClick={onClick}
    >
      {/* Person header */}
      <div className="mb-2 text-center">
        <div className="text-2xl leading-none">{member.emoji}</div>
        <div
          className="text-sm font-black leading-tight mt-0.5 truncate"
          style={{ color: member.color }}
        >
          {member.name}
        </div>
      </div>

      {/* Items */}
      <div className="flex-1 min-h-0 overflow-y-auto scrollbar-hide" onClick={(e) => e.stopPropagation()}>
        {children}
      </div>
    </motion.div>
  );
}
