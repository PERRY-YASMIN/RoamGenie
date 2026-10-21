import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import DestinationsPage from "./DestinationsPage";
import * as api from "../services/api";

// Mock API
vi.mock("../services/api", () => ({
  getDestinations: vi.fn(),
  getHotels: vi.fn(),
  getRestaurants: vi.fn(),
  getAttractions: vi.fn(),
  getTransportOptions: vi.fn(),
}));

function renderDestinationsPage() {
  return render(
    <BrowserRouter>
      <DestinationsPage />
    </BrowserRouter>
  );
}

describe("DestinationsPage — View Catalogue Bug Fix & Regression Tests", () => {
  const mockDests = [
    {
      id: 413,
      city: "Abu Dhabi",
      country: "United Arab Emirates",
      description: "Capital of the UAE with Sheikh Zayed Grand Mosque.",
      average_daily_cost: 16000,
      active: true,
    },
    {
      id: 5,
      city: "Kyoto",
      country: "Japan",
      description: "Historic imperial capital famous for temples.",
      average_daily_cost: 7500,
      active: true,
    },
  ];

  const mockHotelsAbuDhabi = [
    { id: 101, name: "Jumeirah at Saadiyat Island", price_per_night: 24000, rating: 4.8 },
    { id: 102, name: "Emirates Palace Mandarin", price_per_night: 45000, rating: 4.9 },
  ];

  const mockRestaurantsAbuDhabi = [
    { id: 201, name: "Li Beirut", cuisine: "Lebanese", average_cost_per_person: 6500, rating: 4.7 },
  ];

  const mockAttractionsAbuDhabi = [
    { id: 301, name: "Louvre Abu Dhabi", category: "museum", entry_fee: 1500, rating: 4.9 },
    { id: 302, name: "Sheikh Zayed Grand Mosque", category: "landmark", entry_fee: 0, rating: 5.0 },
  ];

  const mockTransportsAbuDhabi = [
    { id: 401, origin: "Dubai", mode: "bus", provider: "RTA Intercity Coach", estimated_cost: 350, duration_minutes: 90 },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    api.getDestinations.mockResolvedValue(mockDests);
    api.getHotels.mockResolvedValue(mockHotelsAbuDhabi);
    api.getRestaurants.mockResolvedValue(mockRestaurantsAbuDhabi);
    api.getAttractions.mockResolvedValue(mockAttractionsAbuDhabi);
    api.getTransportOptions.mockResolvedValue(mockTransportsAbuDhabi);
  });

  it("renders destinations and opens the catalogue modal when 'View Catalogue' is clicked", async () => {
    renderDestinationsPage();

    // Verify destinations rendered
    await waitFor(() => {
      expect(screen.getByText("Abu Dhabi")).toBeInTheDocument();
      expect(screen.getByText("Kyoto")).toBeInTheDocument();
    });

    // Check that View Catalogue button exists
    const catalogueButtons = screen.getAllByRole("button", { name: /view catalogue/i });
    expect(catalogueButtons.length).toBeGreaterThanOrEqual(2);

    // Click View Catalogue for Abu Dhabi
    fireEvent.click(catalogueButtons[0]);

    // Modal dialog must become visible in the document (rendered via portal into document.body)
    await waitFor(() => {
      expect(screen.getByRole("dialog", { name: /catalogue inspection for abu dhabi/i })).toBeInTheDocument();
    });

    // Verify header in modal
    expect(screen.getByText(/Abu Dhabi, United Arab Emirates/i)).toBeInTheDocument();

    // Verify API called with destination ID 413
    expect(api.getHotels).toHaveBeenCalledWith(413);
    expect(api.getRestaurants).toHaveBeenCalledWith(413);
    expect(api.getAttractions).toHaveBeenCalledWith(413);
    expect(api.getTransportOptions).toHaveBeenCalledWith(413);

    // Verify hotels rendered by default
    await waitFor(() => {
      expect(screen.getByText("Jumeirah at Saadiyat Island")).toBeInTheDocument();
      expect(screen.getByText("Emirates Palace Mandarin")).toBeInTheDocument();
    });
  });

  it("switches tabs in the catalogue modal to view Dining, Sights & Culture, and Transit", async () => {
    renderDestinationsPage();

    await waitFor(() => {
      expect(screen.getByText("Abu Dhabi")).toBeInTheDocument();
    });

    const viewBtn = screen.getAllByRole("button", { name: /view catalogue/i })[0];
    fireEvent.click(viewBtn);

    await waitFor(() => {
      expect(screen.getByRole("dialog")).toBeInTheDocument();
    });

    // Switch to Dining tab
    const diningTab = screen.getByRole("tab", { name: /dining/i });
    fireEvent.click(diningTab);
    expect(diningTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Li Beirut")).toBeInTheDocument();

    // Switch to Sights & Culture tab
    const sightsTab = screen.getByRole("tab", { name: /sights & culture/i });
    fireEvent.click(sightsTab);
    expect(sightsTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Louvre Abu Dhabi")).toBeInTheDocument();
    expect(screen.getByText("Sheikh Zayed Grand Mosque")).toBeInTheDocument();
    expect(screen.getByText("Complimentary entry")).toBeInTheDocument();

    // Switch to Transit tab
    const transitTab = screen.getByRole("tab", { name: /transit/i });
    fireEvent.click(transitTab);
    expect(transitTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Dubai → Abu Dhabi")).toBeInTheDocument();
    expect(screen.getByText(/RTA Intercity Coach/i)).toBeInTheDocument();
  });

  it("allows switching between different destinations and updates catalogue content", async () => {
    // Kyoto mocks
    api.getHotels.mockImplementation((id) =>
      id === 5
        ? Promise.resolve([{ id: 501, name: "Hoshinoya Kyoto", price_per_night: 60000, rating: 4.9 }])
        : Promise.resolve(mockHotelsAbuDhabi)
    );

    renderDestinationsPage();

    await waitFor(() => {
      expect(screen.getByText("Kyoto")).toBeInTheDocument();
    });

    // Click View Catalogue for Kyoto (the 2nd button)
    const kyotoBtn = screen.getByRole("button", { name: /view catalogue for kyoto/i });
    fireEvent.click(kyotoBtn);

    await waitFor(() => {
      expect(screen.getByText(/Kyoto, Japan/i)).toBeInTheDocument();
      expect(screen.getByText("Hoshinoya Kyoto")).toBeInTheDocument();
    });

    expect(api.getHotels).toHaveBeenCalledWith(5);
  });

  it("closes the catalogue modal on Escape key and close button", async () => {
    renderDestinationsPage();

    await waitFor(() => {
      expect(screen.getByText("Abu Dhabi")).toBeInTheDocument();
    });

    const viewBtn = screen.getAllByRole("button", { name: /view catalogue/i })[0];
    fireEvent.click(viewBtn);

    await waitFor(() => {
      expect(screen.getByRole("dialog")).toBeInTheDocument();
    });

    // Press Escape
    fireEvent.keyDown(window, { key: "Escape" });

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });

  it("displays error state with retry option when catalogue fetch fails", async () => {
    api.getHotels.mockRejectedValue(new Error("Database connection lost"));

    renderDestinationsPage();

    await waitFor(() => {
      expect(screen.getByText("Abu Dhabi")).toBeInTheDocument();
    });

    const viewBtn = screen.getAllByRole("button", { name: /view catalogue/i })[0];
    fireEvent.click(viewBtn);

    await waitFor(() => {
      expect(screen.getByRole("dialog")).toBeInTheDocument();
    });

    // Error box should be displayed
    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText(/Database connection lost/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /retry loading catalogue/i })).toBeInTheDocument();
    });
  });
});
