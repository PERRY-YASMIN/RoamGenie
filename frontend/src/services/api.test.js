import { afterEach, describe, expect, it, vi } from "vitest";
import { previewPlan, swapItineraryItem } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("previewPlan", () => {
  it("returns structured API data", async () => {
    const payload = { destination: "Mysuru" };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ provider: "deterministic-scheduler" }) }));
    await expect(previewPlan(payload)).resolves.toEqual({ provider: "deterministic-scheduler" });
    expect(fetch).toHaveBeenCalledOnce();
  });

  it("uses a safe fallback message for an unreadable error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, json: async () => { throw new Error("bad body"); } }));
    await expect(previewPlan({})).rejects.toThrow("Could not create the preview.");
  });
});

describe("swapItineraryItem", () => {
  it("sends PATCH request to the correct trip item URL with payload", async () => {
    const mockTrip = { id: 42, estimated_total: "15000.00" };
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockTrip,
      })
    );

    const payload = { replacement_type: "hotel", replacement_id: 5 };
    const result = await swapItineraryItem(42, 101, payload);

    expect(result).toEqual(mockTrip);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/trips/42/itinerary/items/101"),
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify(payload),
      })
    );
  });

  it("handles swap API error responses with detail message", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: "Cannot replace a 'food' event with a hotel entity." }),
      })
    );

    await expect(
      swapItineraryItem(42, 101, { replacement_type: "hotel", replacement_id: 5 })
    ).rejects.toThrow("Cannot replace a 'food' event with a hotel entity.");
  });
});

describe("chatAssistant", () => {
  it("sends POST request to /assistant/chat with message, tripId, and conversationId", async () => {
    const { chatAssistant } = await import("./api");
    const mockChatResp = {
      conversation_id: 12,
      trip_id: 5,
      reply: "Based on your Jaipur itinerary, pack cottons.",
      provider: "ai-gemini",
      suggested_actions: ["View Checklist"],
    };

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockChatResp,
      })
    );

    const res = await chatAssistant("What should I pack?", 5, 12);
    expect(res).toEqual(mockChatResp);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/assistant/chat"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ message: "What should I pack?", trip_id: 5, conversation_id: 12 }),
      })
    );
  });

  it("handles assistant API error gracefully", async () => {
    const { chatAssistant } = await import("./api");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({ detail: "Access denied to this trip." }),
      })
    );

    await expect(chatAssistant("Hello", 99)).rejects.toThrow("Access denied to this trip.");
  });
});

