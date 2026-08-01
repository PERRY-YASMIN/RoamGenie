import { afterEach, describe, expect, it, vi } from "vitest";
import { previewPlan } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("previewPlan", () => {
  it("returns structured API data", async () => {
    const payload = { destination: "Mysuru" };
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ provider: "mock" }) }));
    await expect(previewPlan(payload)).resolves.toEqual({ provider: "mock" });
    expect(fetch).toHaveBeenCalledOnce();
  });

  it("uses a safe fallback message for an unreadable error", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, json: async () => { throw new Error("bad body"); } }));
    await expect(previewPlan({})).rejects.toThrow("Could not create the preview.");
  });
});
