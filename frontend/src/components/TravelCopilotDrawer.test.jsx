import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../context/AuthContext";
import { CopilotProvider } from "../context/CopilotContext";
import TravelCopilotDrawer from "./TravelCopilotDrawer";

vi.mock("../services/api", () => ({
  listTrips: vi.fn().mockResolvedValue([]),
  listSavedTrips: vi.fn().mockResolvedValue([]),
  sendCopilotMessage: vi.fn(),
  executeProposal: vi.fn(),
}));

function renderDrawer() {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <CopilotProvider>
          <TravelCopilotDrawer />
        </CopilotProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

describe("TravelCopilotDrawer Visual & Accessibility Remediation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders floating trigger with accessible attributes and opens drawer on click", () => {
    renderDrawer();

    const triggerBtn = screen.getByRole("button", { name: /Open RoamGenie AI Assistant/i });
    expect(triggerBtn).toBeInTheDocument();
    expect(triggerBtn).toHaveAttribute("aria-expanded", "false");

    fireEvent.click(triggerBtn);

    const dialog = screen.getByRole("dialog", { name: /RoamGenie AI Travel Assistant/i });
    expect(dialog).toBeInTheDocument();
    expect(dialog).toHaveAttribute("aria-modal", "true");
  });

  it("closes the drawer on Escape key press", async () => {
    renderDrawer();

    const triggerBtn = screen.getByRole("button", { name: /Open RoamGenie AI Assistant/i });
    fireEvent.click(triggerBtn);

    expect(screen.getByRole("dialog", { name: /RoamGenie AI Travel Assistant/i })).toBeInTheDocument();

    fireEvent.keyDown(window, { key: "Escape" });

    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: /RoamGenie AI Travel Assistant/i })).not.toBeInTheDocument();
    });
  });

  it("has accessible close button with proper aria-label", () => {
    renderDrawer();

    const triggerBtn = screen.getByRole("button", { name: /Open RoamGenie AI Assistant/i });
    fireEvent.click(triggerBtn);

    const closeBtn = screen.getByRole("button", { name: /Close RoamGenie AI drawer/i });
    expect(closeBtn).toBeInTheDocument();

    fireEvent.click(closeBtn);
    expect(screen.queryByRole("dialog", { name: /RoamGenie AI Travel Assistant/i })).not.toBeInTheDocument();
  });
});
