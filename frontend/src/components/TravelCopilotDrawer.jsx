import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCopilot } from "../context/CopilotContext";
import {
  IconClose,
  IconSend,
  IconCompass,
  IconTrash,
  IconArrowRight,
  IconHelpCircle,
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

function ProposalCard({ proposal, status, errorMessage, onConfirm, onReject, isApplying }) {
  if (!proposal) return null;

  const {
    action = "swap",
    original_item,
    proposed_item,
    budget_impact = {},
    summary,
  } = proposal;

  const originalTotal = budget_impact.original_estimated_total ?? 0;
  const proposedTotal = budget_impact.proposed_estimated_total ?? 0;
  const savings = budget_impact.savings ?? 0;
  const extraCost = budget_impact.extra_cost ?? 0;
  const hasSavings = Number(savings) > 0;
  const hasExtra = Number(extraCost) > 0;

  const isApplied = status === "applied";
  const isRejected = status === "rejected";
  const isFailed = status === "failed";

  return (
    <div
      className={`chat-proposal-card ${isApplied ? "applied" : ""} ${isRejected ? "rejected" : ""} ${isFailed ? "failed" : ""}`}
    >
      <div className="proposal-card-header">
        <span className="proposal-badge">
          <span className="copilot-btn-icon snowflake-emoji" aria-hidden="true">❄️</span>
          <span>
            {action === "clear_day"
              ? "PROPOSED DAY CANCELLATION"
              : `PROPOSED ITINERARY ${action.toUpperCase()}`}
          </span>
        </span>
        {isApplied && <span className="proposal-state-tag applied">✓ Applied</span>}
        {isRejected && <span className="proposal-state-tag rejected">✕ Declined</span>}
        {isFailed && <span className="proposal-state-tag failed">✕ Failed</span>}
      </div>

      {/* Visual Diff: Original vs Proposed */}
      <div className="proposal-diff-grid">
        {action === "clear_day" ? (
          <div className="proposal-diff-box original">
            <div className="diff-label">CURRENT SCHEDULE</div>
            <div className="diff-title">
              Day {proposal.target_day_number || proposal.day_number || 1} Plans
            </div>
            <div className="diff-meta">
              <span className="diff-category">Itinerary Day</span>
              {hasSavings && <span className="diff-cost">Saves ₹{Number(savings).toLocaleString()}</span>}
            </div>
          </div>
        ) : original_item ? (
          <div className="proposal-diff-box original">
            <div className="diff-label">CURRENT ITEM</div>
            <div className="diff-title" title={original_item.title}>
              {original_item.title}
            </div>
            <div className="diff-meta">
              <span className="diff-category">{original_item.category}</span>
              <span className="diff-cost">₹{Number(original_item.estimated_cost || 0).toLocaleString()}</span>
            </div>
          </div>
        ) : null}

        {(action === "swap" || action === "clear_day" || (original_item && proposed_item)) && (
          <div className="diff-arrow" aria-hidden="true">
            <IconArrowRight size={18} />
          </div>
        )}

        {action === "clear_day" ? (
          <div className="proposal-diff-box proposed">
            <div className="diff-label">PROPOSED SCHEDULE</div>
            <div className="diff-title">
              Clear Day (Unscheduled / Free Day)
            </div>
            <div className="diff-meta">
              <span className="diff-category">No Activities</span>
              <span className="diff-cost">₹0</span>
            </div>
          </div>
        ) : proposed_item ? (
          <div className="proposal-diff-box proposed">
            <div className="diff-label">PROPOSED REPLACEMENT</div>
            <div className="diff-title" title={proposed_item.title}>
              {proposed_item.title}
            </div>
            <div className="diff-meta">
              <span className="diff-category">{proposed_item.category}</span>
              <span className="diff-cost">₹{Number(proposed_item.estimated_cost || 0).toLocaleString()}</span>
            </div>
          </div>
        ) : null}
      </div>

      {/* Financial Impact Comparison */}
      <div className="proposal-financial-impact">
        <div className="impact-header">
          <span className="impact-label">FINANCIAL IMPACT</span>
          {hasSavings && (
            <span className="impact-delta savings">
              ↓ ₹{Number(savings).toLocaleString()} Savings
            </span>
          )}
          {hasExtra && (
            <span className="impact-delta deficit">
              ↑ ₹{Number(extraCost).toLocaleString()} Deficit
            </span>
          )}
          {!hasSavings && !hasExtra && (
            <span className="impact-delta neutral">Net Zero Change</span>
          )}
        </div>

        <div className="impact-numbers-row">
          <div className="impact-num-col">
            <span className="num-caption">Current Trip Estimate</span>
            <span className="num-val">₹{Number(originalTotal).toLocaleString()}</span>
          </div>
          <div className="impact-arrow" aria-hidden="true">→</div>
          <div className="impact-num-col">
            <span className="num-caption">New Trip Estimate</span>
            <span className={`num-val ${hasSavings ? "text-savings" : hasExtra ? "text-deficit" : ""}`}>
              ₹{Number(proposedTotal).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {summary && (
        <p className="proposal-summary-note">{summary}</p>
      )}

      {isFailed && (
        <div className="proposal-error-note">
          <span className="error-note-title">Update Failed:</span> {errorMessage || "This change violates your budget or itinerary constraints."}
        </div>
      )}

      {/* Interactive Action Buttons */}
      {!isApplied && !isRejected && !isFailed && (
        <div className="proposal-actions-row">
          <button
            type="button"
            className="proposal-btn apply-btn"
            onClick={() => {
              if (!isApplying) onConfirm();
            }}
            disabled={isApplying}
          >
            {isApplying ? "Applying Changes..." : "Apply Changes"}
          </button>
          <button
            type="button"
            className="proposal-btn reject-btn"
            onClick={() => {
              if (!isApplying) onReject();
            }}
            disabled={isApplying}
          >
            Reject
          </button>
        </div>
      )}
    </div>
  );
}

function ClarificationCard({ clarification, onSelect, disabled }) {
  const [selectedOption, setSelectedOption] = useState("");
  const [customText, setCustomText] = useState("");
  const [isSubmitted, setIsSubmitted] = useState(false);

  if (!clarification) return null;

  const {
    question = "Which option would you like to choose?",
    options = [],
    allow_custom_input = true,
  } = clarification;

  const isOther = selectedOption === "__OTHER__";
  const finalValue = isOther ? customText.trim() : selectedOption;

  const handleOptionClick = (opt) => {
    if (disabled || isSubmitted) return;
    setSelectedOption(opt);
  };

  const handleSelectOther = () => {
    if (disabled || isSubmitted) return;
    setSelectedOption("__OTHER__");
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!finalValue || disabled || isSubmitted) return;
    setIsSubmitted(true);
    onSelect(finalValue);
  };

  return (
    <div className={`chat-clarification-card ${isSubmitted ? "submitted" : ""}`}>
      <div className="clarification-card-header">
        <span className="clarification-badge">
          <IconHelpCircle size={13} />
          <span>CHOICE NEEDED</span>
        </span>
        {isSubmitted && <span className="clarification-state-tag">✓ Answered</span>}
      </div>

      <div className="clarification-question">{question}</div>

      <div className="clarification-options-list" role="radiogroup" aria-label={question}>
        {options.map((opt, oIdx) => {
          const isSelected = selectedOption === opt;
          return (
            <button
              key={oIdx}
              type="button"
              role="radio"
              aria-checked={isSelected}
              className={`clarification-option-pill ${isSelected ? "selected" : ""}`}
              onClick={() => handleOptionClick(opt)}
              disabled={disabled || isSubmitted}
            >
              <span className="clarification-radio-indicator" aria-hidden="true">
                {isSelected && <span className="radio-dot" />}
              </span>
              <span className="option-text">{opt}</span>
            </button>
          );
        })}

        {allow_custom_input && (
          <div className="clarification-custom-container">
            <button
              type="button"
              role="radio"
              aria-checked={isOther}
              className={`clarification-option-pill ${isOther ? "selected" : ""}`}
              onClick={handleSelectOther}
              disabled={disabled || isSubmitted}
            >
              <span className="clarification-radio-indicator" aria-hidden="true">
                {isOther && <span className="radio-dot" />}
              </span>
              <span className="option-text">Other...</span>
            </button>

            {isOther && !isSubmitted && (
              <div className="clarification-custom-input-box">
                <input
                  type="text"
                  className="clarification-text-field"
                  placeholder="Specify day, date or activity..."
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleSubmit();
                    }
                  }}
                  disabled={disabled || isSubmitted}
                  autoFocus
                />
              </div>
            )}
          </div>
        )}
      </div>

      {!isSubmitted && (
        <div className="clarification-action-row">
          <button
            type="button"
            className="clarification-submit-btn"
            onClick={handleSubmit}
            disabled={disabled || !finalValue}
          >
            Submit Selection
          </button>
        </div>
      )}
    </div>
  );
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
    confirmProposal,
    rejectProposal,
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
    executeChatMessage(inputVal, activeTripId || activeTrip?.id || null);
    setInputVal("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleQuickPrompt = (prompt) => {
    executeChatMessage(prompt, activeTripId || activeTrip?.id || null);
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
        className={`copilot-floating-btn ${isOpen ? "is-on" : ""}`}
        onClick={toggleCopilot}
        aria-label="Open RoamGenie AI Assistant"
        aria-expanded={isOpen}
        title={destName ? `RoamGenie AI Assistant · ${destName}` : "RoamGenie AI Assistant"}
      >
        <span className="sound-emoji snowflake-emoji" aria-hidden="true">
          ❄️
        </span>
        <span className="sr-only">RoamGenie AI</span>
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
                <h3 className="chat-title">
                  <span className="copilot-title-icon snowflake-emoji" aria-hidden="true">❄️</span> RoamGenie AI
                </h3>
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
                  value={activeTripId || activeTrip?.id || ""}
                  onChange={(e) => {
                    const val = e.target.value;
                    selectTrip(val ? Number(val) : null);
                  }}
                  aria-label="Select trip context for AI assistant"
                >
                  <option value="">No trip connected (General advice)</option>
                  {activeTrip && !userTrips.some((t) => String(t.id) === String(activeTrip.id)) && (
                    <option key={activeTrip.id || "active"} value={activeTrip.id}>
                      {activeTrip.destination_city || activeTrip.destination?.city || `Trip #${activeTrip.id}`}
                      {activeTrip.start_date && activeTrip.end_date ? ` (${formatTripDates(activeTrip.start_date, activeTrip.end_date)})` : ""}
                    </option>
                  )}
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

                    {/* Interactive Itinerary Modification Proposal Card */}
                    {msg.proposed_changes && (
                      <ProposalCard
                        proposal={msg.proposed_changes}
                        status={msg.proposal_status || "pending"}
                        errorMessage={msg.proposal_error}
                        onConfirm={() => confirmProposal(msg.proposed_changes, idx)}
                        onReject={() => rejectProposal(msg.proposed_changes, idx)}
                        isApplying={chatLoading}
                      />
                    )}

                    {/* Interactive Clarification Engine Card */}
                    {msg.clarification_request && (
                      <ClarificationCard
                        clarification={msg.clarification_request}
                        onSelect={(choice) => handleQuickPrompt(choice)}
                        disabled={chatLoading}
                      />
                    )}

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
