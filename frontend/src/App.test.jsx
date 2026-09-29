import { act, render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "./App";

describe("App Router & Navigation", () => {
  it("renders the navigation and immersive arrival on home route", () => {
    window.history.pushState({}, "Test page", "/");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText("RoamGenie")).toBeInTheDocument();
    expect(screen.getByText("Plan Trip")).toBeInTheDocument();
    expect(screen.getByText("Destinations")).toBeInTheDocument();
    expect(screen.getByText("DBMS Showcase", { exact: false })).toBeInTheDocument();
    expect(screen.getByText("Where the mountains hold their breath.")).toBeInTheDocument();
    expect(screen.getByText("Begin exploring", { exact: false })).toBeInTheDocument();
  });

  it("renders the destination discovery section", () => {
    window.history.pushState({}, "Test page", "/");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText("Start with how you want to feel.")).toBeInTheDocument();
    expect(screen.getByText("Places with a story to tell.")).toBeInTheDocument();
  });

  it("renders the PlanPage in new-trip mode on /plan route", () => {
    window.history.pushState({}, "Plan page", "/plan");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText("Plan Your Optimized Journey")).toBeInTheDocument();
    expect(screen.getByText("Trip Parameters")).toBeInTheDocument();
    expect(screen.getByText("Generate Optimized Itinerary →")).toBeInTheDocument();
  });

  it("handles /plan with tripId and destinationId query parameters safely", () => {
    window.history.pushState({}, "Plan saved trip", "/plan?destinationId=1&tripId=42");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText("Plan Your Optimized Journey")).toBeInTheDocument();
    expect(screen.getByText("Trip Parameters")).toBeInTheDocument();
  });

  it("renders 404 Not Found page on unmatched route", () => {
    window.history.pushState({}, "404 page", "/some-non-existent-route-12345");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText("404 Error")).toBeInTheDocument();
    expect(screen.getByText("Page Not Found")).toBeInTheDocument();
    expect(screen.getByText("Return Home →")).toBeInTheDocument();
  });

  it("displays session expired warning toast when roamgenie:auth-expired event fires", () => {
    window.history.pushState({}, "Test page", "/");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    act(() => {
      window.dispatchEvent(new CustomEvent("roamgenie:auth-expired"));
    });

    expect(screen.getByText("Your session has expired. Please log in again.")).toBeInTheDocument();
  });

  it("renders the floating RoamGenie AI Assistant button and toggles drawer on click", () => {
    window.history.pushState({}, "Test page", "/");
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const copilotBtn = screen.getByRole("button", { name: /Open RoamGenie AI Assistant/i });
    expect(copilotBtn).toBeInTheDocument();
    expect(screen.getByText("RoamGenie AI")).toBeInTheDocument();

    act(() => {
      copilotBtn.click();
    });

    expect(screen.getByRole("dialog", { name: /RoamGenie AI Travel Assistant/i })).toBeInTheDocument();
    expect(screen.getByText("Personalized Travel Assistant")).toBeInTheDocument();
  });

  it("renders the live mountain motion background on the home route", () => {
    window.history.pushState({}, "Home page", "/");
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const world = container.querySelector(".global-world");
    expect(world).toBeInTheDocument();
    expect(world.querySelector(".immersive-scene")).toBeInTheDocument();
    expect(world.querySelector(".scene-sky")).toBeInTheDocument();
    expect(world.querySelector(".scene-clouds")).toBeInTheDocument();
    expect(world.querySelector(".scene-mist")).toBeInTheDocument();
    expect(world.querySelector(".scene-wind-streams")).toBeInTheDocument();
    expect(world.querySelector(".scene-petals")).toBeInTheDocument();
  });

  it("renders the live mountain motion background on inner routes like /plan and /destinations", () => {
    window.history.pushState({}, "Plan page", "/plan");
    const { container } = render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const world = container.querySelector(".global-world");
    expect(world).toBeInTheDocument();
    expect(world.querySelector(".immersive-scene")).toBeInTheDocument();
    expect(world.querySelector(".scene-sky")).toBeInTheDocument();
    expect(world.querySelector(".scene-wind-streams")).toBeInTheDocument();
  });
});
