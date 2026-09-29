import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { useCopilot } from "../context/CopilotContext";
import {
  addPackingItem,
  chatAssistant,
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

const PREFERENCE_TAGS = [
  "heritage",
  "culinary",
  "photography",
  "nature",
  "palaces",
  "temples",
  "adventure",
  "shopping",
  "relaxed",
];

function getSuggestedStartDate() {
  const d = new Date();
  d.setDate(d.getDate() + 7);
  return d.toISOString().split("T")[0];
}

function getSuggestedEndDate() {
  const d = new Date();
  d.setDate(d.getDate() + 11);
  return d.toISOString().split("T")[0];
}

export default function PlanPage() {
  const { search } = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { success, error: toastError, info, warning } = useToast();
  const { openCopilot, selectTrip, refreshUserTrips } = useCopilot();

  const queryParams = new URLSearchParams(search);
  const initialDestId = queryParams.get("destinationId");
  const tripIdParam = queryParams.get("tripId");

  const [destinations, setDestinations] = useState([]);
  const [formData, setFormData] = useState({
    destination_id: initialDestId ? Number(initialDestId) : "",
    starting_location: "Delhi",
    start_date: getSuggestedStartDate(),
    end_date: getSuggestedEndDate(),
    traveller_count: 2,
    total_budget: 35000,
    preferences: ["heritage", "culinary"],
    use_ai: false,
  });

  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [errorMessage, setErrorMessage] = useState("");
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [createdTripId, setCreatedTripId] = useState(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);

  // Weather & Packing state
  const [weather, setWeather] = useState(null);
  const [packingList, setPackingList] = useState([]);
  const [newPackItem, setNewPackItem] = useState("");

  // Active day in timeline
  const [selectedDay, setSelectedDay] = useState(1);

  // M4 Catalogue Swap Modal state
  const [swapModalItem, setSwapModalItem] = useState(null);
  const [swapCategory, setSwapCategory] = useState("attraction");
  const [swapAlternatives, setSwapAlternatives] = useState([]);
  const [swapLoading, setSwapLoading] = useState(false);
  const [swapError, setSwapError] = useState("");

  // Destination Autocomplete Search & Dropdown state
  const [destSearchText, setDestSearchText] = useState("");
  const [showDestDropdown, setShowDestDropdown] = useState(false);
  const destDropdownRef = useRef(null);

  useEffect(() => {
    async function loadDests() {
      try {
        const dests = await getDestinations("", true, 500);
        setDestinations(dests);
        if (initialDestId && dests.length > 0) {
          const matched = dests.find((d) => d.id === Number(initialDestId));
          if (matched) {
            setDestSearchText(`${matched.city}, ${matched.country} (₹${Number(matched.average_daily_cost || 3500).toLocaleString()}/day)`);
          }
        }
      } catch (err) {
        console.error("Failed to load destinations", err);
      }
    }
    loadDests();
  }, [initialDestId]);

  // Sync displayed search text when destination_id changes and dropdown is closed
  useEffect(() => {
    if (formData.destination_id && destinations.length > 0 && !showDestDropdown) {
      const selected = destinations.find((d) => d.id === formData.destination_id);
      if (selected) {
        setDestSearchText(`${selected.city}, ${selected.country} (₹${Number(selected.average_daily_cost || 3500).toLocaleString()}/day)`);
      }
    }
  }, [formData.destination_id, destinations, showDestDropdown]);

  // Dismiss dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (destDropdownRef.current && !destDropdownRef.current.contains(e.target)) {
        setShowDestDropdown(false);
        // Restore selected destination label if input was left partially typed
        if (formData.destination_id && destinations.length > 0) {
          const selected = destinations.find((d) => d.id === formData.destination_id);
          if (selected) {
            setDestSearchText(`${selected.city}, ${selected.country} (₹${Number(selected.average_daily_cost || 3500).toLocaleString()}/day)`);
          }
        }
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [formData.destination_id, destinations]);

  // Hydrate saved trip if tripId is provided in URL
  useEffect(() => {
    if (!tripIdParam) return;
    if (!isAuthenticated) return;

    let isMounted = true;
    async function loadSavedTrip() {
      setStatus("loading");
      setErrorMessage("");
      try {
        const tripData = await getTrip(Number(tripIdParam));
        if (!isMounted) return;

        setCreatedTripId(tripData.id);
        setIsSaved(Boolean(tripData.is_saved));
        setIsConfirmed(tripData.status === "planned" || tripData.status === "confirmed");
        setPackingList(tripData.packing_items || []);

        setFormData((prev) => ({
          ...prev,
          destination_id: tripData.destination_id || prev.destination_id,
          starting_location: tripData.starting_location || prev.starting_location,
          start_date: tripData.start_date || prev.start_date,
          end_date: tripData.end_date || prev.end_date,
          traveller_count: tripData.traveller_count || prev.traveller_count,
          total_budget: Number(tripData.total_budget) || prev.total_budget,
        }));

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

        selectTrip(tripData.id);

        try {
          const wx = await getTripWeather(tripData.id);
          if (isMounted) setWeather(wx);
        } catch (wxErr) {
          console.warn("Weather fetch fallback on reload:", wxErr);
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

  // Escape key listener for dialogs
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
      const next = exists ? prev.preferences.filter((t) => t !== tag) : [...prev.preferences, tag];
      return { ...prev, preferences: next };
    });
  }

  async function handleConfirmTrip() {
    if (!createdTripId) return;
    try {
      await updateTrip(createdTripId, { status: "planned" });
      setIsConfirmed(true);
      selectTrip(createdTripId);
      refreshUserTrips();
      success("Trip confirmed! RoamGenie AI is now personalized with your destination itinerary.");
    } catch (err) {
      toastError(err.message || "Failed to confirm trip.");
    }
  }

  async function handlePlanSubmit(e) {
    e.preventDefault();
    setShowDestDropdown(false);

    let destId = formData.destination_id;
    if (!destId && matchingDestinations.length > 0) {
      destId = matchingDestinations[0].id;
      setFormData((prev) => ({ ...prev, destination_id: destId }));
    }

    if (!destId) {
      toastError("Please select a valid destination from the suggestions.");
      return;
    }

    setStatus("loading");
    setErrorMessage("");

    try {
      if (isAuthenticated) {
        // Authenticated flow: Create trip in DB + Generate and Persist multi-table plan
        const tripPayload = {
          destination_id: Number(destId),
          starting_location: formData.starting_location,
          start_date: formData.start_date,
          end_date: formData.end_date,
          traveller_count: Number(formData.traveller_count),
          total_budget: Number(formData.total_budget),
        };

        const createdTrip = await createTrip(tripPayload);
        setCreatedTripId(createdTrip.id);
        setIsConfirmed(false);

        const planResult = await generateTripPlan(
          createdTrip.id,
          formData.preferences,
          formData.use_ai
        );

        setGeneratedPlan(planResult);
        success("Itinerary generated! Review your plan and click 'Confirm & Activate Trip' to connect with RoamGenie AI.");

        // Load weather & packing items
        try {
          const wx = await getTripWeather(createdTrip.id);
          setWeather(wx);
        } catch (wxErr) {
          console.warn("Weather fetch fallback:", wxErr);
        }

        try {
          const packs = await getPackingItems(createdTrip.id);
          setPackingList(packs);
        } catch (pkErr) {
          console.warn("Packing fetch fallback:", pkErr);
        }
      } else {
        // Unauthenticated preview flow
        const selectedDestObj = destinations.find((d) => d.id === Number(formData.destination_id));
        const previewRes = await previewPlan({
          destination_id: Number(formData.destination_id) || undefined,
          starting_location: formData.starting_location,
          destination: selectedDestObj ? selectedDestObj.city : "Jaipur",
          start_date: formData.start_date,
          end_date: formData.end_date,
          travellers: formData.traveller_count,
          total_budget: formData.total_budget,
          preferences: formData.preferences,
        });

        // Shape into common structure with real catalogue data
        const categoryBreakdown = (previewRes.budget_split || []).map((cat) => ({
          category: cat.category,
          allocated: cat.amount,
          actual: cat.amount,
        }));

        setGeneratedPlan({
          itinerary: {
            ...previewRes,
            destination_city: selectedDestObj ? selectedDestObj.city : "Destination",
          },
          budget_summary: {
            total_budget: formData.total_budget,
            estimated_total: previewRes.estimated_total,
            remaining_budget: previewRes.remaining_budget,
            is_over_budget: Number(previewRes.estimated_total) > Number(formData.total_budget),
            deficit_amount: Math.max(0, Number(previewRes.estimated_total) - Number(formData.total_budget)),
            category_breakdown: categoryBreakdown,
          },
          warnings: previewRes.warnings || [],
        });

        if (previewRes.packing_items) {
          setPackingList(
            previewRes.packing_items.map((item, idx) => ({
              id: idx + 1,
              item: item,
              is_packed: false,
            }))
          );
        }
        info("In-memory preview generated. Log in to persist.");
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

  async function handleToggleSave() {
    if (!createdTripId) return;
    try {
      const res = await toggleSaveTrip(createdTripId);
      setIsSaved(res.is_saved);
      if (res.is_saved) {
        success("Trip bookmarked to saved trips!");
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
      console.error(err);
      toastError("Failed to update checklist: " + err.message);
    }
  }

  async function handleAddPackItem(e) {
    e.preventDefault();
    if (!newPackItem.trim() || !createdTripId) return;
    try {
      const added = await addPackingItem(createdTripId, newPackItem.trim());
      setPackingList((prev) => [...prev, added]);
      setNewPackItem("");
      success(`Added "${added.item}" to packing checklist.`);
    } catch (err) {
      console.error(err);
      toastError("Failed to add packing item: " + err.message);
    }
  }

  async function handleDeletePackItem(itemId) {
    try {
      await deletePackingItem(itemId);
      setPackingList((prev) => prev.filter((i) => i.id !== itemId));
      info("Item removed from packing checklist.");
    } catch (err) {
      console.error(err);
      toastError("Failed to delete packing item: " + err.message);
    }
  }

  async function handleOpenSwapModal(item) {
    const rawCat = (item.category || "").toLowerCase().trim();
    let normCat = "attraction";
    if (rawCat.includes("hotel") || rawCat.includes("stay") || rawCat.includes("accommodation") || rawCat.includes("lodging")) {
      normCat = "hotel";
    } else if (rawCat.includes("food") || rawCat.includes("dining") || rawCat.includes("restaurant") || rawCat.includes("meal")) {
      normCat = "restaurant";
    } else if (rawCat.includes("transport") || rawCat.includes("transit")) {
      normCat = "transport";
    } else {
      normCat = "attraction";
    }

    setSwapModalItem({ ...item, normalizedCategory: normCat });
    setSwapCategory(normCat);
    setSwapError("");
    setSwapLoading(true);
    setSwapAlternatives([]);

    try {
      const destId = formData.destination_id;
      let alts = [];
      if (normCat === "hotel") {
        alts = await getHotels(destId);
      } else if (normCat === "restaurant") {
        alts = await getRestaurants(destId);
      } else if (normCat === "transport") {
        alts = await getTransportOptions(destId);
      } else {
        alts = await getAttractions(destId);
      }
      setSwapAlternatives(alts || []);
    } catch (err) {
      console.error("Failed to load alternatives:", err);
      const msg = err.message || "Failed to load catalogue alternatives.";
      setSwapError(msg);
      toastError(msg);
    } finally {
      setSwapLoading(false);
    }
  }

  async function handleConfirmSwap(alt) {
    if (!swapModalItem || swapLoading) return;
    setSwapLoading(true);
    setSwapError("");

    try {
      if (isAuthenticated && createdTripId && swapModalItem.id) {
        // Authenticated persisted trip: Call PATCH API
        const updatedTrip = await swapItineraryItem(createdTripId, swapModalItem.id, {
          replacement_type: swapCategory,
          replacement_id: alt.id,
        });

        const activeItinerary = updatedTrip.itineraries?.[0] || null;
        if (activeItinerary) {
          const categoryBreakdown = (updatedTrip.budget_summary?.categories || updatedTrip.budget_allocations || []).map((c) => ({
            category: c.category,
            actual: Number(c.amount),
            allocated: Number(c.amount),
          }));

          const budgetSummary = updatedTrip.budget_summary
            ? {
                ...updatedTrip.budget_summary,
                is_over_budget:
                  updatedTrip.budget_summary.status === "over_budget" ||
                  Number(updatedTrip.estimated_total) > Number(updatedTrip.total_budget),
                deficit_amount: Number(updatedTrip.budget_summary.deficit || 0),
                remaining_budget: Number(updatedTrip.budget_summary.remaining_budget || 0),
                category_breakdown: categoryBreakdown,
              }
            : null;

          setGeneratedPlan({
            itinerary: {
              ...activeItinerary,
              destination_city: updatedTrip.destination_city,
            },
            budget_summary: budgetSummary,
            warnings: updatedTrip.budget_summary?.warnings || [],
          });
        }
      } else {
        // In-memory guest preview swap: Update local state & recalculate budget math
        let newTitle = "";
        let newCost = 0;
        let newCategory = swapCategory;
        let newNotes = "";

        if (swapCategory === "hotel") {
          newTitle = `Overnight Stay at ${alt.name}`;
          newCost = Number(alt.price_per_night || 0);
          newCategory = "accommodation";
          newNotes = `Rating: ${alt.rating || 4.0}/5.0 · Tariff: ₹${alt.price_per_night}/night`;
        } else if (swapCategory === "restaurant") {
          newTitle = `Dining at ${alt.name}`;
          newCost = Number(alt.average_cost_per_person || 250) * formData.traveller_count;
          newCategory = "food";
          newNotes = `Cuisine: ${alt.cuisine || "Regional"} · Rating: ${alt.rating || 4.0}/5.0`;
        } else if (swapCategory === "transport") {
          newTitle = `Transit from ${alt.origin} to Destination (${(alt.mode || "transit").toUpperCase()})`;
          newCost = Number(alt.estimated_cost || 0) * formData.traveller_count;
          newCategory = "transportation";
          newNotes = `Provider: ${alt.provider || "Direct"} | Duration: ${alt.duration_minutes || 120} mins`;
        } else {
          newTitle = `Visit ${alt.name}`;
          newCost = Number(alt.entry_fee || 0) * formData.traveller_count;
          newCategory = "attraction";
          newNotes = `Category: ${alt.category || "Sight"} · Rating: ${alt.rating || 4.5}/5.0`;
        }

        const updatedDays = (generatedPlan?.itinerary?.days || []).map((day) => {
          const updatedItems = (day.items || []).map((itm) => {
            const isMatch = (swapModalItem.id && itm.id === swapModalItem.id) || itm.title === swapModalItem.title;
            if (isMatch) {
              return {
                ...itm,
                title: newTitle,
                category: newCategory,
                estimated_cost: newCost,
                notes: newNotes,
              };
            }
            return itm;
          });
          return { ...day, items: updatedItems };
        });

        // Recalculate category totals
        const catTotals = { accommodation: 0, transportation: 0, food: 0, attractions: 0 };
        updatedDays.forEach((d) => {
          (d.items || []).forEach((itm) => {
            const cat = (itm.category || "").toLowerCase();
            if (cat.includes("hotel") || cat.includes("accommodation") || cat.includes("stay")) {
              catTotals.accommodation += Number(itm.estimated_cost || 0);
            } else if (cat.includes("food") || cat.includes("dining") || cat.includes("restaurant")) {
              catTotals.food += Number(itm.estimated_cost || 0);
            } else if (cat.includes("transport") || cat.includes("transit")) {
              catTotals.transportation += Number(itm.estimated_cost || 0);
            } else {
              catTotals.attractions += Number(itm.estimated_cost || 0);
            }
          });
        });

        const totalEst = Object.values(catTotals).reduce((a, b) => a + b, 0);
        const totalBudget = Number(formData.total_budget || 0);
        const deficit = Math.max(0, totalEst - totalBudget);
        const remaining = Math.max(0, totalBudget - totalEst);

        const categoryBreakdown = Object.entries(catTotals).map(([k, v]) => ({
          category: k,
          actual: v,
          allocated: v,
        }));

        setGeneratedPlan((prev) => ({
          ...prev,
          itinerary: {
            ...prev.itinerary,
            days: updatedDays,
          },
          budget_summary: {
            total_budget: totalBudget,
            estimated_total: totalEst,
            remaining_budget: remaining,
            deficit_amount: deficit,
            is_over_budget: deficit > 0,
            status: deficit > 0 ? "over_budget" : "within_budget",
            category_breakdown: categoryBreakdown,
          },
        }));
      }

      const altName = alt.name || alt.provider || "Selected item";
      success(`Swapped to ${altName} · Budget updated!`);
      setSwapModalItem(null);
    } catch (err) {
      console.error("Failed to swap item:", err);
      const msg = err.message || "Failed to replace item.";
      setSwapError(msg);
      toastError(msg);
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
    <div className="planner-page">
      <div className="page-header">
        <p className="eyebrow">Interactive Trip Engine</p>
        <h1>Plan Your Optimized Journey</h1>
        <p>Define your travel constraints, dates, and budget. Our relational engine schedules catalogue activities, computes itemized budgets, and detects deficits.</p>
      </div>

      {/* 6-Stage Guided Planning Progress Bar */}
      <div className="planner-stages-bar" role="navigation" aria-label="Trip planning steps">
        <div className={`stage-step ${formData.destination_id ? "completed" : "active"}`}>
          <span className="stage-num">01</span>
          <span className="stage-text">Destination</span>
        </div>
        <div className="stage-connector" />
        <div className={`stage-step ${formData.start_date && formData.end_date ? "completed" : "active"}`}>
          <span className="stage-num">02</span>
          <span className="stage-text">Dates</span>
        </div>
        <div className="stage-connector" />
        <div className={`stage-step ${formData.total_budget > 0 ? "completed" : "active"}`}>
          <span className="stage-num">03</span>
          <span className="stage-text">Budget</span>
        </div>
        <div className="stage-connector" />
        <div className={`stage-step ${formData.preferences.length > 0 ? "completed" : "active"}`}>
          <span className="stage-num">04</span>
          <span className="stage-text">Preferences</span>
        </div>
        <div className="stage-connector" />
        <div className={`stage-step ${generatedPlan ? "completed" : status === "loading" ? "active" : ""}`}>
          <span className="stage-num">05</span>
          <span className="stage-text">Review</span>
        </div>
        <div className="stage-connector" />
        <div className={`stage-step ${isConfirmed ? "completed" : generatedPlan ? "active" : ""}`}>
          <span className="stage-num">06</span>
          <span className="stage-text">Confirm</span>
        </div>
      </div>

      <div className="planner-layout">
        {/* Left Column: Multi-Step Input Wizard */}
        <section className="planner-form-card" aria-label="Trip Parameters Form">
          <div className="form-card-header">
            <h2>Trip Parameters</h2>
            <span className="card-subtitle">Fill stages 01–04 to generate your day-wise itinerary</span>
          </div>
          <form onSubmit={handlePlanSubmit}>
            <div className="form-group">
              <label htmlFor="destination_input">
                <span className="stage-badge">01</span> Select Destination
              </label>
              <div className="dest-autocomplete-container" ref={destDropdownRef}>
                <input
                  id="destination_input"
                  name="destination_input"
                  type="text"
                  className="dest-autocomplete-input"
                  placeholder="🔍 Type city or country (e.g. Shimla, Jaipur, Tokyo)..."
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
                {showDestDropdown && (
                  <ul className="dest-dropdown-menu" role="listbox" aria-label="Destination suggestions">
                    {matchingDestinations.length > 0 ? (
                      matchingDestinations.slice(0, 50).map((d) => {
                        const isSelected = d.id === formData.destination_id;
                        return (
                          <li
                            key={d.id}
                            role="option"
                            aria-selected={isSelected}
                            className={`dest-dropdown-item ${isSelected ? "selected" : ""}`}
                            onMouseDown={(e) => {
                              e.preventDefault();
                              setFormData((prev) => ({ ...prev, destination_id: d.id }));
                              setDestSearchText(`${d.city}, ${d.country} (₹${Number(d.average_daily_cost || 3500).toLocaleString()}/day)`);
                              setShowDestDropdown(false);
                            }}
                          >
                            <div>
                              <span className="dest-dropdown-item-city">{d.city}</span>
                              <span className="dest-dropdown-item-country">, {d.country}</span>
                            </div>
                            <span className="dest-dropdown-item-cost">
                              ₹{Number(d.average_daily_cost || 3500).toLocaleString()}/day
                            </span>
                          </li>
                        );
                      })
                    ) : (
                      <li className="dest-no-matches">
                        No destinations found matching "{destSearchText}"
                      </li>
                    )}
                  </ul>
                )}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="starting_location">
                <span className="stage-badge">02</span> Starting Location
              </label>
              <input
                id="starting_location"
                name="starting_location"
                type="text"
                required
                value={formData.starting_location}
                onChange={handleInputChange}
                placeholder="e.g. Delhi, Mumbai, Bangalore"
                disabled={status === "loading"}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="start_date">Start Date</label>
                <input
                  id="start_date"
                  name="start_date"
                  type="date"
                  required
                  value={formData.start_date}
                  onChange={handleInputChange}
                  disabled={status === "loading"}
                />
              </div>

              <div className="form-group">
                <label htmlFor="end_date">End Date</label>
                <input
                  id="end_date"
                  name="end_date"
                  type="date"
                  min={formData.start_date}
                  required
                  value={formData.end_date}
                  onChange={handleInputChange}
                  disabled={status === "loading"}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="traveller_count">Travellers</label>
                <input
                  id="traveller_count"
                  name="traveller_count"
                  type="number"
                  min="1"
                  max="50"
                  required
                  value={formData.traveller_count}
                  onChange={handleInputChange}
                  disabled={status === "loading"}
                />
              </div>

              <div className="form-group">
                <label htmlFor="total_budget">
                  <span className="stage-badge">03</span> Total Budget (₹ INR)
                </label>
                <input
                  id="total_budget"
                  name="total_budget"
                  type="number"
                  min="1000"
                  step="500"
                  required
                  value={formData.total_budget}
                  onChange={handleInputChange}
                  disabled={status === "loading"}
                />
              </div>
            </div>

            <div className="form-group">
              <label>
                <span className="stage-badge">04</span> Travel Preferences & Activity Tags
              </label>
              <div className="tag-cloud">
                {PREFERENCE_TAGS.map((tag) => (
                  <button
                    key={tag}
                    type="button"
                    className={`tag-btn ${formData.preferences.includes(tag) ? "selected" : ""}`}
                    onClick={() => togglePreference(tag)}
                    disabled={status === "loading"}
                  >
                    {formData.preferences.includes(tag) ? "✓ " : "+ "}
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="use_ai"
                  checked={formData.use_ai}
                  onChange={handleInputChange}
                  disabled={status === "loading"}
                />
                <span>Enable AI Travel Assistant (Weather & Pacing Intelligence)</span>
              </label>
            </div>

            <button type="submit" className="button button-primary button-full" disabled={status === "loading"}>
              {status === "loading" ? "Scheduling & Persisting..." : "Generate Optimized Itinerary →"}
            </button>
          </form>

          {status === "error" && (
            <div className="error-banner" role="alert">
              <p>⚠️ {errorMessage}</p>
            </div>
          )}

          {!isAuthenticated && (
            <div className="auth-notice">
              <p>💡 <strong>Guest Mode:</strong> You are viewing an in-memory preview. <a href="/login">Log in</a> to save itineraries to your PostgreSQL account.</p>
            </div>
          )}
        </section>

        {/* Right Column: Generated Plan & Budget Visualizer */}
        <section className="planner-results" aria-label="Planner Results and Itinerary">
          {status === "idle" && (
            <div className="empty-results-card">
              <div className="placeholder-icon">🗺️</div>
              <h3>Your Itinerary Awaits</h3>
              <p>Adjust trip constraints on the left and click "Generate" to construct your day-wise schedule and budget breakdown.</p>
            </div>
          )}

          {status === "loading" && (
            <div className="hydrating-card">
              <div className="spinner"></div>
              <h3>{tripIdParam ? "Loading Saved Itinerary..." : "Optimizing Itinerary & Budget..."}</h3>
              <p>
                {tripIdParam
                  ? "Hydrating persisted trip details, itinerary activities, and budget allocations from PostgreSQL."
                  : "Executing relational joins, scheduling activities, and checking budget constraints."}
              </p>
            </div>
          )}

          {status === "success" && generatedPlan && (
            <div className="results-wrapper">
              {/* Trip Header & Actions */}
              <div className="itinerary-header-card">
                <div>
                  <span className="dest-badge">📍 {itin.destination_city || "Trip Itinerary"}</span>
                  <h2>{itin.summary || "Generated Multi-Day Itinerary"}</h2>
                  <p className="meta-text">
                    {formData.start_date} to {formData.end_date} · {formData.traveller_count} Travellers · Provider: {itin.provider || "engine-v2"}
                  </p>
                </div>

                <div className="header-actions">
                  {isAuthenticated && createdTripId && (
                    <button
                      type="button"
                      className={`button ${isSaved ? "button-saved" : "button-outline"}`}
                      onClick={handleToggleSave}
                      aria-label={isSaved ? "Remove from bookmarks" : "Bookmark this trip"}
                    >
                      {isSaved ? "★ Bookmarked" : "☆ Save to Bookmarks"}
                    </button>
                  )}
                  {isAuthenticated && createdTripId && (
                    <button
                      type="button"
                      className={`button ${isConfirmed ? "button-confirmed" : "button-primary"}`}
                      onClick={handleConfirmTrip}
                      disabled={isConfirmed}
                    >
                      {isConfirmed ? "✓ Trip Confirmed" : "✓ Confirm Trip"}
                    </button>
                  )}
                  <button
                    type="button"
                    className="button button-secondary"
                    onClick={() => openCopilot(createdTripId)}
                    aria-label="Open RoamGenie AI chat drawer"
                  >
                    ✨ Ask RoamGenie AI
                  </button>
                </div>
              </div>

              {/* Stage 06 Confirmation Card */}
              {isAuthenticated && createdTripId && (
                <div className={`trip-activation-banner ${isConfirmed ? "is-activated" : "is-pending"}`}>
                  <div className="activation-info">
                    <span className="stage-pill">
                      {isConfirmed ? "Stage 06: ✓ Confirmed & Connected" : "Stage 06: Ready to Confirm"}
                    </span>
                    <h3>
                      {isConfirmed
                        ? "Trip Confirmed & Connected to RoamGenie AI"
                        : "Confirm this itinerary to activate RoamGenie AI context"}
                    </h3>
                    <p>
                      {isConfirmed
                        ? `RoamGenie AI is now personalized with your ${itin.destination_city || "destination"} dates, budget, and daily activities.`
                        : "Review your generated schedule and budget below. When you're satisfied, confirm the trip to connect RoamGenie AI."}
                    </p>
                  </div>
                  <div className="activation-actions">
                    {!isConfirmed ? (
                      <button
                        type="button"
                        className="button button-primary"
                        onClick={handleConfirmTrip}
                      >
                        ✓ Confirm & Activate Trip
                      </button>
                    ) : (
                      <button
                        type="button"
                        className="button button-primary"
                        onClick={() => openCopilot(createdTripId)}
                      >
                        ✨ Chat with RoamGenie AI →
                      </button>
                    )}
                  </div>
                </div>
              )}

              {/* Budget Health Bar & Alert */}
              {budget && (
                <div className={`budget-visualizer-card ${budget.is_over_budget ? "alert-deficit" : "alert-ok"}`}>
                  <div className="budget-summary-header">
                    <div>
                      <span className="label">Total Budget: <strong>₹{Number(budget.total_budget).toLocaleString()}</strong></span>
                      <span className="label">Estimated Costs: <strong>₹{Number(budget.estimated_total).toLocaleString()}</strong></span>
                    </div>
                    <div className="budget-status-pill">
                      {budget.is_over_budget ? (
                        <span className="badge danger">⚠️ Budget Deficit: ₹{Number(budget.deficit_amount).toLocaleString()}</span>
                      ) : (
                        <span className="badge success">✓ Under Budget: ₹{Number(budget.remaining_budget).toLocaleString()} remaining</span>
                      )}
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="budget-progress-container">
                    <div
                      className={`budget-progress-bar ${budget.is_over_budget ? "bar-danger" : "bar-success"}`}
                      style={{
                        width: `${Math.min(100, (budget.estimated_total / budget.total_budget) * 100)}%`,
                      }}
                    ></div>
                  </div>

                  {/* Category Breakdown */}
                  {budget.category_breakdown && (
                    <div className="category-splits">
                      {budget.category_breakdown.map((cat) => (
                        <div key={cat.category} className="cat-pill">
                          <span className="cat-name">{cat.category}</span>
                          <span className="cat-val">₹{Number(cat.actual || cat.allocated).toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {generatedPlan.warnings && generatedPlan.warnings.length > 0 && (
                    <div className="budget-warnings">
                      {generatedPlan.warnings.map((w, idx) => (
                        <p key={idx} className="warning-text">ℹ️ {w}</p>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Weather Snapshot Widget */}
              {weather && (
                <div className="weather-card">
                  <div className="weather-header">
                    <span className="weather-icon">🌤️</span>
                    <div>
                      <strong>{weather.city} Forecast</strong>
                      <p>{weather.current_summary} · ~{Number(weather.temperature_c || 28)}°C</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Day-by-Day Timeline Container */}
              <div className="timeline-container">
                <div className="day-tabs" role="tablist">
                  {daysList.map((d) => (
                    <button
                      key={d.day_number}
                      role="tab"
                      aria-selected={selectedDay === d.day_number}
                      className={`day-tab-btn ${selectedDay === d.day_number ? "active" : ""}`}
                      onClick={() => setSelectedDay(d.day_number)}
                    >
                      Day {d.day_number}
                    </button>
                  ))}
                </div>

                <div className="timeline-day-view">
                  <h3>Day {selectedDay} Schedule</h3>
                  {currentDayData && currentDayData.items && currentDayData.items.length > 0 ? (
                    <div className="activity-timeline">
                      {currentDayData.items.map((item, idx) => (
                        <div key={idx} className="timeline-event">
                          <div className="time-badge">{item.start_time || item.time || "09:00"}</div>
                          <div className="event-details">
                            <div className="event-title-row">
                              <strong>{item.title}</strong>
                              <span className="event-cat">{item.category}</span>
                            </div>
                            {item.notes && <p className="event-notes">{item.notes}</p>}
                            <div className="event-footer-row">
                              <span className="event-cost">₹{Number(item.estimated_cost).toLocaleString()}</span>
                              <button
                                type="button"
                                className="swap-btn"
                                onClick={() => handleOpenSwapModal(item)}
                                aria-label={`Swap ${item.title}`}
                              >
                                ⇄ Swap
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="empty-day-notice">No activities scheduled for this day.</p>
                  )}
                </div>
              </div>

              {/* Dynamic Packing Checklist */}
              <div className="packing-card">
                <h3>🧳 Trip Packing Checklist</h3>
                {packingList.length === 0 ? (
                  <p className="empty-pack-notice">Your checklist is empty. Add essential travel items below.</p>
                ) : (
                  <div className="packing-items-grid">
                    {packingList.map((item) => (
                      <div key={item.id} className="packing-item-row">
                        <label className={`pack-label ${item.is_packed ? "packed" : ""}`}>
                          <input
                            type="checkbox"
                            checked={item.is_packed}
                            onChange={() => handleTogglePacking(item)}
                            aria-label={`Mark ${item.item} as ${item.is_packed ? "unpacked" : "packed"}`}
                          />
                          <span>{item.item}</span>
                        </label>
                        <button
                          type="button"
                          className="delete-item-btn"
                          onClick={() => handleDeletePackItem(item.id)}
                          aria-label={`Remove ${item.item}`}
                          title="Remove item"
                        >
                          ✕
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {createdTripId && (
                  <form className="add-pack-form" onSubmit={handleAddPackItem}>
                    <input
                      type="text"
                      placeholder="Add custom packing item..."
                      value={newPackItem}
                      onChange={(e) => setNewPackItem(e.target.value)}
                    />
                    <button type="submit" disabled={!newPackItem.trim()}>Add Item</button>
                  </form>
                )}
              </div>
            </div>
          )}
        </section>
      </div>

      {/* M4 Catalogue Item Swap Modal */}
      {swapModalItem && (
        <div className="modal-backdrop" onClick={handleCloseSwapModal}>
          <div
            className="modal-content"
            role="dialog"
            aria-modal="true"
            aria-label="Select Catalogue Replacement"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <h3>Select Catalogue Replacement</h3>
                <p className="meta-text">
                  Swapping: <strong>{swapModalItem.title}</strong> ({swapCategory})
                </p>
              </div>
              <button
                type="button"
                className="close-btn"
                onClick={handleCloseSwapModal}
                aria-label="Close swap modal"
              >
                ✕
              </button>
            </div>

            <div className="modal-body">
              {swapLoading ? (
                <div className="state-loading">
                  <div className="spinner"></div>
                  <p>Loading destination catalogue options...</p>
                </div>
              ) : swapError ? (
                <div className="state-error" role="alert">
                  <p>⚠️ {swapError}</p>
                </div>
              ) : swapAlternatives.length === 0 ? (
                <p className="empty-alts-notice">No alternative catalogue entities found for this category and destination.</p>
              ) : (
                <div className="catalogue-list">
                  {swapAlternatives.map((alt) => {
                    let costText = "";
                    let detailText = "";
                    if (swapCategory === "hotel") {
                      costText = `₹${Number(alt.price_per_night).toLocaleString()} / night`;
                      detailText = alt.rating ? `Rating: ${alt.rating}/5.0` : "Verified Hotel";
                    } else if (swapCategory === "restaurant") {
                      costText = `₹${Number(alt.average_cost_per_person || 250).toLocaleString()} / person`;
                      detailText = `Cuisine: ${alt.cuisine || "Regional"} ${alt.rating ? `· Rating: ${alt.rating}/5.0` : ""}`;
                    } else if (swapCategory === "transport") {
                      costText = `₹${Number(alt.estimated_cost).toLocaleString()} / person`;
                      detailText = `Origin: ${alt.origin} · Mode: ${(alt.mode || "transit").toUpperCase()}`;
                    } else {
                      costText = Number(alt.entry_fee) === 0 ? "Free Entry" : `₹${Number(alt.entry_fee).toLocaleString()} entry`;
                      detailText = `Category: ${alt.category || "Sight"} ${alt.rating ? `· Rating: ${alt.rating}/5.0` : ""}`;
                    }

                    return (
                      <div key={alt.id} className="catalogue-item">
                        <div className="item-title">
                          <strong>{alt.name || alt.provider || `${alt.origin} Transit`}</strong>
                          <button
                            type="button"
                            className="alt-select-btn"
                            onClick={() => handleConfirmSwap(alt)}
                            disabled={swapLoading}
                            aria-label={`Select ${alt.name || alt.provider || "item"} as replacement`}
                          >
                            {swapLoading ? "Swapping..." : "Select & Swap"}
                          </button>
                        </div>
                        <p className="item-detail">{detailText}</p>
                        <div className="item-footer">
                          <span>{costText}</span>
                          {alt.rating && <span className="rating-badge">★ {alt.rating}</span>}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="button button-outline"
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
