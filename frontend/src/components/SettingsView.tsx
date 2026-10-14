import MemberBadge from "./MemberBadge";
import type { SettingsMember } from "../types";

interface Props {
  members: SettingsMember[] | null;
  loading: boolean;
  error: string | null;
}

export default function SettingsView({ members, loading, error }: Props) {
  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-2xl mx-auto bg-white rounded-3xl p-8 shadow-xl">
        <h1 className="text-3xl font-black text-gray-800 mb-1">⚙️ Settings</h1>
        <p className="text-sm font-bold text-gray-400 mb-6">
          Connect each family member's Google account to sync their calendar and tasks.
        </p>

        {error && <p className="text-red-500 font-bold text-sm mb-4">{error}</p>}
        {loading && !members && <p className="text-gray-400 font-bold">Loading…</p>}

        <div className="flex flex-col gap-3">
          {members?.map((member) => (
            <div
              key={member.id}
              className="flex items-center justify-between gap-3 p-4 bg-gray-50 rounded-2xl"
            >
              <MemberBadge member={member} />
              <div className="flex items-center gap-3">
                <span
                  className={`text-sm font-black uppercase tracking-wider ${
                    member.connected ? "text-green-600" : "text-gray-400"
                  }`}
                >
                  {member.connected ? "✅ Connected" : "❌ Not connected"}
                </span>
                <a
                  href={`/auth/connect/${member.slug}`}
                  className="px-5 py-2.5 bg-indigo-500 text-white font-black rounded-xl active:bg-indigo-600 text-sm text-center"
                >
                  {member.connected ? "Reconnect" : "Connect"}
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
