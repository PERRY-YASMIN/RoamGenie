import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { chatAssistant, executeChatProposal, getTrip, listTrips } from "../services/api";

const CopilotContext = createContext(null);

export function CopilotProvider({ children }) {
  const { isAuthenticated } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [activeTripId, setActiveTripId] = useState(null);
  const [activeTrip, setActiveTrip] = useState(null);
  const [userTrips, setUserTrips] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);

  // Load user trips when authenticated
  const refreshUserTrips = useCallback(async () => {
    if (!isAuthenticated) {
      setUserTrips([]);
      setActiveTripId(null);
      setActiveTrip(null);
      return;
    }
    try {
      const trips = await listTrips();
      setUserTrips(trips || []);

      // Keep activeTripId if it exists in userTrips, or default to the first confirmed trip
      setActiveTripId((currentId) => {
        if (!trips || trips.length === 0) {
          return null;
        }
        if (currentId && trips.some((t) => t.id === currentId)) {
          return currentId;
        }
        return trips[0].id;
      });
    } catch {
      // Non-blocking
    }
  }, [isAuthenticated]);

  useEffect(() => {
    refreshUserTrips();
  }, [refreshUserTrips]);

  // When activeTripId changes, fetch full trip details if not already complete
  useEffect(() => {
    if (!activeTripId || !isAuthenticated) {
      setActiveTrip(null);
      return;
    }
    let isMounted = true;
    getTrip(activeTripId)
      .then((detail) => {
        if (isMounted && detail) {
          setActiveTrip(detail);
        }
      })
      .catch(() => {
        // Fall back to matching item in userTrips if detail call fails
        const matched = userTrips.find((t) => t.id === activeTripId);
        if (isMounted) {
          setActiveTrip(matched || null);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [activeTripId, isAuthenticated, userTrips]);

  // Reset conversation on logout
  useEffect(() => {
    if (!isAuthenticated) {
      setChatMessages([]);
      setConversationId(null);
      setActiveTripId(null);
      setActiveTrip(null);
      setUserTrips([]);
    }
  }, [isAuthenticated]);

  const openCopilot = useCallback((tripId = null) => {
    if (tripId) {
      const id = Number(tripId);
      setActiveTripId(id);
      const matched = userTrips.find((t) => t.id === id);
      if (matched) {
        setActiveTrip(matched);
      }
    } else if (!activeTripId && userTrips.length > 0) {
      setActiveTripId(userTrips[0].id);
      setActiveTrip(userTrips[0]);
    }
    setIsOpen(true);
  }, [activeTripId, userTrips]);

  const closeCopilot = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleCopilot = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const selectTrip = useCallback((tripId) => {
    const id = tripId ? Number(tripId) : null;
    setActiveTripId(id);
    if (id) {
      const matched = userTrips.find((t) => t.id === id);
      if (matched) {
        setActiveTrip(matched);
      }
    } else {
      setActiveTrip(null);
    }
    setConversationId(null); // start fresh conversation context with the new trip
  }, [userTrips]);

  const clearChat = useCallback(() => {
    setChatMessages([]);
    setConversationId(null);
  }, []);

  const executeChatMessage = useCallback(
    async (text, tripIdOverride = undefined) => {
      const trimmed = text?.trim();
      if (!trimmed || chatLoading) return;

      const userMsg = { role: "user", text: trimmed };
      setChatMessages((prev) => [...prev, userMsg]);
      setChatLoading(true);

      let targetTripId = null;
      if (tripIdOverride !== undefined) {
        targetTripId = tripIdOverride ? Number(tripIdOverride) : null;
      } else if (activeTripId !== null && activeTripId !== undefined) {
        targetTripId = Number(activeTripId);
      } else if (activeTrip?.id) {
        targetTripId = Number(activeTrip.id);
      } else if (userTrips.length > 0) {
        targetTripId = Number(userTrips[0].id);
      }

      try {
        const res = await chatAssistant(trimmed, targetTripId, conversationId);
        if (res.conversation_id) {
          setConversationId(res.conversation_id);
        }
        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: res.reply,
            actions: res.suggested_actions,
            provider: res.provider,
            proposed_changes: res.proposed_changes || null,
            proposal_status: res.proposed_changes ? "pending" : null,
            clarification_request: res.clarification_request || null,
          },
        ]);
      } catch (err) {
        console.error("RoamGenie AI chat error:", err);
        const errReply = "Something went wrong while connecting with RoamGenie AI. Please try again.";
        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: errReply,
            actions: ["Try again", "What should I pack?", "How can I reduce my budget?"],
          },
        ]);
      } finally {
        setChatLoading(false);
      }
    },
    [activeTrip, activeTripId, userTrips, conversationId, chatLoading]
  );

  const confirmProposal = useCallback(
    async (proposal, messageIndex = null) => {
      if (!proposal || chatLoading) return;
      setChatLoading(true);
      try {
        const payload = {
          trip_id: proposal.trip_id,
          action: proposal.action || "swap",
          action_type: proposal.action || "swap",
          target_item_id: proposal.target_item_id || proposal.original_item?.id,
          original_item_id: proposal.target_item_id || proposal.original_item?.id,
          day_number: proposal.target_day_number || proposal.day_number,
          target_day_number: proposal.target_day_number || proposal.day_number,
          replacement_type: proposal.proposed_item?.replacement_type,
          replacement_id: proposal.proposed_item?.replacement_id,
          new_item_id: proposal.proposed_item?.replacement_id,
          title: proposal.proposed_item?.title,
          proposed_item: proposal.proposed_item,
          proposal_id: proposal.proposal_id,
        };

        const res = await executeChatProposal(payload);

        // Instant update of active trip in context
        if (res.trip) {
          setActiveTrip(res.trip);
        } else if (proposal.trip_id) {
          const freshTrip = await getTrip(proposal.trip_id);
          if (freshTrip) setActiveTrip(freshTrip);
        }

        // Refresh trips list so other views are up to date
        refreshUserTrips();

        // Mark proposal status as applied in message history and append confirmation reply
        setChatMessages((prev) => {
          const updated = prev.map((m, idx) => {
            if (
              (messageIndex !== null && idx === messageIndex) ||
              (m.proposed_changes && m.proposed_changes.proposal_id === proposal.proposal_id)
            ) {
              return { ...m, proposal_status: "applied" };
            }
            return m;
          });

          return [
            ...updated,
            {
              role: "assistant",
              text: `Done! ${res.message || "Your itinerary and budget have been safely updated in the database."}`,
              actions: ["Show updated itinerary", "What else can we optimize?"],
            },
          ];
        });
      } catch (err) {
        console.error("Failed to execute proposal:", err);
        const errorDetail = err.message || "This change violates your budget or itinerary constraints.";

        // Mark the proposal as "failed" and record error detail
        setChatMessages((prev) => {
          const updated = prev.map((m, idx) => {
            if (
              (messageIndex !== null && idx === messageIndex) ||
              (m.proposed_changes && m.proposed_changes.proposal_id === proposal.proposal_id)
            ) {
              return { ...m, proposal_status: "failed", proposal_error: errorDetail };
            }
            return m;
          });

          return [
            ...updated,
            {
              role: "assistant",
              text: `Could not apply changes: ${errorDetail}`,
              actions: ["Try again", "What is my current budget?", "Suggest a different option"],
            },
          ];
        });
      } finally {
        setChatLoading(false);
      }
    },
    [chatLoading, refreshUserTrips]
  );

  const rejectProposal = useCallback(
    (proposal, messageIndex = null) => {
      if (!proposal) return;
      // Mark proposal as rejected
      setChatMessages((prev) =>
        prev.map((m, idx) => {
          if (
            (messageIndex !== null && idx === messageIndex) ||
            (m.proposed_changes && m.proposed_changes.proposal_id === proposal.proposal_id)
          ) {
            return { ...m, proposal_status: "rejected" };
          }
          return m;
        })
      );
      // Ask LLM for alternative
      const itemTitle = proposal.original_item?.title || "that item";
      executeChatMessage(
        `I would prefer not to change "${itemTitle}". Can you suggest a different alternative?`,
        proposal.trip_id || activeTripId || activeTrip?.id || null
      );
    },
    [executeChatMessage]
  );

  return (
    <CopilotContext.Provider
      value={{
        isOpen,
        openCopilot,
        closeCopilot,
        toggleCopilot,
        activeTripId,
        activeTrip,
        selectTrip,
        setActiveTrip,
        userTrips,
        refreshUserTrips,
        chatMessages,
        chatLoading,
        conversationId,
        executeChatMessage,
        confirmProposal,
        rejectProposal,
        clearChat,
      }}
    >
      {children}
    </CopilotContext.Provider>
  );
}

export function useCopilot() {
  const context = useContext(CopilotContext);
  if (!context) {
    throw new Error("useCopilot must be used within a CopilotProvider");
  }
  return context;
}
