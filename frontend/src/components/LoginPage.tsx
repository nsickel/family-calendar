import { useState } from "react";
import { login } from "../api";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password) {
      setError("Please enter a username and password.");
      return;
    }
    setSubmitting(true);
    setError("");
    try {
      const result = await login(username.trim(), password);
      if (result) {
        setError(
          result.error === "too many failed attempts"
            ? `Too many failed attempts. Try again in ${Math.ceil((result.retry_after ?? 0) / 60)} min.`
            : "Invalid username or password."
        );
        return;
      }
      window.location.reload();
    } catch (e) {
      console.error(e);
      setError("Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex items-center justify-center h-screen p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm bg-white rounded-3xl p-8 shadow-xl"
      >
        <h1 className="text-3xl font-black text-gray-800 mb-6 text-center">🗓️ Family Calendar</h1>

        <div className="mb-4">
          <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
            autoFocus
            autoComplete="username"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-black text-gray-500 mb-2 uppercase tracking-wider">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border-2 border-gray-200 rounded-2xl p-4 text-lg font-bold text-gray-800 focus:outline-none focus:border-indigo-400"
            autoComplete="current-password"
          />
        </div>

        {error && <p className="text-red-500 font-bold text-sm mb-3">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full h-16 rounded-2xl bg-indigo-500 text-white font-black text-xl active:bg-indigo-600 disabled:opacity-50"
        >
          {submitting ? "Logging in…" : "Log in"}
        </button>
      </form>
    </div>
  );
}
