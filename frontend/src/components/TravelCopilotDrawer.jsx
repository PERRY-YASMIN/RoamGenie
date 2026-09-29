import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCopilot } from "../context/CopilotContext";
import {
  IconSparkles,
  IconClose,
  IconSend,
  IconCompass,
  IconSuitcase,
  IconCalendar,
  IconWallet,
  IconSun,
  IconMapPin,
  IconTrash,
} from "./icons";

function formatTripDates(startDate, endDate) {
  if (!startDate || !endDate) return "";
  try {
    const s = new Date(startDate);
    const e = new Date(endDate);
    const sStr = s.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    const eStr = e.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    return `${sStr} – ${eStr}`;
  } catch {
    return `${startDate} – ${endDate}`;
  }
}

export default function TravelCopilotDrawer() {
  const { isAuthenticated } = useAuth();
  const {
    isOpen,
    toggleCopilot,
    closeCopilot,
    activeTripId,
    activeTrip,
    selectTrip,
    userTrips,
    chatMessages,
    chatLoading,
    executeChatMessage,
    clearChat,
  } = useCopilot();

  const [inputVal, setInputVal] = useState("");
  const chatBottomRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll when messages update or drawer opens
  useEffect(() => {
    if (isOpen && typeof chatBottomRef.current?.scrollIntoView === "function") {
      chatBottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [chatMessages, chatLoading, isOpen]);

  // Focus input on drawer open
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  // Close on Escape key
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === "Escape" && isOpen) {
        closeCopilot();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, closeCopilot]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputVal.trim() || chatLoading) return;
    executeChatMessage(inputVal);
    setInputVal("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleQuickPrompt = (prompt) => {
    executeChatMessage(prompt);
  };

  const destName = activeTrip?.destination_city || activeTrip?.destination?.city || null;
  const isOverBudget =
    activeTrip &&
    Number(activeTrip.estimated_total || 0) > Number(activeTrip.total_budget || 0);
  const deficitAmount = isOverBudget
    ? Number(activeTrip.estimated_total) - Number(activeTrip.total_budget)
    : 0;

  return (
    <>
      {/* Floating Trigger Button in Bottom-Right */}
      <button
        type="button"
        className="copilot-floating-btn"
        onClick={toggleCopilot}
        aria-label="Open RoamGenie AI Assistant"
        aria-expanded={isOpen}
      >
        <span className="copilot-btn-icon" aria-hidden="true">
          <IconSparkles size={16} />
        </span>
        <span className="copilot-btn-label">RoamGenie AI</span>
        {destName && (
          <span className="copilot-btn-badge" title={`Active trip: ${destName}`}>
            {destName}
          </span>
        )}
      </button>

      {/* Sliding Chat Drawer & Backdrop */}
      {isOpen && (
        <div className="chat-drawer-backdrop" onClick={closeCopilot}>
          <div
            className="chat-drawer editorial-drawer"
            role="dialog"
            aria-modal="true"
            aria-label="RoamGenie AI Travel Assistant"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="chat-header">
              <div className="chat-header-title-wrap">
                <div className="chat-eyebrow">INTELLIGENCE</div>
                <h3 className="chat-title">RoamGenie AI</h3>
                <p className="chat-header-subtitle">Personalized Travel Assistant</p>
              </div>

              <button
                type="button"
                className="chat-close-btn"
                onClick={closeCopilot}
                aria-label="Close RoamGenie AI drawer"
              >
                <IconClose size={18} />
              </button>
            </div>

            {/* Trip Selector Toolbar */}
            {isAuthenticated && userTrips.length > 0 && (
              <div className="chat-trip-selector-bar">
                <label htmlFor="ai-trip-select" className="selector-label">
                  JOURNEY
                </label>
                <select
                  id="ai-trip-select"
                  className="chat-trip-select"
                  value={activeTripId || ""}
                  onChange={(e) => selectTrip(e.target.value)}
                  aria-label="Select trip context for AI assistant"
                >
                  <option value="">No trip connected (General advice)</option>
                  {userTrips.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.destination_city || `Trip #${t.id}`}
                      {t.start_date && t.end_date ? ` (${formatTripDates(t.start_date, t.end_date)})` : ""}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Trip Context Card or Empty State */}
            {activeTrip ? (
              <div className="chat-context-editorial">
                <div className="context-hero-line">
                  <h4 className="context-city-title">{destName || `Trip #${activeTrip.id}`}</h4>
                  {activeTrip.start_date && (
                    <span className="context-date-range">
                      {formatTripDates(activeTrip.start_date, activeTrip.end_date)}
                    </span>
                  )}
                </div>

                <div className="context-details-row">
                  <div className="context-meta-col">
                    <span className="context-meta-label">TRAVELLERS</span>
                    <span className="context-meta-val">{activeTrip.traveller_count} travellers</span>
                  </div>
                  <div className="context-meta-col">
                    <span className="context-meta-label">BUDGET</span>
                    <span className="context-meta-val">₹{Number(activeTrip.total_budget || 0).toLocaleString()}</span>
                  </div>
                  <div className="context-meta-col">
                    <span className="context-meta-label">STATUS</span>
                    {isOverBudget ? (
                      <span className="context-meta-val text-deficit">₹{deficitAmount.toLocaleString()} over</span>
                    ) : (
                      <span className="context-meta-val text-aligned">Aligned</span>
                    )}
                  </div>
                </div>

                <div className="context-action-line">
                  <button
                    type="button"
                    className="context-link-btn"
                    onClick={() => selectTrip(null)}
                    title="Switch to general travel mode"
                  >
                    Disconnect journey context
                  </button>
                </div>
              </div>
            ) : (
              <div className="chat-empty-context">
                <div className="empty-context-inner">
                  <span className="empty-context-icon" aria-hidden="true">
                    <IconCompass size={24} />
                  </span>
                  <div>
                    <h4>No trip is connected yet</h4>
                    <p>
                      Confirm a trip and your travel preferences, itinerary and budget will become available here.
                    </p>
                  </div>
                </div>
                <Link
                  to="/plan"
                  className="editorial-action-btn empty-plan-btn"
                  onClick={closeCopilot}
                >
                  Plan a Trip →
                </Link>
              </div>
            )}

            {/* Chat Body */}
            <div className="chat-body">
              {!isAuthenticated ? (
                <div className="chat-auth-prompt">
                  <div className="auth-prompt-eyebrow">AUTHENTICATION</div>
                  <h4>Sign in to connect RoamGenie AI</h4>
                  <p>
                    Log in to receive personalized recommendations grounded in your private itineraries,
                    category budgets, and local destination intelligence.
                  </p>
                  <div className="chat-auth-buttons">
                    <Link className="editorial-action-btn" to="/login" onClick={closeCopilot}>
                      Log In →
                    </Link>
                    <Link className="editorial-quiet-btn" to="/register" onClick={closeCopilot}>
                      Create Account
                    </Link>
                  </div>
                </div>
              ) : chatMessages.length === 0 ? (
                <div className="chat-welcome">
                  <p className="welcome-intro">
                    {activeTrip
                      ? `Ready to assist with your journey to ${destName}. Inquire about itinerary pacing, budget allocations, or local context.`
                      : "RoamGenie AI is ready. Inquire about destinations, planning principles, or connect a journey above."}
                  </p>

                  <div className="quick-actions-label">SUGGESTED INQUIRIES</div>
                  <div className="quick-suggestions-editorial">
                    <button
                      type="button"
                      className="quick-suggestion-item"
                      onClick={() => handleQuickPrompt("What should I pack?")}
                    >
                      <span className="suggestion-bullet">—</span>
                      <span>Packing essentials & checklist</span>
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-item"
                      onClick={() => handleQuickPrompt("How can I reduce my budget?")}
                    >
                      <span className="suggestion-bullet">—</span>
                      <span>Budget review & optimization</span>
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-item"
                      onClick={() => handleQuickPrompt("Can you improve my itinerary?")}
                    >
                      <span className="suggestion-bullet">—</span>
                      <span>Itinerary pacing suggestions</span>
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-item"
                      onClick={() => handleQuickPrompt("What should I do if it rains?")}
                    >
                      <span className="suggestion-bullet">—</span>
                      <span>Weather context & contingency plans</span>
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-item"
                      onClick={() => handleQuickPrompt("Suggest places to visit")}
                    >
                      <span className="suggestion-bullet">—</span>
                      <span>Local recommendations & highlights</span>
                    </button>
                  </div>
                </div>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div key={idx} className={`chat-bubble-editorial ${msg.role}`}>
                    <div className="bubble-speaker">
                      {msg.role === "user" ? "YOU" : "ROAMGENIE AI"}
                    </div>
                    <div className="bubble-content" style={{ whiteSpace: "pre-line" }}>
                      {msg.text}
                    </div>
                    {msg.actions && msg.actions.length > 0 && (
                      <div className="suggested-actions-editorial">
                        {msg.actions.map((act, aIdx) => (
                          <button
                            key={aIdx}
                            type="button"
                            className="editorial-action-chip"
                            onClick={() => handleQuickPrompt(act)}
                          >
                            {act}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))
              )}

              {chatLoading && (
                <div className="chat-bubble-editorial assistant loading" role="status" aria-live="polite">
                  <div className="bubble-speaker">ROAMGENIE AI</div>
                  <div className="thinking-row">
                    <span className="thinking-text">Analyzing journey parameters...</span>
                    <span className="typing-dots" aria-hidden="true">
                      <span />
                      <span />
                      <span />
                    </span>
                  </div>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            {/* Footer with Input */}
            {isAuthenticated && (
              <form className="chat-footer-editorial" onSubmit={handleSubmit}>
                <div className="chat-input-row">
                  <input
                    ref={inputRef}
                    type="text"
                    className="chat-text-input"
                    placeholder={
                      destName
                        ? `Ask about your trip to ${destName}...`
                        : "Ask about travel destinations or planning..."
                    }
                    value={inputVal}
                    onChange={(e) => setInputVal(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={chatLoading}
                    aria-label="Type your message to RoamGenie AI"
                  />
                  <button
                    type="submit"
                    className="chat-submit-btn"
                    disabled={chatLoading || !inputVal.trim()}
                    aria-label="Send message"
                  >
                    <IconSend size={15} />
                  </button>
                </div>
                {chatMessages.length > 0 && (
                  <div className="chat-footer-meta">
                    <button
                      type="button"
                      className="chat-clear-link"
                      onClick={clearChat}
                      title="Clear message history and start a new conversation"
                      aria-label="Clear chat history"
                    >
                      <IconTrash size={12} /> Clear history
                    </button>
                  </div>
                )}
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
