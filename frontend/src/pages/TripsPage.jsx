import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { useCopilot } from "../context/CopilotContext";
import { deleteTrip, listSavedTrips, listTrips } from "../services/api";
import { getDestinationImageUrl } from "../utils/destinationImages";
import { IconArrowRight, IconSparkles, IconTrash, IconCompass } from "../components/icons";

function formatDateRange(startDate, endDate) {
  if (!startDate || !endDate) return "";
  try {
    const s = new Date(startDate);
    const e = new Date(endDate);
    const sStr = s.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    const eStr = e.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
    return `${sStr} – ${eStr}`;
  } catch {
    return `${startDate} to ${endDate}`;
  }
}

export default function TripsPage() {
  const { isAuthenticated } = useAuth();
  const { success, error: toastError } = useToast();
  const { openCopilot } = useCopilot();
  const [activeTab, setActiveTab] = useState("all"); // all | saved
  const [trips, setTrips] = useState([]);
  const [savedTrips, setSavedTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      loadData();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  async function loadData() {
    setLoading(true);
    setError(null);
    try {
      const [allList, savedList] = await Promise.all([
        listTrips().catch(() => []),
        listSavedTrips().catch(() => []),
      ]);
      setTrips(allList);
      setSavedTrips(savedList);
    } catch (err) {
      setError(err.message);
      toastError(err.message || "Failed to load trips.");
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteTrip(tripId) {
    if (!window.confirm("Are you sure you want to remove this journey entry?")) return;
    setDeletingId(tripId);
    try {
      await deleteTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
      setSavedTrips((prev) => prev.filter((s) => s.trip_id !== tripId));
      success("Journey removed from journal.");
    } catch (err) {
      toastError("Failed to delete trip: " + err.message);
    } finally {
      setDeletingId(null);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="trips-journal-page">
        <header className="editorial-page-header">
          <p className="editorial-eyebrow">TRAVEL JOURNAL</p>
          <h1 className="editorial-page-title">Access your journeys</h1>
          <p className="editorial-page-subtitle">
            Please log in or create an account to view your confirmed itineraries, spending health, and personal travel notes.
          </p>
          <div className="editorial-auth-actions">
            <Link className="editorial-action-btn" to="/login">Log In →</Link>
            <Link className="editorial-quiet-btn" to="/register">Create Account</Link>
          </div>
        </header>
      </div>
    );
  }

  const displayedTrips = activeTab === "all" ? trips : savedTrips.map((s) => s.trip).filter(Boolean);

  return (
    <div className="trips-journal-page">
      {/* Editorial Header */}
      <header className="editorial-page-header">
        <p className="editorial-eyebrow">TRAVEL JOURNAL</p>
        <h1 className="editorial-page-title">My Trips</h1>
        <p className="editorial-page-subtitle">
          A persistent record of your journeys, day-by-day itineraries, and budget allocations.
        </p>

        {/* Tab switchers */}
        <div className="journal-filter-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "all"}
            className={`journal-tab-btn ${activeTab === "all" ? "active" : ""}`}
            onClick={() => setActiveTab("all")}
          >
            All Journeys ({trips.length})
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === "saved"}
            className={`journal-tab-btn ${activeTab === "saved" ? "active" : ""}`}
            onClick={() => setActiveTab("saved")}
          >
            Saved Bookmarks ({savedTrips.length})
          </button>
        </div>
      </header>

      {/* Main Journal Stream */}
      {loading ? (
        <div className="editorial-loading-state" role="status" aria-live="polite">
          <div className="editorial-spinner" />
          <p>Retrieving travel journal...</p>
        </div>
      ) : error ? (
        <div className="editorial-error-box" role="alert">
          <p>{error}</p>
          <button type="button" className="editorial-link-btn" onClick={loadData}>
            Try again
          </button>
        </div>
      ) : displayedTrips.length === 0 ? (
        <div className="journal-empty-state">
          <div className="empty-state-compass" aria-hidden="true">
            <IconCompass size={32} />
          </div>
          <h3>Your next journey starts here.</h3>
          <p>
            {activeTab === "all"
              ? "Create a trip and RoamGenie will help you plan every step."
              : "You haven't bookmarked any journeys yet. Bookmark an itinerary from the planner to easily find it here."}
          </p>
          {activeTab === "saved" && trips.length > 0 ? (
            <button
              type="button"
              className="editorial-action-btn"
              onClick={() => setActiveTab("all")}
            >
              View All Journeys ({trips.length}) →
            </button>
          ) : (
            <Link className="editorial-action-btn" to="/plan">
              Plan a Trip →
            </Link>
          )}
        </div>
      ) : (
        <div className="journal-entries-stream">
          {displayedTrips.map((trip) => {
            const isDeficit = Number(trip.estimated_total) > Number(trip.total_budget);
            const isDeleting = deletingId === trip.id;
            const destCity = trip.destination_city || `Trip #${trip.id}`;
            const mockDest = trip.destination || { city: destCity, country: "" };
            const imgSrc = getDestinationImageUrl(mockDest);

            return (
              <article key={trip.id} className="journal-entry-row">
                <div className="journal-entry-visual">
                  <img
                    src={imgSrc}
                    alt={`Scenery for ${destCity}`}
                    loading="lazy"
                    onError={(e) => {
                      e.target.src = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=600&q=80";
                    }}
                  />
                </div>

                <div className="journal-entry-details">
                  <div className="journal-entry-top">
                    <span className="journal-entry-tag">{trip.status || "planned"}</span>
                    <span className="journal-entry-dates">{formatDateRange(trip.start_date, trip.end_date)}</span>
                  </div>

                  <h2 className="journal-entry-city">{destCity}</h2>

                  <div className="journal-entry-meta">
                    <span>{trip.traveller_count} travellers</span>
                    <span>·</span>
                    <span>Origin: {trip.starting_location || "Not specified"}</span>
                    <span>·</span>
                    <span>
                      Budget: ₹{Number(trip.total_budget).toLocaleString()} (
                      <span className={isDeficit ? "text-deficit" : "text-aligned"}>
                        {isDeficit ? `₹${(Number(trip.estimated_total) - Number(trip.total_budget)).toLocaleString()} deficit` : "on track"}
                      </span>
                      )
                    </span>
                  </div>

                  <div className="journal-entry-actions">
                    <Link
                      className="journal-link-primary"
                      to={`/plan?destinationId=${trip.destination_id}&tripId=${trip.id}`}
                      aria-label={`Open Itinerary for trip in ${destCity}`}
                    >
                      Open Itinerary <IconArrowRight size={13} />
                    </Link>
                    <button
                      type="button"
                      className="journal-link-ai"
                      onClick={() => openCopilot(trip.id)}
                      aria-label={`Ask RoamGenie AI about trip in ${destCity}`}
                    >
                      <IconSparkles size={13} /> RoamGenie AI
                    </button>
                    <button
                      type="button"
                      className="journal-link-delete"
                      onClick={() => handleDeleteTrip(trip.id)}
                      disabled={isDeleting}
                      aria-label={`Delete trip in ${destCity}`}
                    >
                      <IconTrash size={13} /> {isDeleting ? "Removing..." : "Delete"}
                    </button>
                  </div>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}
