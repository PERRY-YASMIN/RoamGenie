import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCopilot } from "../context/CopilotContext";
import { useToast } from "../context/ToastContext";
import {
  addPackingItem,
  createTrip,
  deletePackingItem,
  generateTripPlan,
  getAttractions,
  getDestinations,
  getHotels,
  getPackingItems,
  getRestaurants,
  getTransportOptions,
  getTrip,
  getTripWeather,
  previewPlan,
  swapItineraryItem,
  togglePackingItem,
  toggleSaveTrip,
  updateTrip,
} from "../services/api";
import { getAttractionImageUrl, getDestinationImageUrl } from "../utils/destinationImages";
import {
  IconArrowRight,
  IconCalendar,
  IconCheck,
  IconClose,
  IconCompass,
  IconRefresh,
  IconSearch,
  IconSparkles,
  IconSuitcase,
  IconSun,
  IconTrash,
  IconUsers,
  IconWallet,
} from "../components/icons";

const PREFERENCE_TAGS = [
  "Culture",
  "Food",
  "Nature",
  "Adventure",
  "Relaxation",
  "Architecture",
  "Shopping",
  "Nightlife",
];

function getDefaultStartDate() {
  const d = new Date();
  d.setDate(d.getDate() + 7);
  return d.toISOString().split("T")[0];
}

function getDefaultEndDate() {
  const d = new Date();
  d.setDate(d.getDate() + 11);
  return d.toISOString().split("T")[0];
}

function formatDayPart(timeStr) {
  if (!timeStr) return "Morning";
  const hour = parseInt(timeStr.split(":")[0], 10);
  if (isNaN(hour)) return "Daytime";
  if (hour < 12) return "Morning";
  if (hour < 17) return "Afternoon";
  return "Evening";
}

