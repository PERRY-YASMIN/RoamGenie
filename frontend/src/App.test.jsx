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
});
