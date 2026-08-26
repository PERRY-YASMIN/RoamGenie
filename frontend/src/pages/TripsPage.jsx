import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { deleteTrip, listSavedTrips, listTrips } from "../services/api";

export default function TripsPage() {
  const { isAuthenticated } = useAuth();
  const { success, error: toastError, info } = useToast();
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
    if (!window.confirm("Are you sure you want to delete this trip and its itinerary?")) return;
    setDeletingId(tripId);
    try {
      await deleteTrip(tripId);
      setTrips((prev) => prev.filter((t) => t.id !== tripId));
      setSavedTrips((prev) => prev.filter((s) => s.trip_id !== tripId));
      success("Trip deleted successfully.");
    } catch (err) {
      toastError("Failed to delete trip: " + err.message);
    } finally {
      setDeletingId(null);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="trips-page-container">
        <div className="panel auth-prompt-panel" role="region" aria-label="Authentication Required">
          <p className="eyebrow">Authentication Required</p>
          <h1>Access Your Travel History</h1>
          <p>Please log in or create an account to view your saved itineraries and planned trips stored in PostgreSQL.</p>
          <div className="actions">
            <Link className="button button-primary" to="/login">Log In →</Link>
            <Link className="button button-secondary" to="/register">Create Account</Link>
          </div>
        </div>
      </div>
    );
  }

  const displayedTrips = activeTab === "all" ? trips : savedTrips.map((s) => s.trip).filter(Boolean);

  return (
    <div className="trips-page-container">
      <div className="page-header">
        <p className="eyebrow">User History & Persistence Dashboard</p>
        <h1>My Travel Journeys</h1>
        <p>Review your saved multi-day itineraries, check spending health, and reopen planned vacations.</p>

        <div className="trip-tabs" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === "all"}
            className={`tab-btn ${activeTab === "all" ? "active" : ""}`}
            onClick={() => setActiveTab("all")}
          >
            All Planned Trips ({trips.length})
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "saved"}
            className={`tab-btn ${activeTab === "saved" ? "active" : ""}`}
            onClick={() => setActiveTab("saved")}
          >
            ★ Bookmarks & Saved ({savedTrips.length})
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Loading trips from database...</p>
        </div>
      ) : error ? (
        <div className="error-banner" role="alert">
          <p>⚠️ {error}</p>
          <button type="button" onClick={loadData}>Retry</button>
        </div>
      ) : displayedTrips.length === 0 ? (
        <div className="empty-trips-card">
          <div className="placeholder-icon">✈️</div>
          <h3>No Trips Found</h3>
          <p>
            {activeTab === "all"
              ? "You haven't created any trips yet. Set a destination, dates, and budget to generate your first itinerary."
              : "You haven't bookmarked any trips yet. Bookmark a trip from the itinerary planner to easily find it here."}
          </p>
          {activeTab === "saved" && trips.length > 0 ? (
            <button
              type="button"
              className="button button-outline"
              onClick={() => setActiveTab("all")}
            >
              View All Planned Trips ({trips.length}) →
            </button>
          ) : (
            <Link className="button button-primary" to="/plan">Plan a New Trip →</Link>
          )}
        </div>
      ) : (
        <div className="trips-grid">
          {displayedTrips.map((trip) => {
            const isDeficit = Number(trip.estimated_total) > Number(trip.total_budget);
            const isDeleting = deletingId === trip.id;
            return (
              <div key={trip.id} className="trip-history-card">
                <div className="card-top">
                  <div>
                    <span className="dest-tag">📍 {trip.destination_city || "Destination"}</span>
                    <h2>{trip.destination_city || `Trip #${trip.id}`}</h2>
                  </div>
                  <span className={`status-pill ${trip.status}`}>{trip.status}</span>
                </div>

                <div className="trip-details-grid">
                  <div className="detail-item">
                    <span className="label">Dates</span>
                    <strong>{trip.start_date} to {trip.end_date}</strong>
                  </div>
                  <div className="detail-item">
                    <span className="label">Origin</span>
                    <strong>{trip.starting_location || "N/A"}</strong>
                  </div>
                  <div className="detail-item">
                    <span className="label">Travellers</span>
                    <strong>{trip.traveller_count} Persons</strong>
                  </div>
                  <div className="detail-item">
                    <span className="label">Budget vs Estimated</span>
                    <strong>₹{Number(trip.total_budget).toLocaleString()} / <span className={isDeficit ? "text-danger" : "text-success"}>₹{Number(trip.estimated_total).toLocaleString()}</span></strong>
                  </div>
                </div>

                <div className="card-actions">
                  <Link
                    className="button button-primary button-sm"
                    to={`/plan?destinationId=${trip.destination_id}&tripId=${trip.id}`}
                    aria-label={`Open Itinerary for trip in ${trip.destination_city || trip.id}`}
                  >
                    Open Itinerary →
                  </Link>
                  <button
                    type="button"
                    className="button button-danger button-sm"
                    onClick={() => handleDeleteTrip(trip.id)}
                    disabled={isDeleting}
                    aria-label={`Delete trip in ${trip.destination_city || trip.id}`}
                  >
                    {isDeleting ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
