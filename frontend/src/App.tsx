import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import WeekGrid from "./components/WeekGrid";
import WeekNav from "./components/WeekNav";
import DayNav from "./components/DayNav";
import LayoutToggle from "./components/LayoutToggle";
import AddEventModal from "./components/AddEventModal";
import TaskEditorModal from "./components/TaskEditorModal";
import MemberBadge from "./components/MemberBadge";
import LoginPage from "./components/LoginPage";
import IconSidebar from "./components/IconSidebar";
import TodosView from "./components/TodosView";
import PersonDayView from "./components/PersonDayView";
import TaskPersonDayView from "./components/TaskPersonDayView";
import { setUnauthorizedHandler } from "./api";
import { useWeekData } from "./hooks/useWeekData";
import type { CalendarEvent, Task } from "./types";

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

function addDays(dateStr: string, days: number) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export default function App() {
  const [needsLogin, setNeedsLogin] = useState(false);
  useEffect(() => {
    setUnauthorizedHandler(() => setNeedsLogin(true));
  }, []);

  const [view, setView] = useState<"calendar" | "todos">("calendar");
  const [layoutMode, setLayoutMode] = useState<"week" | "day">("week");
  const [selectedDate, setSelectedDate] = useState(() => todayStr());

  const { data, loading, error, monday, goNextWeek, goPrevWeek, goToday, refresh } = useWeekData();

  const weekEnd = addDays(monday, 6);

  // Keep the selected day inside whatever week is currently loaded (e.g. if
  // the user navigates weeks via WeekNav while in day mode).
  useEffect(() => {
    if (selectedDate < monday || selectedDate > weekEnd) {
      setSelectedDate(monday);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [monday]);

  const selectedDay = data?.days.find((d) => d.date === selectedDate);

  const goPrevDay = () => {
    const next = addDays(selectedDate, -1);
    setSelectedDate(next);
    if (next < monday) goPrevWeek();
  };

  const goNextDay = () => {
    const next = addDays(selectedDate, 1);
    setSelectedDate(next);
    if (next > weekEnd) goNextWeek();
  };

  const goTodayDay = () => {
    setSelectedDate(todayStr());
    goToday();
  };

  const [modalOpen, setModalOpen] = useState(false);
  const [prefillDate, setPrefillDate] = useState<string | undefined>();
  const [editEvent, setEditEvent] = useState<CalendarEvent | undefined>();

  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [taskPrefillDate, setTaskPrefillDate] = useState<string | undefined>();
  const [editTask, setEditTask] = useState<Task | undefined>();

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

  const openAddTask = (date: string) => {
    setEditTask(undefined);
    setTaskPrefillDate(date);
    setTaskModalOpen(true);
  };

  const openEditTask = (task: Task) => {
    setEditTask(task);
    setTaskPrefillDate(undefined);
    setTaskModalOpen(true);
  };

  const handleSaved = () => {
    refresh();
  };

  const handleFabClick = () => {
    const date = layoutMode === "day" ? selectedDate : todayStr();
    if (view === "calendar") openAdd(date);
    else openAddTask(date);
  };

  return (
    <div className="flex flex-row h-screen p-3 gap-3 select-none">
      <IconSidebar view={view} onChange={setView} />

      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-3 mb-0">
          <div className="flex-1 min-w-0">
            {layoutMode === "week" ? (
              <WeekNav
                monday={monday}
                loading={loading}
                onPrev={goPrevWeek}
                onNext={goNextWeek}
                onToday={goToday}
                onRefresh={refresh}
              />
            ) : (
              <DayNav
                date={selectedDate}
                loading={loading}
                onPrev={goPrevDay}
                onNext={goNextDay}
                onToday={goTodayDay}
                onRefresh={refresh}
              />
            )}
          </div>
          <LayoutToggle mode={layoutMode} onChange={setLayoutMode} />
        </div>

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
            {data && (layoutMode === "week" || selectedDay) && (
              <motion.div
                key={`${view}-${layoutMode}-${layoutMode === "week" ? monday : selectedDate}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.15 }}
                className="h-full"
              >
                {view === "calendar" ? (
                  layoutMode === "week" ? (
                    <WeekGrid data={data} onAddEvent={openAdd} onEditEvent={openEdit} />
                  ) : (
                    <PersonDayView
                      day={selectedDay!}
                      members={data.members}
                      onAddEvent={openAdd}
                      onEditEvent={openEdit}
                    />
                  )
                ) : layoutMode === "week" ? (
                  <TodosView data={data} onAddTask={openAddTask} onEditTask={openEditTask} />
                ) : (
                  <TaskPersonDayView
                    day={selectedDay!}
                    members={data.members}
                    onAddTask={openAddTask}
                    onEditTask={openEditTask}
                  />
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Floating add button */}
        <motion.button
          whileTap={{ scale: 0.9 }}
          onClick={handleFabClick}
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

        {/* Add/Edit Task Modal */}
        <TaskEditorModal
          isOpen={taskModalOpen}
          prefillDate={taskPrefillDate}
          editTask={editTask}
          members={data?.members ?? []}
          onClose={() => setTaskModalOpen(false)}
          onSaved={handleSaved}
        />
      </div>
    </div>
  );
}
