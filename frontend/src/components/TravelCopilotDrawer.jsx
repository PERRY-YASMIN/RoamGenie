import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCopilot } from "../context/CopilotContext";

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
        <span className="copilot-btn-icon" aria-hidden="true">✨</span>
        <span className="copilot-btn-label">RoamGenie AI</span>
        {destName && (
          <span className="copilot-btn-badge" title={`Active trip: ${destName}`}>
            📍 {destName}
          </span>
        )}
      </button>

      {/* Sliding Chat Drawer & Backdrop */}
      {isOpen && (
        <div className="chat-drawer-backdrop" onClick={closeCopilot}>
          <div
            className="chat-drawer"
            role="dialog"
            aria-modal="true"
            aria-label="RoamGenie AI Travel Assistant"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="chat-header">
              <div className="chat-header-title-wrap">
                <div className="chat-header-brand">
                  <span className="brand-sparkle" aria-hidden="true">✨</span>
                  <h3>RoamGenie AI</h3>
                </div>
                <p className="chat-header-subtitle">Personalized Travel Assistant</p>
              </div>

              <div className="chat-header-actions">
                <button
                  type="button"
                  className="chat-close-btn"
                  onClick={closeCopilot}
                  aria-label="Close RoamGenie AI drawer"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Trip Selector Toolbar */}
            {isAuthenticated && userTrips.length > 0 && (
              <div className="chat-trip-selector-bar">
                <label htmlFor="ai-trip-select" className="selector-label">
                  Planning with:
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
              <div className="chat-context-card">
                <div className="context-card-header">
                  <span className="context-dest-name">
                    📍 {destName || `Trip #${activeTrip.id}`}
                  </span>
                  {activeTrip.start_date && (
                    <span className="context-dates">
                      {formatTripDates(activeTrip.start_date, activeTrip.end_date)}
                    </span>
                  )}
                </div>

                <div className="context-card-metrics">
                  <div className="context-metric">
                    <span className="metric-label">Travellers</span>
                    <span className="metric-value">{activeTrip.traveller_count} persons</span>
                  </div>
                  <div className="context-metric">
                    <span className="metric-label">Budget</span>
                    <span className="metric-value">₹{Number(activeTrip.total_budget || 0).toLocaleString()}</span>
                  </div>
                  {isOverBudget ? (
                    <div className="context-metric alert-deficit">
                      <span className="metric-label">Status</span>
                      <span className="metric-value text-danger">⚠️ ₹{deficitAmount.toLocaleString()} over</span>
                    </div>
                  ) : Number(activeTrip.estimated_total) > 0 ? (
                    <div className="context-metric alert-ok">
                      <span className="metric-label">Status</span>
                      <span className="metric-value text-success">✓ On Track</span>
                    </div>
                  ) : null}
                </div>

                <button
                  type="button"
                  className="context-disconnect-btn"
                  onClick={() => selectTrip(null)}
                  title="Switch to general travel mode"
                >
                  Disconnect trip context
                </button>
              </div>
            ) : (
              <div className="chat-empty-context">
                <div className="empty-context-inner">
                  <span className="empty-context-icon" aria-hidden="true">🗺️</span>
                  <div>
                    <h4>Your trip isn&apos;t connected yet</h4>
                    <p>
                      Confirm a trip and I&apos;ll personalize travel suggestions around your destination,
                      dates, budget and itinerary.
                    </p>
                  </div>
                </div>
                <Link
                  to="/plan"
                  className="button button-sm button-primary empty-plan-btn"
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
                  <div className="placeholder-icon">🔐</div>
                  <h4>Sign in to Unlock RoamGenie AI</h4>
                  <p>
                    Log in to receive personalized travel recommendations grounded in your private itineraries,
                    category budgets, packing lists, and local destination weather.
                  </p>
                  <div className="chat-auth-buttons">
                    <Link className="button button-primary button-sm" to="/login" onClick={closeCopilot}>
                      Log In →
                    </Link>
                    <Link className="button button-outline button-sm" to="/register" onClick={closeCopilot}>
                      Sign Up
                    </Link>
                  </div>
                </div>
              ) : chatMessages.length === 0 ? (
                <div className="chat-welcome">
                  <p className="welcome-intro">
                    {activeTrip
                      ? `Hello! I'm ready to assist with your trip to ${destName}. Ask me anything about your itinerary pacing, category budgets, packing essentials, or local attractions.`
                      : "Hello! I'm RoamGenie AI. Ask me general travel questions, or connect a confirmed trip above for personalized advice."}
                  </p>

                  <div className="quick-actions-label">Suggested Inquiries</div>
                  <div className="quick-suggestions">
                    <button
                      type="button"
                      className="quick-suggestion-btn"
                      onClick={() => handleQuickPrompt("What should I pack?")}
                    >
                      🎒 What should I pack?
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-btn"
                      onClick={() => handleQuickPrompt("How can I reduce my budget?")}
                    >
                      💰 Optimize my budget
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-btn"
                      onClick={() => handleQuickPrompt("Can you improve my itinerary?")}
                    >
                      📅 Improve my itinerary
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-btn"
                      onClick={() => handleQuickPrompt("What should I do if it rains?")}
                    >
                      🌧️ What if it rains?
                    </button>
                    <button
                      type="button"
                      className="quick-suggestion-btn"
                      onClick={() => handleQuickPrompt("Suggest places to visit")}
                    >
                      📍 Suggest places
                    </button>
                  </div>
                </div>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div key={idx} className={`chat-bubble ${msg.role}`}>
                    <p style={{ whiteSpace: "pre-line" }}>{msg.text}</p>
                    {msg.actions && msg.actions.length > 0 && (
                      <div className="suggested-actions-list">
                        {msg.actions.map((act, aIdx) => (
                          <button
                            key={aIdx}
                            type="button"
                            className="action-pill action-pill-btn"
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
                <div className="chat-bubble assistant loading" role="status" aria-live="polite">
                  <span className="thinking-text">RoamGenie AI is thinking</span>
                  <span className="typing-dots" aria-hidden="true">
                    <span />
                    <span />
                    <span />
                  </span>
                </div>
              )}
              <div ref={chatBottomRef} />
            </div>

            {/* Footer with Input */}
            {isAuthenticated && (
              <form className="chat-footer" onSubmit={handleSubmit}>
                <div className="chat-input-wrapper">
                  <input
                    ref={inputRef}
                    type="text"
                    placeholder={
                      destName
                        ? `Ask about your trip to ${destName}...`
                        : "Ask travel questions or connect a trip..."
                    }
                    value={inputVal}
                    onChange={(e) => setInputVal(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={chatLoading}
                    aria-label="Type your message to RoamGenie AI"
                  />
                  <button
                    type="submit"
                    className="chat-send-btn"
                    disabled={chatLoading || !inputVal.trim()}
                    aria-label="Send message"
                  >
                    ↑
                  </button>
                </div>
                {chatMessages.length > 0 && (
                  <button
                    type="button"
                    className="chat-clear-link"
                    onClick={clearChat}
                    title="Clear message history and start a new conversation"
                    aria-label="Clear chat history"
                  >
                    Clear chat
                  </button>
                )}
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
