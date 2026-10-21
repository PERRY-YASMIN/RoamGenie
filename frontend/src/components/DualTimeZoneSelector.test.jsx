import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DualTimeZoneSelector from "./DualTimeZoneSelector";

describe("DualTimeZoneSelector Component", () => {
  it("renders destination and origin options with dynamic locations and time zones (India -> Abu Dhabi)", () => {
    const handleModeChange = vi.fn();

    render(
      <DualTimeZoneSelector
        activeMode="destination"
        onModeChange={handleModeChange}
        origin="Delhi"
        destination="Abu Dhabi"
        referenceDate="2026-10-28"
      />
    );

    // Radiogroup container
    expect(screen.getByRole("radiogroup", { name: /select itinerary display time zone/i })).toBeInTheDocument();

    // Destination Time Option (Abu Dhabi, GST)
    const destRadio = screen.getByRole("radio", { name: /destination time: abu dhabi, gst, utc\+04:00/i });
    expect(destRadio).toBeInTheDocument();
    expect(destRadio).toHaveAttribute("aria-checked", "true");

    // Origin Time Option (Delhi, IST)
    const originRadio = screen.getByRole("radio", { name: /origin time: delhi, ist, utc\+05:30/i });
    expect(originRadio).toBeInTheDocument();
    expect(originRadio).toHaveAttribute("aria-checked", "false");

    // Click origin radio
    fireEvent.click(originRadio);
    expect(handleModeChange).toHaveBeenCalledWith("origin");
  });

  it("supports keyboard navigation with arrow keys", () => {
    const handleModeChange = vi.fn();

    render(
      <DualTimeZoneSelector
        activeMode="destination"
        onModeChange={handleModeChange}
        origin="Delhi"
        destination="Abu Dhabi"
        referenceDate="2026-10-28"
      />
    );

    const radiogroup = screen.getByRole("radiogroup");

    // ArrowRight toggles to origin
    fireEvent.keyDown(radiogroup, { key: "ArrowRight" });
    expect(handleModeChange).toHaveBeenCalledWith("origin");

    // ArrowLeft toggles to destination
    fireEvent.keyDown(radiogroup, { key: "ArrowLeft" });
    expect(handleModeChange).toHaveBeenCalledWith("destination");
  });

  it("detects same time zone for domestic trips (Delhi -> Jaipur)", () => {
    render(
      <DualTimeZoneSelector
        activeMode="destination"
        onModeChange={vi.fn()}
        origin="Delhi"
        destination="Jaipur"
        referenceDate="2026-10-28"
      />
    );

    expect(screen.getByText(/same time zone \(ist\)/i)).toBeInTheDocument();
  });

  it("gracefully displays fallback notice when origin time zone is ambiguous", () => {
    render(
      <DualTimeZoneSelector
        activeMode="origin"
        onModeChange={vi.fn()}
        origin="Atlantis Mysterious Island"
        destination="Abu Dhabi"
        referenceDate="2026-10-28"
      />
    );

    expect(
      screen.getByText(/time zone for origin "atlantis mysterious island" could not be detected automatically/i)
    ).toBeInTheDocument();

    expect(screen.getByRole("button", { name: /choose origin standard time zone/i })).toBeInTheDocument();
  });
});
