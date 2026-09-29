import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";
import { chatAssistant, getTrip, listTrips } from "../services/api";

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

      // Never auto-select a random or default trip.
      // Only keep activeTripId if it was explicitly selected and exists in userTrips.
      setActiveTripId((currentId) => {
        if (!currentId || !trips || trips.length === 0) {
          return null;
        }
        const exists = trips.some((t) => t.id === currentId);
        return exists ? currentId : null;
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
      setActiveTripId(Number(tripId));
    }
    setIsOpen(true);
  }, []);

  const closeCopilot = useCallback(() => {
    setIsOpen(false);
  }, []);

  const toggleCopilot = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const selectTrip = useCallback((tripId) => {
    const id = tripId ? Number(tripId) : null;
    setActiveTripId(id);
    setConversationId(null); // start fresh conversation context with the new trip
  }, []);

  const clearChat = useCallback(() => {
    setChatMessages([]);
    setConversationId(null);
  }, []);

  const executeChatMessage = useCallback(
    async (text) => {
      const trimmed = text?.trim();
      if (!trimmed || chatLoading) return;

      const userMsg = { role: "user", text: trimmed };
      setChatMessages((prev) => [...prev, userMsg]);
      setChatLoading(true);

      const targetTripId = activeTripId || null;

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
          },
        ]);
      } catch (err) {
        console.error("RoamGenie AI chat error:", err);
        const errReply = "Something went wrong while connecting with RoamGenie AI. Please try again.";
        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            text: `⚠️ ${errReply}`,
            actions: ["Try again", "What should I pack?", "How can I reduce my budget?"],
          },
        ]);
      } finally {
        setChatLoading(false);
      }
    },
    [activeTripId, conversationId, chatLoading]
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
