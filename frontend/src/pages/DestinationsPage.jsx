import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAttractions, getDestination, getDestinations, getHotels, getRestaurants } from "../services/api";
import { getAttractionImageUrl, getDestinationImageUrl, getGoogleMapsUrl } from "../utils/destinationImages";

export default function DestinationsPage() {
  const [destinations, setDestinations] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Selected destination modal state
  const [selectedDest, setSelectedDest] = useState(null);
  const [modalTab, setModalTab] = useState("hotels");
  const [modalData, setModalData] = useState({ hotels: [], restaurants: [], attractions: [] });
  const [modalLoading, setModalLoading] = useState(false);

  useEffect(() => {
    loadDestinations();
  }, []);

  // Escape key listener to close catalogue modal
  useEffect(() => {
    function handleKeyDown(e) {
      if (e.key === "Escape" && selectedDest) {
        setSelectedDest(null);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [selectedDest]);

  async function loadDestinations(query = "") {
    setLoading(true);
    setError(null);
    try {
      const data = await getDestinations(query);
      setDestinations(data);
    } catch (err) {
      setError(
        err.name === "AbortError"
          ? "The destination catalogue is taking too long to respond. Check the database connection and try again."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  function handleSearchSubmit(e) {
    e.preventDefault();
    loadDestinations(search);
  }

  async function openCatalogueModal(dest) {
    setSelectedDest(dest);
    setModalTab("hotels");
    setModalLoading(true);
    try {
      const [hotels, restaurants, attractions] = await Promise.all([
        getHotels(dest.id).catch(() => []),
        getRestaurants(dest.id).catch(() => []),
        getAttractions(dest.id).catch(() => []),
      ]);
      setModalData({ hotels, restaurants, attractions });
    } catch (err) {
      console.error(err);
    } finally {
      setModalLoading(false);
    }
  }

  return (
    <div className="destinations-container">
      <div className="page-header">
        <p className="eyebrow">Relational Catalogue Explorer</p>
        <h1>Explore Travel Destinations</h1>
        <p>Browse normalized catalogue data including hotels, local dining, attractions, and average daily expenses.</p>

        <form className="search-bar" onSubmit={handleSearchSubmit}>
          <input
            type="text"
            placeholder="Search by city (e.g., Jaipur, Kochi, Varanasi)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search destinations by city"
          />
          <button type="submit" disabled={loading}>Search</button>
          {search && (
            <button
              type="button"
              className="button-clear"
              onClick={() => {
                setSearch("");
                loadDestinations("");
              }}
              aria-label="Clear search"
            >
              Clear
            </button>
          )}
        </form>
      </div>

      {loading ? (
        <div className="loading-state" role="status" aria-live="polite">
          <div className="spinner"></div>
          <p>Loading destination catalogue from PostgreSQL...</p>
        </div>
      ) : error ? (
        <div className="error-banner" role="alert">
          <p>⚠️ {error}</p>
          <button type="button" onClick={() => loadDestinations(search)}>Retry</button>
        </div>
      ) : destinations.length === 0 ? (
        <div className="empty-state">
          <div className="placeholder-icon">📍</div>
          <h3>No Destinations Found</h3>
          <p>{search ? `No destinations found matching "${search}".` : "No destination records found in database."}</p>
          {search && (
            <button
              type="button"
              className="button button-outline"
              onClick={() => {
                setSearch("");
                loadDestinations("");
              }}
            >
              Reset Search
            </button>
          )}
        </div>
      ) : (
        <div className="destinations-grid">
          {destinations.map((dest) => (
            <div key={dest.id} className="destination-card">
              <div className="dest-card-image-wrap">
                <img
                  className="dest-card-img"
                  src={getDestinationImageUrl(dest)}
                  alt={`Scenic view of ${dest.city}, ${dest.country}`}
                  loading="lazy"
                  onError={(e) => {
                    e.target.src = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80";
                  }}
                />
                <div className="dest-card-badge-overlay">
                  <span className="dest-tag-badge">🏛️ {dest.country}</span>
                  <span className="dest-cost-badge">₹{Number(dest.average_daily_cost || 3500).toLocaleString()}/day</span>
                </div>
              </div>

              <div className="dest-card-body">
                <h2>{dest.city}</h2>
                <p className="dest-desc">{dest.description || "Historical cultural and scenic travel destination."}</p>

                <div className="dest-actions">
                  <button
                    type="button"
                    className="button button-outline button-sm"
                    onClick={() => openCatalogueModal(dest)}
                    aria-label={`View catalogue items for ${dest.city}`}
                  >
                    View Catalogue
                  </button>
                  <Link
                    className="button button-primary button-sm"
                    to={`/plan?destinationId=${dest.id}&city=${encodeURIComponent(dest.city)}`}
                    aria-label={`Plan trip to ${dest.city}`}
                  >
                    Plan Trip
                  </Link>
                </div>

                <a
                  href={getGoogleMapsUrl(dest.city, dest.country)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="dest-maps-link"
                  aria-label={`Explore ${dest.city} on Google Maps`}
                >
                  🗺️ Explore {dest.city} on Google Maps ↗
                </a>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Catalogue Details Modal */}
      {selectedDest && (
        <div className="modal-backdrop" onClick={() => setSelectedDest(null)}>
          <div
            className="modal-content"
            role="dialog"
            aria-modal="true"
            aria-label={`Catalogue Inspection for ${selectedDest.city}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <div>
                <h2>{selectedDest.city}, {selectedDest.country}</h2>
                <p className="eyebrow">Database Catalogue Inspection</p>
              </div>
              <button
                type="button"
                className="close-btn"
                onClick={() => setSelectedDest(null)}
                aria-label="Close catalogue inspection dialog"
              >
                ✕
              </button>
            </div>

            <div className="modal-tabs" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={modalTab === "hotels"}
                className={`tab-btn ${modalTab === "hotels" ? "active" : ""}`}
                onClick={() => setModalTab("hotels")}
              >
                Accommodations ({modalData.hotels.length})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={modalTab === "restaurants"}
                className={`tab-btn ${modalTab === "restaurants" ? "active" : ""}`}
                onClick={() => setModalTab("restaurants")}
              >
                Dining Venues ({modalData.restaurants.length})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={modalTab === "attractions"}
                className={`tab-btn ${modalTab === "attractions" ? "active" : ""}`}
                onClick={() => setModalTab("attractions")}
              >
                Sightseeing & Sights ({modalData.attractions.length})
              </button>
            </div>

            <div className="modal-body">
              {modalLoading ? (
                <div className="loading-state" role="status" aria-live="polite">
                  <div className="spinner"></div>
                  <p>Loading catalogue items...</p>
                </div>
              ) : modalTab === "hotels" ? (
                <div className="catalogue-list">
                  {modalData.hotels.length === 0 ? <p className="empty-notice">No hotels recorded in database.</p> : (
                    modalData.hotels.map((h) => (
                      <div key={h.id} className="catalogue-item">
                        <div className="item-title">
                          <strong>{h.name}</strong>
                          <span className="rating-badge">★ {h.rating || "4.5"}</span>
                        </div>
                        <p className="item-detail">{h.address || "Centrally located"}</p>
                        <div className="item-footer">
                          <span className="tier-tag">{h.tier}</span>
                          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
                            <span className="cost-tag">₹{Number(h.price_per_night).toLocaleString()} / night</span>
                            <a
                              href={getGoogleMapsUrl(h.name, selectedDest.city, selectedDest.country)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="item-maps-link"
                              aria-label={`Explore ${h.name} on Google Maps`}
                            >
                              🗺️ Maps ↗
                            </a>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : modalTab === "restaurants" ? (
                <div className="catalogue-list">
                  {modalData.restaurants.length === 0 ? <p className="empty-notice">No dining venues recorded.</p> : (
                    modalData.restaurants.map((r) => (
                      <div key={r.id} className="catalogue-item">
                        <div className="item-title">
                          <strong>{r.name}</strong>
                          <span className="rating-badge">★ {r.rating || "4.5"}</span>
                        </div>
                        <p className="item-detail">Cuisine: {r.cuisine}</p>
                        <div className="item-footer">
                          <span className="cost-tag">~₹{Number(r.average_cost_per_person).toLocaleString()} / person</span>
                          <a
                            href={getGoogleMapsUrl(r.name, selectedDest.city, selectedDest.country)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="item-maps-link"
                            aria-label={`Explore ${r.name} on Google Maps`}
                          >
                            🗺️ Maps ↗
                          </a>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                <div className="catalogue-list">
                  {modalData.attractions.length === 0 ? <p className="empty-notice">No attractions recorded.</p> : (
                    modalData.attractions.map((a) => (
                      <div key={a.id} className="catalogue-sight-item">
                        <div className="sight-thumbnail-wrap">
                          <img
                            className="sight-thumbnail-img"
                            src={getAttractionImageUrl(a)}
                            alt={`Photo of ${a.name}`}
                            loading="lazy"
                            onError={(e) => {
                              e.target.src = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=400&q=80";
                            }}
                          />
                        </div>
                        <div className="sight-info">
                          <div className="item-title">
                            <strong>{a.name}</strong>
                            <span className="rating-badge">★ {a.rating || "4.8"}</span>
                          </div>
                          <p className="item-detail">Category: {a.category}</p>
                          <div className="item-footer">
                            <span className="cost-tag">Entry Fee: {Number(a.entry_fee) === 0 ? "Free Entry" : `₹${Number(a.entry_fee).toLocaleString()}`}</span>
                            <a
                              href={getGoogleMapsUrl(a.name, selectedDest.city, selectedDest.country)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="item-maps-link"
                              aria-label={`Explore ${a.name} on Google Maps`}
                            >
                              🗺️ Maps ↗
                            </a>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <Link
                className="button button-primary"
                to={`/plan?destinationId=${selectedDest.id}&city=${encodeURIComponent(selectedDest.city)}`}
                onClick={() => setSelectedDest(null)}
              >
                Plan Itinerary for {selectedDest.city}
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
