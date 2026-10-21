import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AmbientWorld from "./AmbientWorld";

describe("AmbientWorld — Floating Music Button Remediation", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock HTMLMediaElement methods in jsdom
    window.HTMLMediaElement.prototype.play = vi.fn().mockResolvedValue(undefined);
    window.HTMLMediaElement.prototype.pause = vi.fn();
  });

  it("renders the floating music button with the headphone emoji 🎧", () => {
    render(<AmbientWorld showScene={false} />);

    const button = screen.getByRole("button", { name: /Unmute ambient soundscape/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute("title", "Unmute soundscape");
    expect(button).toHaveAttribute("aria-pressed", "false");
    expect(button).toHaveClass("sound-control");

    // Check for the headphone emoji inside the button
    const noteSpan = button.querySelector(".sound-emoji");
    expect(noteSpan).toBeInTheDocument();
    expect(noteSpan).toHaveTextContent("🎧");
  });

  it("toggles playback state and updates aria attributes when clicked", async () => {
    render(<AmbientWorld showScene={false} />);

    const button = screen.getByRole("button", { name: /Unmute ambient soundscape/i });
    expect(button).toHaveAttribute("aria-pressed", "false");
    expect(button).not.toHaveClass("is-on");

    // Click to turn sound on
    fireEvent.click(button);

    await waitFor(() => {
      expect(window.HTMLMediaElement.prototype.play).toHaveBeenCalled();
      expect(button).toHaveAttribute("aria-pressed", "true");
      expect(button).toHaveAttribute("aria-label", "Mute ambient soundscape");
      expect(button).toHaveAttribute("title", "Mute soundscape");
      expect(button).toHaveClass("is-on");
    });

    // Click again to turn sound off
    fireEvent.click(button);

    await waitFor(() => {
      expect(window.HTMLMediaElement.prototype.pause).toHaveBeenCalled();
      expect(button).toHaveAttribute("aria-pressed", "false");
      expect(button).toHaveAttribute("aria-label", "Unmute ambient soundscape");
      expect(button).toHaveAttribute("title", "Unmute soundscape");
      expect(button).not.toHaveClass("is-on");
    });
  });

  it("maintains audio asset path and looping attribute", () => {
    const { container } = render(<AmbientWorld showScene={false} />);
    const audio = container.querySelector("audio.ambient-audio");

    expect(audio).toBeInTheDocument();
    expect(audio).toHaveAttribute("src", "/kargil-peaceful-wind.mp3");
    expect(audio).toHaveAttribute("loop");
  });
});
