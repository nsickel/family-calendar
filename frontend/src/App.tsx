import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import WeekGrid from "./components/WeekGrid";
import WeekNav from "./components/WeekNav";
import AddEventModal from "./components/AddEventModal";
import MemberBadge from "./components/MemberBadge";
import LoginPage from "./components/LoginPage";
import { setUnauthorizedHandler } from "./api";
import { useWeekData } from "./hooks/useWeekData";
import type { CalendarEvent } from "./types";

export default function App() {
  const [needsLogin, setNeedsLogin] = useState(false);
  useEffect(() => {
    setUnauthorizedHandler(() => setNeedsLogin(true));
  }, []);

  const { data, loading, error, monday, goNextWeek, goPrevWeek, goToday, refresh } = useWeekData();

  const [modalOpen, setModalOpen] = useState(false);
  const [prefillDate, setPrefillDate] = useState<string | undefined>();
  const [editEvent, setEditEvent] = useState<CalendarEvent | undefined>();

  if (needsLogin) return <LoginPage />;

  const openAdd = (date: string) => {
    setEditEvent(undefined);
    setPrefillDate(date);
    setModalOpen(true);
  };

  const openEdit = (event: CalendarEvent) => {
    setEditEvent(event);
    setPrefillDate(undefined);
    setModalOpen(true);
  };

  const handleSaved = () => {
    refresh();
  };

  return (
    <div className="flex flex-col h-screen p-3 select-none">
      {/* Header */}
      <WeekNav
        monday={monday}
        loading={loading}
        onPrev={goPrevWeek}
        onNext={goNextWeek}
        onToday={goToday}
        onRefresh={refresh}
      />

      {/* Member legend */}
      {data && (
        <div className="flex gap-2 flex-wrap mb-3 px-1">
          {data.members
            .filter((m) => m.connected)
            .map((m) => (
              <MemberBadge key={m.id} member={m} size="sm" />
            ))}
        </div>
      )}

      {/* Main grid */}
      <div className="flex-1 min-h-0">
        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-4xl mb-2">😬</p>
              <p className="font-bold text-gray-500">Couldn't load calendar</p>
              <p className="text-sm text-gray-400 mb-4">{error}</p>
              <button
                onClick={refresh}
                className="px-6 py-3 bg-indigo-500 text-white font-black rounded-xl active:bg-indigo-600"
              >
                Try again
              </button>
            </div>
          </div>
        )}

        {!error && !data && loading && (
          <div className="flex items-center justify-center h-full">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
              className="text-5xl"
            >
              🗓️
            </motion.div>
          </div>
        )}

        <AnimatePresence mode="wait">
          {data && (
            <motion.div
              key={monday}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="h-full"
            >
              <WeekGrid data={data} onAddEvent={openAdd} onEditEvent={openEdit} />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Floating add button */}
      <motion.button
        whileTap={{ scale: 0.9 }}
        onClick={() => openAdd(new Date().toISOString().slice(0, 10))}
        className="fixed bottom-6 right-6 w-16 h-16 rounded-full bg-yellow-400 text-white text-3xl font-black shadow-lg flex items-center justify-center z-30 active:bg-yellow-500"
      >
        +
      </motion.button>

      {/* Add/Edit Modal */}
      <AddEventModal
        isOpen={modalOpen}
        prefillDate={prefillDate}
        editEvent={editEvent}
        members={data?.members ?? []}
        onClose={() => setModalOpen(false)}
        onSaved={handleSaved}
      />
    </div>
  );
}
