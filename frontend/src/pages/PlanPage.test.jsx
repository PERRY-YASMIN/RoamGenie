import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AuthProvider } from "../context/AuthContext";
import { CopilotProvider } from "../context/CopilotContext";
import { ToastProvider } from "../context/ToastContext";
import PlanPage from "./PlanPage";
import * as api from "../services/api";

// Mock API services
vi.mock("../services/api", () => ({
  getDestinations: vi.fn(),
  getTrip: vi.fn(),
  createTrip: vi.fn(),
  generateTripPlan: vi.fn(),
  getTripWeather: vi.fn(),
  getPackingItems: vi.fn(),
  togglePackingItem: vi.fn(),
  addPackingItem: vi.fn(),
  deletePackingItem: vi.fn(),
  updateTrip: vi.fn(),
  toggleSaveTrip: vi.fn(),
  getHotels: vi.fn(),
  getRestaurants: vi.fn(),
  getAttractions: vi.fn(),
  getTransportOptions: vi.fn(),
  swapItineraryItem: vi.fn(),
  listTrips: vi.fn().mockResolvedValue([]),
  listSavedTrips: vi.fn().mockResolvedValue([]),
}));

function renderPlanPage() {
  return render(
    <BrowserRouter>
      <ToastProvider>
        <AuthProvider>
          <CopilotProvider>
            <PlanPage />
          </CopilotProvider>
        </AuthProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

describe("PlanPage Remediation & Accessibility Tests (WCAG 2.2 AA)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.getDestinations.mockResolvedValue([
      { id: 1, city: "Kargil", country: "India", average_daily_cost: 3200 },
      { id: 2, city: "Mysuru", country: "India", average_daily_cost: 2800 },
    ]);
    api.getPackingItems.mockResolvedValue([
      { id: 10, item: "Thermal base layers", is_packed: false },
      { id: 11, item: "UV Sunglasses", is_packed: true },
    ]);
    api.getTripWeather.mockResolvedValue({
      city: "Kargil",
      temperature_c: -6,
      current_summary: "Cold mountain breeze",
    });
  });

  it("renders the Trip Parameters form in a contained panel with persistent associated labels", async () => {
    const { container } = renderPlanPage();

    expect(screen.getByText("Plan Your Optimized Journey")).toBeInTheDocument();
    expect(screen.getByText("Trip Parameters")).toBeInTheDocument();

    const panel = container.querySelector(".planner-form-panel");
    expect(panel).toBeInTheDocument();

    // Check persistent programmatically associated form labels
    const destLabel = screen.getByLabelText(/Where are you going\?/i);
    expect(destLabel).toBeInTheDocument();

    const depInput = screen.getByLabelText(/DEPARTURE/i);
    expect(depInput).toBeInTheDocument();
    expect(depInput).toHaveAttribute("id", "start_date");

    const retInput = screen.getByLabelText(/RETURN/i);
    expect(retInput).toBeInTheDocument();
    expect(retInput).toHaveAttribute("id", "end_date");

    const travInput = screen.getByLabelText(/TRAVELLERS/i);
    expect(travInput).toBeInTheDocument();
    expect(travInput).toHaveAttribute("id", "traveller_count");

    const originInput = screen.getByLabelText(/ORIGIN/i);
    expect(originInput).toBeInTheDocument();
    expect(originInput).toHaveAttribute("id", "starting_location");

    const budgetSlider = screen.getByLabelText(/Trip budget in Rupees/i);
    expect(budgetSlider).toBeInTheDocument();
    expect(budgetSlider).toHaveAttribute("id", "total_budget");
  });

  it("generates an itinerary in guest mode and renders the explicit budget deficit warning panel", async () => {
    const { container } = renderPlanPage();

    // Select a destination
    const destInput = screen.getByPlaceholderText(/Search destination city or country\.\.\./i);
    fireEvent.focus(destInput);
    fireEvent.change(destInput, { target: { value: "Kargil" } });

    await waitFor(() => {
      expect(screen.getByText("Kargil")).toBeInTheDocument();
    });

    const destOption = screen.getByRole("option", { name: /Kargil/i });
    fireEvent.mouseDown(destOption);

    // Set a budget that creates a deficit: expenses are ~33,000, set budget to 15,000
    const budgetSlider = screen.getByLabelText(/Trip budget in Rupees/i);
    fireEvent.change(budgetSlider, { target: { value: "15000", name: "total_budget" } });

    // Submit form to generate itinerary
    const submitBtn = screen.getByRole("button", { name: /Generate Optimized Itinerary/i });
    fireEvent.click(submitBtn);

    // Verify inline workflow feedback banner
    await waitFor(() => {
      expect(screen.getByText("Itinerary Generated Successfully")).toBeInTheDocument();
    });

    // Verify timeline container panel
    const timelinePanel = container.querySelector(".timeline-container-panel");
    expect(timelinePanel).toBeInTheDocument();

    // Verify day tabs
    expect(screen.getByRole("tab", { name: /Day 01/i })).toBeInTheDocument();

    // Verify explicit budget deficit warning panel (Issue B: Deficit Status Alert)
    const deficitAlert = screen.getByRole("alert", { name: /Budget Deficit Warning/i });
    expect(deficitAlert).toBeInTheDocument();
    expect(screen.getByText(/WARNING: OVER BUDGET/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Deficit/i).length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/exceed your allocated budget/i)).toBeInTheDocument();
  });

  it("renders the packing checklist without harsh blue selection and supports accessible interaction", async () => {
    // Generate trip with packing items
    api.createTrip.mockResolvedValue({ id: 99 });
    api.generateTripPlan.mockResolvedValue({
      itinerary: {
        destination_city: "Kargil",
        summary: "Kargil Journey",
        days: [{ day_number: 1, date: "2026-11-01", items: [] }],
      },
      budget_summary: {
        total_budget: 80000,
        estimated_total: 50000,
        remaining_budget: 30000,
        deficit_amount: 0,
        is_over_budget: false,
      },
      warnings: [],
    });

    const { container } = renderPlanPage();

    // Trigger guest generation
    const destInput = screen.getByPlaceholderText(/Search destination city or country\.\.\./i);
    fireEvent.focus(destInput);
    fireEvent.change(destInput, { target: { value: "Kargil" } });

    await waitFor(() => {
      expect(screen.getByText("Kargil")).toBeInTheDocument();
    });

    fireEvent.mouseDown(screen.getByRole("option", { name: /Kargil/i }));

    const submitBtn = screen.getByRole("button", { name: /Generate Optimized Itinerary/i });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Trip Packing Checklist")).toBeInTheDocument();
    });

    const packingSection = container.querySelector(".packing-editorial-section");
    expect(packingSection).toBeInTheDocument();
  });

  it("renders Dual-Time-Zone selector and converts activity times when switching between Destination and Origin time", async () => {
    api.getDestinations.mockResolvedValue([
      { id: 413, city: "Abu Dhabi", country: "United Arab Emirates", average_daily_cost: 16000 },
    ]);

    renderPlanPage();

    // Select Abu Dhabi
    const destInput = screen.getByPlaceholderText(/Search destination city or country\.\.\./i);
    fireEvent.focus(destInput);
    fireEvent.change(destInput, { target: { value: "Abu Dhabi" } });

    await waitFor(() => {
      expect(screen.getByText("Abu Dhabi")).toBeInTheDocument();
    });

    fireEvent.mouseDown(screen.getByRole("option", { name: /Abu Dhabi/i }));

    // Origin is default "Delhi"
    const submitBtn = screen.getByRole("button", { name: /Generate Optimized Itinerary/i });
    fireEvent.click(submitBtn);

    // Wait for itinerary generation
    await waitFor(() => {
      expect(screen.getByRole("region", { name: /itinerary time zone display options/i })).toBeInTheDocument();
    });

    // Verify dual timezone selector is rendered
    const destRadio = screen.getByRole("radio", { name: /destination time: abu dhabi, gst, utc\+04:00/i });
    const originRadio = screen.getByRole("radio", { name: /origin time: delhi, ist, utc\+05:30/i });
    expect(destRadio).toBeInTheDocument();
    expect(originRadio).toBeInTheDocument();
    expect(destRadio).toHaveAttribute("aria-checked", "true");

    // Initially in Destination Time (Abu Dhabi GST)
    // Guest mode Day 1 item 1 is at 09:30 AM
    expect(screen.getByText("09:30 AM")).toBeInTheDocument();
    expect(screen.getByText(/Morning · GST/i)).toBeInTheDocument();

    // Switch to Origin Time (Delhi IST: UTC+4 -> UTC+5:30 is +1.5h -> 11:00 AM)
    fireEvent.click(originRadio);
    expect(originRadio).toHaveAttribute("aria-checked", "true");
    expect(destRadio).toHaveAttribute("aria-checked", "false");

    // Converted time is now 11:00 AM
    expect(screen.getByText("11:00 AM")).toBeInTheDocument();
    expect(screen.getByText(/Morning · IST/i)).toBeInTheDocument();

    // Active timezone banner shows Origin Time
    expect(screen.getByText(/Times converted from Abu Dhabi schedule/i)).toBeInTheDocument();

    // Switch back to Destination Time
    fireEvent.click(destRadio);
    expect(destRadio).toHaveAttribute("aria-checked", "true");
    expect(screen.getByText("09:30 AM")).toBeInTheDocument();
    expect(screen.getByText(/Morning · GST/i)).toBeInTheDocument();
  });
});
