import { useToast } from "../context/ToastContext";
import { IconCheck, IconClose, IconAlert } from "./icons";

export default function ToastContainer() {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container" role="region" aria-label="Notifications">
      {toasts.map((toast) => {
        const role = toast.type === "error" ? "alert" : "status";
        return (
          <div
            key={toast.id}
            className={`toast-item toast-${toast.type}`}
            role={role}
            aria-live={toast.type === "error" ? "assertive" : "polite"}
          >
            <span className="toast-icon" aria-hidden="true">
              {toast.type === "success" && <IconCheck size={14} />}
              {toast.type === "error" && <IconClose size={14} />}
              {toast.type === "warning" && <IconAlert size={14} />}
              {toast.type === "info" && <IconAlert size={14} />}
            </span>
            <span className="toast-message">{toast.message}</span>
            <button
              type="button"
              className="toast-close-btn"
              onClick={() => removeToast(toast.id)}
              aria-label="Dismiss notification"
            >
              <IconClose size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