export default function PlanPage() {
  const [searchParams] = useSearchParams();
  const destIdParam = searchParams.get("destinationId");
  const tripIdParam = searchParams.get("tripId");
  const cityParam = searchParams.get("city");

  const { isAuthenticated } = useAuth();
  const { success, error: toastError, info } = useToast();
  const { selectTrip, activeTripId } = useCopilot();

  const [destinations, setDestinations] = useState([]);
  const [destSearchText, setDestSearchText] = useState(cityParam || "");
  const [showDestDropdown, setShowDestDropdown] = useState(false);
  const destDropdownRef = useRef(null);

  const [formData, setFormData] = useState({
    destination_id: destIdParam ? Number(destIdParam) : "",
    starting_location: "Delhi",
    start_date: getDefaultStartDate(),
    end_date: getDefaultEndDate(),
    total_budget: 45000,
    traveller_count: 2,
    preferences: ["Culture", "Food"],
    use_ai: true,
  });

  const [status, setStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [createdTripId, setCreatedTripId] = useState(tripIdParam ? Number(tripIdParam) : null);
  const [selectedDay, setSelectedDay] = useState(1);
  const [weather, setWeather] = useState(null);
  const [packingList, setPackingList] = useState([]);
  const [newPackItem, setNewPackItem] = useState("");
  const [isSaved, setIsSaved] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);

  // Alternative Swap Modal State
  const [swapModalItem, setSwapModalItem] = useState(null);
  const [swapCategory, setSwapCategory] = useState("hotel");
  const [swapAlternatives, setSwapAlternatives] = useState([]);
  const [swapLoading, setSwapLoading] = useState(false);
  const [swapError, setSwapError] = useState("");

  // Load destinations catalogue
  useEffect(() => {
    let isMounted = true;
    getDestinations()
      .then((dests) => {
        if (!isMounted) return;
        setDestinations(dests);
        if (destIdParam && dests.length > 0) {
          const match = dests.find((d) => d.id === Number(destIdParam));
          if (match) {
            setFormData((prev) => ({ ...prev, destination_id: match.id }));
            setDestSearchText(`${match.city}, ${match.country}`);
          }
        }
      })
      .catch((err) => {
        console.error("Failed to load destinations:", err);
      });
    return () => {
      isMounted = false;
    };
  }, [destIdParam]);

  // Click outside listener for destination dropdown
  useEffect(() => {
    function handleClickOutside(event) {
      if (destDropdownRef.current && !destDropdownRef.current.contains(event.target)) {
        setShowDestDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Hydrate saved trip if tripIdParam present
  useEffect(() => {
    let isMounted = true;
    if (!tripIdParam) return;

    async function loadSavedTrip() {
      setStatus("loading");
      setErrorMessage("");
      try {
        const tripData = await getTrip(tripIdParam);
        if (!isMounted) return;

        setCreatedTripId(tripData.id);
        setIsSaved(Boolean(tripData.is_saved));
        setIsConfirmed(tripData.status === "planned" || tripData.status === "confirmed");

        setFormData((prev) => ({
          ...prev,
          destination_id: tripData.destination_id || prev.destination_id,
          starting_location: tripData.starting_location || prev.starting_location,
          start_date: tripData.start_date || prev.start_date,
          end_date: tripData.end_date || prev.end_date,
          traveller_count: tripData.traveller_count || prev.traveller_count,
          total_budget: Number(tripData.total_budget) || prev.total_budget,
        }));

        if (tripData.destination_city) {
          setDestSearchText(tripData.destination_city);
        }

        const activeItinerary = tripData.itineraries?.[0] || null;
        if (activeItinerary) {
          const categoryBreakdown = (tripData.budget_summary?.categories || tripData.budget_allocations || []).map((c) => ({
            category: c.category,
            actual: Number(c.amount),
            allocated: Number(c.amount),
          }));

          const budgetSummary = tripData.budget_summary
            ? {
                ...tripData.budget_summary,
                is_over_budget:
                  tripData.budget_summary.status === "over_budget" ||
                  Number(tripData.estimated_total) > Number(tripData.total_budget),
                deficit_amount: Number(tripData.budget_summary.deficit || 0),
                remaining_budget: Number(tripData.budget_summary.remaining_budget || 0),
                category_breakdown: categoryBreakdown,
              }
            : null;

          setGeneratedPlan({
            itinerary: {
              ...activeItinerary,
              destination_city: tripData.destination_city,
            },
            budget_summary: budgetSummary,
            warnings: tripData.budget_summary?.warnings || [],
          });
          setStatus("success");
          setSelectedDay(1);
        } else {
          setStatus("idle");
        }

        if (tripData.status === "planned" || tripData.status === "confirmed") {
          selectTrip(tripData.id);
        }

        try {
          const wx = await getTripWeather(tripData.id);
          if (isMounted) setWeather(wx);
        } catch {
          // ignore optional weather fallback
        }

        try {
          const packs = await getPackingItems(tripData.id);
          if (isMounted) setPackingList(packs);
        } catch {
          // ignore optional packing fallback
        }
      } catch (err) {
        if (!isMounted) return;
        setStatus("error");
        const msg = err.message || "Failed to load saved trip.";
        setErrorMessage(msg);
        toastError(msg);
      }
    }

    loadSavedTrip();
    return () => {
      isMounted = false;
    };
  }, [tripIdParam, isAuthenticated, toastError, selectTrip]);

  // Escape key listener for swap modal
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === "Escape" && swapModalItem) {
        handleCloseSwapModal();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [swapModalItem]);

  function handleInputChange(e) {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : type === "number" ? Number(value) : value,
    }));
  }

  function togglePreference(tag) {
    setFormData((prev) => {
      const exists = prev.preferences.includes(tag);
      return {
        ...prev,
        preferences: exists ? prev.preferences.filter((t) => t !== tag) : [...prev.preferences, tag],
      };
    });
  }

  async function handlePlanSubmit(e) {
    e.preventDefault();
    if (!formData.destination_id) {
      toastError("Please choose a destination to plan your journey.");
      return;
    }
    setStatus("loading");
    setErrorMessage("");
    setGeneratedPlan(null);
    setIsConfirmed(false);

    try {
      if (isAuthenticated) {
        const createPayload = {
          destination_id: Number(formData.destination_id),
          starting_location: formData.starting_location,
          start_date: formData.start_date,
          end_date: formData.end_date,
          total_budget: Number(formData.total_budget),
          traveller_count: Number(formData.traveller_count),
          preferences: formData.preferences,
          use_ai: formData.use_ai,
        };
        const tripRes = await createTrip(createPayload);
        setCreatedTripId(tripRes.id);

        const planRes = await generateTripPlan(
          tripRes.id,
          formData.preferences,
          formData.use_ai
        );
        setGeneratedPlan(planRes);

        try {
          const wx = await getTripWeather(tripRes.id);
          setWeather(wx);
        } catch {
          setWeather(null);
        }

        try {
          const packs = await getPackingItems(tripRes.id);
          setPackingList(packs);
        } catch {
          setPackingList([]);
        }

        success("Itinerary generated. Review your schedule and confirm below.");
      } else {
        // Guest mode preview
        const selectedDest = destinations.find((d) => d.id === Number(formData.destination_id));
        const city = selectedDest?.city || "Selected Destination";
        const start = new Date(formData.start_date);
        const end = new Date(formData.end_date);
        const dayDiff = Math.max(1, Math.round((end - start) / (1000 * 60 * 60 * 24)) + 1);

        const mockDays = [];
        for (let i = 1; i <= dayDiff; i++) {
          const dDate = new Date(start);
          dDate.setDate(dDate.getDate() + (i - 1));
          mockDays.push({
            day_number: i,
            date: dDate.toISOString().split("T")[0],
            items: [
              {
                time: "09:30",
                title: `${city} Morning Cultural Exploration`,
                category: "attractions",
                estimated_cost: 450,
                notes: `Guided exploration of heritage sights and historic districts in ${city}.`,
              },
              {
                time: "13:00",
                title: "Traditional Lunch & Culinary Experience",
                category: "food",
                estimated_cost: 650,
                notes: "Authentic regional lunch featuring local specialties.",
              },
              {
                time: "16:00",
                title: `${city} Afternoon Landmark Tour`,
                category: "attractions",
                estimated_cost: 300,
                notes: "Afternoon walking route through architectural landmarks.",
              },
              {
                time: "19:30",
                title: "Evening Dining & Relaxation",
                category: "food",
                estimated_cost: 900,
                notes: "Evening culinary experience with local ambiance.",
              },
            ],
          });
        }

        const estDaily = (450 + 650 + 300 + 900) * Number(formData.traveller_count);
        const estTotal = estDaily * dayDiff + 2500 * (dayDiff - 1);
        const budgetTotal = Number(formData.total_budget);

        setGeneratedPlan({
          itinerary: {
            destination_city: city,
            summary: `${dayDiff}-Day Curated Journey in ${city}`,
            provider: formData.use_ai ? "RoamGenie AI" : "engine-v2",
            days: mockDays,
          },
          budget_summary: {
            total_budget: budgetTotal,
            estimated_total: estTotal,
            remaining_budget: Math.max(0, budgetTotal - estTotal),
            deficit_amount: Math.max(0, estTotal - budgetTotal),
            is_over_budget: estTotal > budgetTotal,
            category_breakdown: [
              { category: "accommodation", actual: 2500 * (dayDiff - 1), allocated: 2500 * (dayDiff - 1) },
              { category: "food", actual: 1550 * dayDiff * Number(formData.traveller_count), allocated: 1550 * dayDiff * Number(formData.traveller_count) },
              { category: "attractions", actual: 750 * dayDiff * Number(formData.traveller_count), allocated: 750 * dayDiff * Number(formData.traveller_count) },
            ],
          },
          warnings: estTotal > budgetTotal ? [`Estimated expenses exceed budget by ₹${(estTotal - budgetTotal).toLocaleString()}`] : [],
        });

        info("Preview generated. Sign in to save and confirm your journey.");
      }

      setStatus("success");
      setSelectedDay(1);
    } catch (err) {
      setStatus("error");
      const msg = err.message || "Failed to generate itinerary.";
      setErrorMessage(msg);
      toastError(msg);
    }
  }

  async function handleConfirmTrip() {
    if (!createdTripId) {
      toastError("Please log in to confirm and persist your trip.");
      return;
    }
    setIsConfirming(true);
    try {
      await updateTrip(createdTripId, { status: "planned" });
      setIsConfirmed(true);
      selectTrip(createdTripId);
      success("Trip confirmed! RoamGenie AI is now connected to this journey.");
    } catch (err) {
      console.error(err);
      toastError("Failed to confirm trip: " + err.message);
    } finally {
      setIsConfirming(false);
    }
  }

  async function handleToggleSave() {
    if (!createdTripId) return;
    try {
      const res = await toggleSaveTrip(createdTripId);
      setIsSaved(res.is_saved);
      if (res.is_saved) {
        success("Trip saved to bookmarks.");
      } else {
        info("Trip removed from bookmarks.");
      }
    } catch (err) {
      toastError("Failed to bookmark trip: " + err.message);
    }
  }

  async function handleTogglePacking(item) {
    try {
      const updated = await togglePackingItem(item.id, !item.is_packed);
      setPackingList((prev) => prev.map((i) => (i.id === item.id ? updated : i)));
    } catch (err) {
      toastError("Failed to update packing checklist: " + err.message);
    }
  }

  async function handleAddPackItem(e) {
    e.preventDefault();
    if (!newPackItem.trim() || !createdTripId) return;
    try {
      const added = await addPackingItem(createdTripId, newPackItem.trim());
      setPackingList((prev) => [...prev, added]);
      setNewPackItem("");
      success(`Added "${added.item}" to checklist.`);
    } catch (err) {
      toastError("Failed to add item: " + err.message);
    }
  }

  async function handleDeletePackItem(itemId) {
    try {
      await deletePackingItem(itemId);
      setPackingList((prev) => prev.filter((i) => i.id !== itemId));
    } catch (err) {
      toastError("Failed to delete item: " + err.message);
    }
  }

  async function handleOpenSwapModal(item) {
    setSwapModalItem(item);
    setSwapError("");
    setSwapAlternatives([]);

    const cat = (item.category || "").toLowerCase();
    let entityCategory = "attraction";
    if (cat.includes("hotel") || cat.includes("stay") || cat.includes("accommodation")) {
      entityCategory = "hotel";
    } else if (cat.includes("restaurant") || cat.includes("food") || cat.includes("dining")) {
      entityCategory = "restaurant";
    } else if (cat.includes("transit") || cat.includes("transport")) {
      entityCategory = "transport";
    }
    setSwapCategory(entityCategory);

    setSwapLoading(true);
    try {
      const destId = formData.destination_id;
      let alts = [];
      if (entityCategory === "hotel") {
        alts = await getHotels(destId);
      } else if (entityCategory === "restaurant") {
        alts = await getRestaurants(destId);
      } else if (entityCategory === "transport") {
        alts = await getTransportOptions(destId);
      } else {
        alts = await getAttractions(destId);
      }
      setSwapAlternatives(alts || []);
    } catch (err) {
      setSwapError(err.message || "Failed to load alternative catalogue items.");
    } finally {
      setSwapLoading(false);
    }
  }

  async function handleConfirmSwap(alt) {
    if (!swapModalItem) return;
    setSwapLoading(true);
    try {
      const isPersistedItem = Boolean(swapModalItem.id && createdTripId);
      if (isPersistedItem) {
        const updatedTrip = await swapItineraryItem(createdTripId, swapModalItem.id, {
          replacement_type: swapCategory,
          replacement_id: alt.id,
        });
        const activeItinerary = updatedTrip?.itineraries?.[0];
        if (activeItinerary) {
          setGeneratedPlan((prev) => ({
            ...prev,
            itinerary: activeItinerary,
            budget_summary: updatedTrip.budget_summary || prev.budget_summary,
          }));
        }
      } else {
        // In-memory swap update
        const newTitle = alt.name || alt.provider || swapModalItem.title;
        let newCost = swapModalItem.estimated_cost;
        let newNotes = swapModalItem.notes;
        if (swapCategory === "hotel") {
          newCost = Number(alt.price_per_night || newCost);
          newNotes = alt.address ? `Stay at ${alt.name} (${alt.address})` : newNotes;
        } else if (swapCategory === "restaurant") {
          newCost = Number(alt.average_cost_per_person || newCost);
          newNotes = `Dining at ${alt.name}, featuring ${alt.cuisine || "local"} cuisine.`;
        } else if (swapCategory === "transport") {
          newCost = Number(alt.estimated_cost || newCost);
          newNotes = `Transit from ${alt.origin} via ${(alt.mode || "train").toUpperCase()}.`;
        } else {
          newCost = Number(alt.entry_fee ?? newCost);
          newNotes = `Visit ${alt.name} (${alt.category || "attraction"}).`;
        }

        const updatedDays = (generatedPlan?.itinerary?.days || []).map((day) => {
          const updatedItems = (day.items || []).map((itm) => {
            if (itm === swapModalItem || itm.id === swapModalItem.id) {
              return {
                ...itm,
                title: newTitle,
                estimated_cost: newCost,
                notes: newNotes,
              };
            }
            return itm;
          });
          return { ...day, items: updatedItems };
        });

        setGeneratedPlan((prev) => ({
          ...prev,
          itinerary: { ...prev.itinerary, days: updatedDays },
        }));
      }

      success(`Replaced with ${alt.name || alt.provider || "selected option"}.`);
      setSwapModalItem(null);
    } catch (err) {
      setSwapError(err.message || "Failed to replace catalogue item.");
    } finally {
      setSwapLoading(false);
    }
  }

  function handleCloseSwapModal() {
    setSwapModalItem(null);
    setSwapError("");
    setSwapAlternatives([]);
  }

  const itin = generatedPlan?.itinerary;
  const budget = generatedPlan?.budget_summary;
  const daysList = itin?.days || [];
  const currentDayData = daysList.find((d) => d.day_number === selectedDay) || daysList[0];

  const matchingDestinations = destinations.filter((d) => {
    if (!destSearchText.trim()) return true;
    const q = destSearchText.toLowerCase().trim();
    return (
      (d.city && d.city.toLowerCase().includes(q)) ||
      (d.country && d.country.toLowerCase().includes(q))
    );
  });

  return (
    <div className="planner-editorial-page">
      {/* Editorial Page Header */}
      <header className="editorial-page-header">
        <p className="editorial-eyebrow">PLAN YOUR JOURNEY</p>
        <h1 className="editorial-page-title">Plan Your Optimized Journey</h1>
        <p className="editorial-page-subtitle">
          Build a trip around the places, pace, and experiences you actually want.
        </p>
      </header>

      {/* Refined Thin Line Progress Indicator */}
      <nav className="planner-editorial-nav" aria-label="Trip planning steps">
        <div className="editorial-step-chain">
          <div className={`chain-step ${formData.destination_id ? "completed" : "active"}`}>
            <span className="chain-num">01</span>
            <span className="chain-title">DESTINATION</span>
          </div>
          <span className="chain-divider">—</span>
          <div className={`chain-step ${formData.start_date && formData.end_date ? "completed" : "active"}`}>
            <span className="chain-num">02</span>
            <span className="chain-title">DATES & TRAVELLERS</span>
          </div>
          <span className="chain-divider">—</span>
          <div className={`chain-step ${formData.total_budget > 0 ? "completed" : "active"}`}>
            <span className="chain-num">03</span>
            <span className="chain-title">BUDGET</span>
          </div>
          <span className="chain-divider">—</span>
          <div className={`chain-step ${formData.preferences.length > 0 ? "completed" : "active"}`}>
            <span className="chain-num">04</span>
            <span className="chain-title">STYLE</span>
          </div>
          <span className="chain-divider">—</span>
          <div className={`chain-step ${generatedPlan ? "completed" : status === "loading" ? "active" : ""}`}>
            <span className="chain-num">05</span>
            <span className="chain-title">REVIEW</span>
          </div>
          <span className="chain-divider">—</span>
          <div className={`chain-step ${isConfirmed ? "completed" : generatedPlan ? "active" : ""}`}>
            <span className="chain-num">06</span>
            <span className="chain-title">CONFIRM</span>
          </div>
        </div>
      </nav>

      {/* Main Editorial Planner Composition */}
      <div className="planner-editorial-layout">
        {/* Left Column: Calm Journey Configuration */}
        <section className="planner-inputs-column" aria-label="Trip Parameters Form">
          <div className="inputs-column-header">
            <span className="inputs-eyebrow">STAGE 01 — 04</span>
            <h2 className="inputs-section-title">Trip Parameters</h2>
            <p className="inputs-section-sub">Define the essentials of where and how you want to travel.</p>
          </div>

          <form onSubmit={handlePlanSubmit} className="editorial-form">
            {/* Stage 01: Destination Discovery */}
            <div className="editorial-field-block">
              <label htmlFor="destination_input" className="field-label-editorial">
                Where are you going?
              </label>
              <div className="dest-discovery-wrap" ref={destDropdownRef}>
                <div className="dest-input-shell">
                  <span className="dest-input-icon" aria-hidden="true">
                    <IconSearch size={16} />
                  </span>
                  <input
                    id="destination_input"
                    name="destination_input"
                    type="text"
                    className="editorial-line-input"
                    placeholder="Search destination city or country..."
                    value={destSearchText}
                    onFocus={() => setShowDestDropdown(true)}
                    onChange={(e) => {
                      const text = e.target.value;
                      setDestSearchText(text);
                      setShowDestDropdown(true);
                      if (text.trim()) {
                        const q = text.toLowerCase().trim();
                        const match = destinations.find(
                          (d) =>
                            (d.city && d.city.toLowerCase().includes(q)) ||
                            (d.country && d.country.toLowerCase().includes(q))
                        );
                        if (match) {
                          setFormData((prev) => ({ ...prev, destination_id: match.id }));
                        }
                      }
                    }}
                    disabled={status === "loading"}
                    required
                    autoComplete="off"
                  />
                </div>

                {showDestDropdown && (
                  <ul className="dest-discovery-dropdown" role="listbox" aria-label="Destination suggestions">
                    {matchingDestinations.length > 0 ? (
                      matchingDestinations.slice(0, 30).map((d) => {
                        const isSelected = d.id === formData.destination_id;
                        return (
                          <li
                            key={d.id}
                            role="option"
                            aria-selected={isSelected}
                            className={`dest-dropdown-row ${isSelected ? "selected" : ""}`}
                            onMouseDown={(e) => {
                              e.preventDefault();
                              setFormData((prev) => ({ ...prev, destination_id: d.id }));
                              setDestSearchText(`${d.city}, ${d.country}`);
                              setShowDestDropdown(false);
                            }}
                          >
                            <div className="dropdown-row-main">
                              <span className="dropdown-city">{d.city}</span>
                              <span className="dropdown-country">, {d.country}</span>
                            </div>
                            <span className="dropdown-cost">
                              ₹{Number(d.average_daily_cost || 3500).toLocaleString()} / day
                            </span>
                          </li>
                        );
                      })
                    ) : (
                      <li className="dest-no-matches">
                        No catalogue destinations found matching &quot;{destSearchText}&quot;
                      </li>
                    )}
                  </ul>
                )}
              </div>
            </div>

            {/* Stage 02: Dates, Travellers, and Origin */}
            <div className="editorial-field-block">
              <label className="field-label-editorial">When and with whom?</label>
              <div className="dates-travellers-grid">
                <div className="grid-input-unit">
                  <span className="input-sublabel">DEPARTURE</span>
                  <input
                    id="start_date"
                    name="start_date"
                    type="date"
                    className="editorial-date-input"
                    required
                    value={formData.start_date}
                    onChange={handleInputChange}
                    disabled={status === "loading"}
                  />
                </div>

                <div className="grid-input-unit">
                  <span className="input-sublabel">RETURN</span>
                  <input
                    id="end_date"
                    name="end_date"
                    type="date"
                    className="editorial-date-input"
                    min={formData.start_date}
                    required
                    value={formData.end_date}
                    onChange={handleInputChange}
                    disabled={status === "loading"}
                  />
                </div>

                <div className="grid-input-unit">
                  <span className="input-sublabel">TRAVELLERS</span>
                  <input
                    id="traveller_count"
                    name="traveller_count"
                    type="number"
                    min="1"
                    max="50"
                    className="editorial-number-input"
                    required
                    value={formData.traveller_count}
                    onChange={handleInputChange}
                    disabled={status === "loading"}
                  />
                </div>

                <div className="grid-input-unit">
                  <span className="input-sublabel">ORIGIN</span>
                  <input
                    id="starting_location"
                    name="starting_location"
                    type="text"
                    className="editorial-text-input"
                    required
                    value={formData.starting_location}
                    onChange={handleInputChange}
                    placeholder="Starting point"
                    disabled={status === "loading"}
                  />
                </div>
              </div>
            </div>

            {/* Stage 03: Budget Display & Slider */}
            <div className="editorial-field-block">
              <div className="budget-header-row">
                <label htmlFor="total_budget" className="field-label-editorial">
                  Your trip budget
                </label>
                <span className="budget-large-display">
                  ₹{Number(formData.total_budget || 0).toLocaleString()}
                </span>
              </div>
              <input
                id="total_budget"
                name="total_budget"
                type="range"
                min="5000"
                max="500000"
                step="2500"
                className="editorial-range-slider"
                value={formData.total_budget}
                onChange={handleInputChange}
                disabled={status === "loading"}
              />
              <div className="slider-limits">
                <span>₹5,000</span>
                <span>₹5,00,000</span>
              </div>
            </div>

            {/* Stage 04: Travel Style & Preferences */}
            <div className="editorial-field-block">
              <label className="field-label-editorial">Travel style & pace</label>
              <div className="editorial-preference-list">
                {PREFERENCE_TAGS.map((tag) => {
                  const isSelected = formData.preferences.includes(tag);
                  return (
                    <button
                      key={tag}
                      type="button"
                      className={`preference-text-link ${isSelected ? "selected" : ""}`}
                      onClick={() => togglePreference(tag)}
                      disabled={status === "loading"}
                    >
                      {tag}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* AI Optimization Option */}
            <div className="editorial-ai-toggle">
              <label className="toggle-label-editorial">
                <input
                  type="checkbox"
                  name="use_ai"
                  checked={formData.use_ai}
                  onChange={handleInputChange}
                  disabled={status === "loading"}
                />
                <span>Enable RoamGenie AI weather and pacing intelligence</span>
              </label>
            </div>

            {/* Submit Action */}
            <div className="form-submit-block">
              <button
                type="submit"
                className="editorial-action-btn submit-btn"
                disabled={status === "loading"}
              >
                {status === "loading" ? "Scheduling & Persisting..." : "Generate Optimized Itinerary →"}
              </button>
            </div>
          </form>

          {status === "error" && (
            <div className="editorial-error-box" role="alert">
              <p>{errorMessage}</p>
            </div>
          )}

          {!isAuthenticated && (
            <div className="editorial-notice-box">
              <p>
                <strong>Guest Mode:</strong> You are viewing an in-memory preview.{" "}
                <Link to="/login" className="editorial-link">Log in</Link> to save itineraries to your PostgreSQL account.
              </p>
            </div>
          )}
        </section>

        {/* Right Column: Editorial Itinerary & Results */}
        <section className="planner-results-column" aria-label="Planner Results and Itinerary">
          {status === "idle" && (
            <div className="results-idle-state">
              <div className="idle-inner">
                <span className="idle-compass" aria-hidden="true">
                  <IconCompass size={28} />
                </span>
                <h3>Your journey will take shape here</h3>
                <p>
                  Set your destination, dates, and budget on the left to generate an itemized day-by-day itinerary.
                </p>
              </div>
            </div>
          )}

          {status === "loading" && (
            <div className="results-loading-state">
              <div className="editorial-spinner" />
              <h3>Calculating optimal schedule...</h3>
              <p>Relational engine is matching catalogue activities against your date range and budget limits.</p>
            </div>
          )}

          {status === "success" && generatedPlan && (
            <div className="editorial-itinerary-stream">
              {/* Itinerary Header */}
              <div className="itinerary-editorial-header">
                <div>
                  <span className="itinerary-eyebrow">
                    {itin.destination_city ? itin.destination_city.toUpperCase() : "JOURNEY"} · {daysList.length} DAYS
                  </span>
                  <h2 className="itinerary-headline">{itin.summary || `${daysList.length}-Day Curated Journey`}</h2>
                  <p className="itinerary-meta">
                    {formData.start_date} to {formData.end_date} · {formData.traveller_count} travellers
                  </p>
                </div>

                <div className="itinerary-header-buttons">
                  {isAuthenticated && createdTripId && (
                    <button
                      type="button"
                      className={`editorial-quiet-btn ${isSaved ? "saved-active" : ""}`}
                      onClick={handleToggleSave}
                      aria-label={isSaved ? "Remove bookmark" : "Bookmark this journey"}
                    >
                      {isSaved ? "Bookmarked" : "Save Bookmark"}
                    </button>
                  )}
                  <button
                    type="button"
                    className="editorial-ai-btn"
                    onClick={() => selectTrip(createdTripId)}
                    aria-label="Open RoamGenie AI chat drawer"
                  >
                    <IconSparkles size={14} /> RoamGenie AI
                  </button>
                </div>
              </div>

              {/* Stage 06 Confirmation Card */}
              <div className={`confirmation-editorial-panel ${isConfirmed ? "confirmed" : "pending"}`}>
                <div className="confirmation-panel-left">
                  <span className="confirmation-eyebrow">
                    {isConfirmed ? "STAGE 06 — TRIP CONNECTED" : "STAGE 06 — FINAL CONFIRMATION"}
                  </span>
                  <h3 className="confirmation-panel-title">
                    {isConfirmed ? "Journey confirmed & connected to RoamGenie AI" : "Ready to make this journey official?"}
                  </h3>
                  <p className="confirmation-panel-sub">
                    {isConfirmed
                      ? "RoamGenie AI is now personalized around this destination, dates, budget allocations, and scheduled activities."
                      : "Confirming this trip locks in your itinerary, enables budget tracking, and connects RoamGenie AI."}
                  </p>
                </div>
                <div className="confirmation-panel-action">
                  {!isConfirmed ? (
                    <button
                      type="button"
                      className="editorial-action-btn"
                      onClick={handleConfirmTrip}
                      disabled={isConfirming}
                    >
                      {isConfirming ? "Confirming..." : "Confirm Trip & Connect AI"}
                    </button>
                  ) : (
                    <span className="confirmed-pill">
                      <IconCheck size={14} /> Confirmed
                    </span>
                  )}
                </div>
              </div>

              {/* Budget Health Line & Categorical Splits */}
              {budget && (
                <div className="budget-editorial-line">
                  <div className="budget-figures-row">
                    <div>
                      <span className="figure-label">TOTAL BUDGET</span>
                      <strong className="figure-val">₹{Number(budget.total_budget).toLocaleString()}</strong>
                    </div>
                    <div>
                      <span className="figure-label">ESTIMATED EXPENSES</span>
                      <strong className="figure-val">₹{Number(budget.estimated_total).toLocaleString()}</strong>
                    </div>
                    <div>
                      <span className="figure-label">STATUS</span>
                      {budget.is_over_budget ? (
                        <span className="figure-val text-deficit">
                          ₹{Number(budget.deficit_amount).toLocaleString()} deficit
                        </span>
                      ) : (
                        <span className="figure-val text-aligned">
                          ₹{Number(budget.remaining_budget).toLocaleString()} remaining
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="budget-thin-bar">
                    <div
                      className={`budget-thin-fill ${budget.is_over_budget ? "fill-deficit" : "fill-aligned"}`}
                      style={{
                        width: `${Math.min(100, (budget.estimated_total / budget.total_budget) * 100)}%`,
                      }}
                    />
                  </div>

                  {budget.category_breakdown && (
                    <div className="budget-categories-row">
                      {budget.category_breakdown.map((cat) => (
                        <span key={cat.category} className="cat-breakdown-item">
                          <span className="cat-key">{cat.category}:</span>
                          <span className="cat-cost">₹{Number(cat.actual || cat.allocated).toLocaleString()}</span>
                        </span>
                      ))}
                    </div>
                  )}

                  {generatedPlan.warnings && generatedPlan.warnings.length > 0 && (
                    <div className="budget-warnings-editorial">
                      {generatedPlan.warnings.map((w, idx) => (
                        <p key={idx} className="warning-line">{w}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Weather Forecast Widget */}
              {weather && (
                <div className="weather-editorial-bar">
                  <span className="weather-bar-icon" aria-hidden="true">
                    <IconSun size={18} />
                  </span>
                  <div className="weather-bar-text">
                    <strong>{weather.city} Weather Context</strong>
                    <span>{weather.current_summary} · ~{Number(weather.temperature_c || 28)}°C</span>
                  </div>
                </div>
              )}

              {/* Day Tabs */}
              <div className="day-selection-chain" role="tablist">
                {daysList.map((d) => (
                  <button
                    key={d.day_number}
                    role="tab"
                    aria-selected={selectedDay === d.day_number}
                    className={`day-chain-btn ${selectedDay === d.day_number ? "active" : ""}`}
                    onClick={() => setSelectedDay(d.day_number)}
                  >
                    Day {d.day_number < 10 ? `0${d.day_number}` : d.day_number}
                  </button>
                ))}
              </div>

              {/* Day Timeline View */}
              <div className="day-editorial-timeline">
                <div className="timeline-day-header">
                  <h3>Day {selectedDay < 10 ? `0${selectedDay}` : selectedDay} Itinerary</h3>
                  {currentDayData?.date && <span className="timeline-day-date">{currentDayData.date}</span>}
                </div>

                {currentDayData && currentDayData.items && currentDayData.items.length > 0 ? (
                  <div className="timeline-events-list">
                    {currentDayData.items.map((item, idx) => (
                      <div key={idx} className="editorial-timeline-event">
                        <div className="event-time-col">
                          <span className="event-time">{item.start_time || item.time || "09:00"}</span>
                          <span className="event-period">{formatDayPart(item.start_time || item.time)}</span>
                        </div>

                        <div className="event-timeline-line" />

                        <div className="event-content-col">
                          <div className="event-primary-line">
                            <h4 className="event-title">{item.title}</h4>
                            <span className="event-cost-tag">₹{Number(item.estimated_cost).toLocaleString()}</span>
                          </div>
                          {item.notes && <p className="event-description">{item.notes}</p>}
                          <div className="event-meta-line">
                            <span className="event-category-label">{item.category}</span>
                            <button
                              type="button"
                              className="event-swap-link"
                              onClick={() => handleOpenSwapModal(item)}
                              aria-label={`Swap ${item.title}`}
                            >
                              <IconRefresh size={12} /> Replace activity
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="empty-day-notice">No activities recorded for this day.</p>
                )}
              </div>

              {/* Packing Checklist */}
              <div className="packing-editorial-section">
                <div className="packing-header">
                  <div className="packing-header-title">
                    <IconSuitcase size={16} />
                    <h3>Trip Packing Checklist</h3>
                  </div>
                  <span className="packing-count">
                    {packingList.filter((i) => i.is_packed).length} of {packingList.length} packed
                  </span>
                </div>

                <div className="packing-items-stream">
                  {packingList.map((item) => (
                    <div key={item.id} className="packing-row-item">
                      <label className={`pack-checkbox-label ${item.is_packed ? "checked" : ""}`}>
                        <input
                          type="checkbox"
                          checked={item.is_packed}
                          onChange={() => handleTogglePacking(item)}
                          aria-label={`Mark ${item.item} as ${item.is_packed ? "unpacked" : "packed"}`}
                        />
                        <span className="pack-item-name">{item.item}</span>
                      </label>
                      <button
                        type="button"
                        className="pack-remove-btn"
                        onClick={() => handleDeletePackItem(item.id)}
                        aria-label={`Remove ${item.item}`}
                      >
                        <IconClose size={13} />
                      </button>
                    </div>
                  ))}
                </div>

                {createdTripId && (
                  <form className="add-packing-form-editorial" onSubmit={handleAddPackItem}>
                    <input
                      type="text"
                      className="add-pack-input"
                      placeholder="Add custom packing essential..."
                      value={newPackItem}
                      onChange={(e) => setNewPackItem(e.target.value)}
                    />
                    <button type="submit" className="add-pack-btn" disabled={!newPackItem.trim()}>
                      Add Item
                    </button>
                  </form>
                )}
              </div>
            </div>
          )}
        </section>
      </div>

      {/* Catalogue Item Swap Modal */}
      {swapModalItem && (
        <div className="editorial-modal-backdrop" onClick={handleCloseSwapModal}>
          <div
            className="editorial-modal-window"
            role="dialog"
            aria-modal="true"
            aria-label="Select Catalogue Replacement"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="editorial-modal-header">
              <div>
                <p className="modal-eyebrow">CATALOGUE REPLACEMENT</p>
                <h3 className="modal-city-title">Swapping: {swapModalItem.title}</h3>
              </div>
              <button
                type="button"
                className="modal-close-btn"
                onClick={handleCloseSwapModal}
                aria-label="Close swap modal"
              >
                <IconClose size={20} />
              </button>
            </div>

            <div className="editorial-modal-body">
              {swapLoading ? (
                <div className="editorial-loading-state">
                  <div className="editorial-spinner" />
                  <p>Searching destination catalogue...</p>
                </div>
              ) : swapError ? (
                <div className="editorial-error-box" role="alert">
                  <p>{swapError}</p>
                </div>
              ) : swapAlternatives.length === 0 ? (
                <p className="empty-notice">No alternative catalogue items found for this category and destination.</p>
              ) : (
                <div className="editorial-catalogue-list">
                  {swapAlternatives.map((alt) => {
                    let costText = "";
                    let detailText = "";
                    if (swapCategory === "hotel") {
                      costText = `₹${Number(alt.price_per_night).toLocaleString()} / night`;
                      detailText = alt.rating ? `Rating: ${alt.rating}/5.0` : "Accommodations";
                    } else if (swapCategory === "restaurant") {
                      costText = `~₹${Number(alt.average_cost_per_person || 250).toLocaleString()} / person`;
                      detailText = `Cuisine: ${alt.cuisine || "Regional"}`;
                    } else if (swapCategory === "transport") {
                      costText = `₹${Number(alt.estimated_cost).toLocaleString()} / person`;
                      detailText = `Origin: ${alt.origin} · ${(alt.mode || "transit").toUpperCase()}`;
                    } else {
                      costText = Number(alt.entry_fee) === 0 ? "Complimentary entry" : `₹${Number(alt.entry_fee).toLocaleString()} entry`;
                      detailText = `Category: ${alt.category || "Sight"}`;
                    }

                    return (
                      <div key={alt.id} className="editorial-catalogue-row">
                        <div className="catalogue-row-main">
                          <strong className="row-item-name">{alt.name || alt.provider || `${alt.origin} Transit`}</strong>
                          <p className="catalogue-row-sub">{detailText}</p>
                        </div>
                        <div className="catalogue-row-meta">
                          <span className="cost-num">{costText}</span>
                          <button
                            type="button"
                            className="editorial-action-btn btn-sm"
                            onClick={() => handleConfirmSwap(alt)}
                            disabled={swapLoading}
                            aria-label={`Select ${alt.name || alt.provider || "item"} as replacement`}
                          >
                            {swapLoading ? "Replacing..." : "Select & Swap"}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="editorial-modal-footer">
              <button
                type="button"
                className="editorial-quiet-btn"
                onClick={handleCloseSwapModal}
                disabled={swapLoading}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
