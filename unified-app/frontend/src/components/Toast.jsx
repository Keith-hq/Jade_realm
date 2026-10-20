import { useEffect, useState } from 'react';

const TOASTS = {}; let toastId = 0;
let globalSetToasts = null;

export function showToast(message, duration = 2500) {
  const id = ++toastId;
  if (globalSetToasts) {
    globalSetToasts((prev) => [...prev, { id, message, exiting: false }]);
    setTimeout(() => {
      globalSetToasts?.((prev) => prev.map((t) => (t.id === id ? { ...t, exiting: true } : t)));
      setTimeout(() => globalSetToasts?.((prev) => prev.filter((t) => t.id !== id)), 300);
    }, duration);
  }
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState([]);
  useEffect(() => { globalSetToasts = setToasts; return () => { globalSetToasts = null; }; }, []);

  if (!toasts.length) return null;

  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-[9999] flex flex-col items-center gap-2 pointer-events-none">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`px-5 py-2.5 rounded-xl bg-jade/15 border border-jade/30 text-jade text-sm font-medium backdrop-blur-md shadow-lg ${t.exiting ? 'toast-exit' : 'toast-enter'}`}
        >
          {t.message}
        </div>
      ))}
    </div>
  );
}
