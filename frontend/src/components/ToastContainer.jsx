import { useToast } from "../context/ToastContext";

const TOAST_ICONS = {
  success: "✓",
  error: "✕",
  warning: "⚠️",
  info: "ℹ️",
};

export default function ToastContainer() {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container" role="region" aria-label="Notifications">
      {toasts.map((toast) => {
        const icon = TOAST_ICONS[toast.type] || "ℹ️";
        const role = toast.type === "error" ? "alert" : "status";
        return (
          <div
            key={toast.id}
            className={`toast-item toast-${toast.type}`}
            role={role}
            aria-live={toast.type === "error" ? "assertive" : "polite"}
          >
            <span className="toast-icon" aria-hidden="true">
              {icon}
            </span>
            <span className="toast-message">{toast.message}</span>
            <button
              type="button"
              className="toast-close-btn"
              onClick={() => removeToast(toast.id)}
              aria-label="Dismiss notification"
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
}
