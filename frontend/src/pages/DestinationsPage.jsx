import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAttractions, getDestinations, getHotels, getRestaurants } from "../services/api";
import { getAttractionImageUrl, getDestinationImageUrl, getGoogleMapsUrl } from "../utils/destinationImages";
import { IconSearch, IconClose, IconArrowRight, IconExternalLink, IconStar, IconCompass } from "../components/icons";

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
  const [selectedFilter, setSelectedFilter] = useState("all");

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

  const displayedDestinations = destinations.filter((dest) => {
    if (selectedFilter === "india") return dest.country?.toLowerCase().includes("india");
    if (selectedFilter === "europe") {
      const euro = ["france", "italy", "spain", "germany", "united kingdom", "greece", "switzerland", "netherlands", "austria", "portugal"];
      return euro.some((c) => dest.country?.toLowerCase().includes(c));
    }
    if (selectedFilter === "asia") {
      const asia = ["japan", "thailand", "vietnam", "indonesia", "singapore", "malaysia", "south korea", "india"];
      return asia.some((c) => dest.country?.toLowerCase().includes(c));
    }
    if (selectedFilter === "budget") return Number(dest.average_daily_cost || 0) <= 4000;
    return true;
  });

  const featuredDest = displayedDestinations.length > 0 ? displayedDestinations[0] : null;
  const remainingDests = displayedDestinations.length > 1 ? displayedDestinations.slice(1) : [];

  return (
    <div className="destinations-editorial-page">
      {/* Editorial Header */}
      <header className="editorial-page-header">
        <p className="editorial-eyebrow">DESTINATIONS</p>
        <h1 className="editorial-page-title">Find somewhere worth going.</h1>
        <p className="editorial-page-subtitle">
          An intentional catalogue of places, with accommodation options, local dining venues, and daily expense estimates.
        </p>
      </header>

      {/* Editorial Search & Filter Bar */}
      <section className="editorial-search-section" aria-label="Search and filter destinations">
        <form className="editorial-search-bar" onSubmit={handleSearchSubmit}>
          <span className="search-icon-slot" aria-hidden="true">
            <IconSearch size={18} />
          </span>
          <input
            type="text"
            className="editorial-search-input"
            placeholder="Search city or country (e.g. Kyoto, Shimla, Florence)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search destinations by city"
          />
          {search && (
            <button
              type="button"
              className="editorial-clear-btn"
              onClick={() => {
                setSearch("");
                loadDestinations("");
              }}
              aria-label="Clear search query"
            >
              <IconClose size={14} />
            </button>
          )}
          <button type="submit" className="editorial-submit-btn" disabled={loading}>
            Search
          </button>
        </form>

        <div className="editorial-filter-tabs" role="toolbar" aria-label="Filter destinations by region">
          {[
            { id: "all", label: "All Destinations" },
            { id: "india", label: "India" },
            { id: "europe", label: "Europe" },
            { id: "asia", label: "Asia" },
            { id: "budget", label: "Budget Friendly (≤ ₹4,000)" },
          ].map((f) => (
            <button
              key={f.id}
              type="button"
              className={`editorial-filter-link ${selectedFilter === f.id ? "active" : ""}`}
              onClick={() => setSelectedFilter(f.id)}
            >
              {f.label}
            </button>
          ))}
        </div>
      </section>

      {/* Main Content Area */}
      {loading ? (
        <div className="editorial-loading-state" role="status" aria-live="polite">
          <div className="editorial-spinner" />
          <p>Accessing destination catalogue...</p>
        </div>
      ) : error ? (
        <div className="editorial-error-box" role="alert">
          <p>{error}</p>
          <button type="button" className="editorial-link-btn" onClick={() => loadDestinations(search)}>
            Try again
          </button>
        </div>
      ) : displayedDestinations.length === 0 ? (
        <div className="editorial-empty-state">
          <p className="empty-title">No destinations found</p>
          <p className="empty-desc">
            {search ? `No catalogue entries match "${search}".` : "No destinations match the active filter criteria."}
          </p>
          {(search || selectedFilter !== "all") && (
            <button
              type="button"
              className="editorial-action-btn"
              onClick={() => {
                setSearch("");
                setSelectedFilter("all");
                loadDestinations("");
              }}
            >
              Reset Filters
            </button>
          )}
        </div>
      ) : (
        <div className="editorial-destinations-layout">
          {/* Featured Destination Hero Block */}
          {featuredDest && (
            <article className="featured-destination-block" aria-label={`Featured destination: ${featuredDest.city}`}>
              <div className="featured-image-frame">
                <img
                  className="featured-image"
                  src={getDestinationImageUrl(featuredDest)}
                  alt={`Scenic landscape of ${featuredDest.city}, ${featuredDest.country}`}
                  loading="eager"
                  onError={(e) => {
                    e.target.src = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1200&q=80";
                  }}
                />
              </div>

              <div className="featured-content">
                <span className="featured-eyebrow">
                  FEATURED DESTINATION · {featuredDest.country.toUpperCase()}
                </span>
                <h2 className="featured-city-title">{featuredDest.city}</h2>
                <p className="featured-description">
                  {featuredDest.description || "A storied landscape offering rich historical significance, cultural heritage, and memorable scenic routes."}
                </p>

                <div className="featured-meta-row">
                  <div className="featured-meta-item">
                    <span className="meta-label">DAILY EXPENSE</span>
                    <strong className="meta-val">₹{Number(featuredDest.average_daily_cost || 3500).toLocaleString()} <span className="meta-unit">/ day</span></strong>
                  </div>
                  <div className="featured-meta-item">
                    <span className="meta-label">REGION</span>
                    <strong className="meta-val">{featuredDest.country}</strong>
                  </div>
                </div>

                <div className="featured-action-row">
                  <Link
                    to={`/plan?destinationId=${featuredDest.id}&city=${encodeURIComponent(featuredDest.city)}`}
                    className="editorial-action-btn"
                  >
                    Plan Itinerary for {featuredDest.city} <IconArrowRight size={14} />
                  </Link>
                  <button
                    type="button"
                    className="editorial-quiet-btn"
                    onClick={() => openCatalogueModal(featuredDest)}
                  >
                    View Catalogue Details
                  </button>
                </div>
              </div>
            </article>
          )}

          {/* Section Divider */}
          {remainingDests.length > 0 && (
            <div className="editorial-grid-divider">
              <span className="divider-label">MORE DESTINATIONS</span>
              <div className="divider-line" />
            </div>
          )}

          {/* Asymmetric Editorial Grid */}
          {remainingDests.length > 0 && (
            <div className="editorial-destinations-grid">
              {remainingDests.map((dest) => (
                <article key={dest.id} className="editorial-dest-item">
                  <div className="dest-image-wrap">
                    <img
                      className="dest-image"
                      src={getDestinationImageUrl(dest)}
                      alt={`View of ${dest.city}, ${dest.country}`}
                      loading="lazy"
                      onError={(e) => {
                        e.target.src = "https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80";
                      }}
                    />
                  </div>

                  <div className="dest-item-body">
                    <div className="dest-item-header">
                      <span className="dest-item-country">{dest.country}</span>
                      <span className="dest-item-cost">₹{Number(dest.average_daily_cost || 3500).toLocaleString()}/day</span>
                    </div>

                    <h3 className="dest-item-title">{dest.city}</h3>
                    <p className="dest-item-desc">
                      {dest.description || "A considered destination for exploration and travel."}
                    </p>

                    <div className="dest-item-actions">
                      <Link
                        className="dest-plan-link"
                        to={`/plan?destinationId=${dest.id}&city=${encodeURIComponent(dest.city)}`}
                        aria-label={`Plan trip to ${dest.city}`}
                      >
                        Plan trip <IconArrowRight size={13} />
                      </Link>
                      <button
                        type="button"
                        className="dest-details-link"
                        onClick={() => openCatalogueModal(dest)}
                        aria-label={`Inspect catalogue for ${dest.city}`}
                      >
                        Catalogue
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Catalogue Inspection Modal */}
      {selectedDest && (
        <div className="editorial-modal-backdrop" onClick={() => setSelectedDest(null)}>
          <div
            className="editorial-modal-window"
            role="dialog"
            aria-modal="true"
            aria-label={`Catalogue Inspection for ${selectedDest.city}`}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="editorial-modal-header">
              <div>
                <p className="modal-eyebrow">DATABASE CATALOGUE</p>
                <h2 className="modal-city-title">{selectedDest.city}, {selectedDest.country}</h2>
              </div>
              <button
                type="button"
                className="modal-close-btn"
                onClick={() => setSelectedDest(null)}
                aria-label="Close catalogue inspection dialog"
              >
                <IconClose size={20} />
              </button>
            </div>

            <div className="editorial-modal-tabs" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={modalTab === "hotels"}
                className={`editorial-tab-btn ${modalTab === "hotels" ? "active" : ""}`}
                onClick={() => setModalTab("hotels")}
              >
                Accommodations ({modalData.hotels.length})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={modalTab === "restaurants"}
                className={`editorial-tab-btn ${modalTab === "restaurants" ? "active" : ""}`}
                onClick={() => setModalTab("restaurants")}
              >
                Dining ({modalData.restaurants.length})
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={modalTab === "attractions"}
                className={`editorial-tab-btn ${modalTab === "attractions" ? "active" : ""}`}
                onClick={() => setModalTab("attractions")}
              >
                Sights & Culture ({modalData.attractions.length})
              </button>
            </div>

            <div className="editorial-modal-body">
              {modalLoading ? (
                <div className="editorial-loading-state" role="status" aria-live="polite">
                  <div className="editorial-spinner" />
                  <p>Retrieving database records...</p>
                </div>
              ) : modalTab === "hotels" ? (
                <div className="editorial-catalogue-list">
                  {modalData.hotels.length === 0 ? (
                    <p className="empty-notice">No accommodations recorded in database.</p>
                  ) : (
                    modalData.hotels.map((h) => (
                      <div key={h.id} className="editorial-catalogue-row">
                        <div className="catalogue-row-main">
                          <div className="catalogue-row-title">
                            <strong>{h.name}</strong>
                            <span className="rating-pill">
                              <IconStar size={12} /> {h.rating || "4.5"}
                            </span>
                          </div>
                          <p className="catalogue-row-sub">{h.address || "Centrally located"} · {h.tier || "Standard"}</p>
                        </div>
                        <div className="catalogue-row-meta">
                          <span className="cost-num">₹{Number(h.price_per_night).toLocaleString()} / night</span>
                          <a
                            href={getGoogleMapsUrl(h.name, selectedDest.city, selectedDest.country)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="maps-external-link"
                            aria-label={`Explore ${h.name} on Google Maps`}
                          >
                            Map <IconExternalLink size={12} />
                          </a>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : modalTab === "restaurants" ? (
                <div className="editorial-catalogue-list">
                  {modalData.restaurants.length === 0 ? (
                    <p className="empty-notice">No dining venues recorded.</p>
                  ) : (
                    modalData.restaurants.map((r) => (
                      <div key={r.id} className="editorial-catalogue-row">
                        <div className="catalogue-row-main">
                          <div className="catalogue-row-title">
                            <strong>{r.name}</strong>
                            <span className="rating-pill">
                              <IconStar size={12} /> {r.rating || "4.5"}
                            </span>
                          </div>
                          <p className="catalogue-row-sub">Cuisine: {r.cuisine}</p>
                        </div>
                        <div className="catalogue-row-meta">
                          <span className="cost-num">~₹{Number(r.average_cost_per_person).toLocaleString()} / person</span>
                          <a
                            href={getGoogleMapsUrl(r.name, selectedDest.city, selectedDest.country)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="maps-external-link"
                            aria-label={`Explore ${r.name} on Google Maps`}
                          >
                            Map <IconExternalLink size={12} />
                          </a>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              ) : (
                <div className="editorial-catalogue-list">
                  {modalData.attractions.length === 0 ? (
                    <p className="empty-notice">No attractions recorded.</p>
                  ) : (
                    modalData.attractions.map((a) => (
                      <div key={a.id} className="editorial-sight-row">
                        <div className="sight-thumb">
                          <img
                            src={getAttractionImageUrl(a)}
                            alt={a.name}
                            loading="lazy"
                            onError={(e) => {
                              e.target.src = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=400&q=80";
                            }}
                          />
                        </div>
                        <div className="sight-details">
                          <div className="catalogue-row-title">
                            <strong>{a.name}</strong>
                            <span className="rating-pill">
                              <IconStar size={12} /> {a.rating || "4.8"}
                            </span>
                          </div>
                          <p className="catalogue-row-sub">Category: {a.category}</p>
                          <div className="sight-row-footer">
                            <span className="cost-num">
                              {Number(a.entry_fee) === 0 ? "Complimentary entry" : `Entry: ₹${Number(a.entry_fee).toLocaleString()}`}
                            </span>
                            <a
                              href={getGoogleMapsUrl(a.name, selectedDest.city, selectedDest.country)}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="maps-external-link"
                              aria-label={`Explore ${a.name} on Google Maps`}
                            >
                              Map <IconExternalLink size={12} />
                            </a>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>

            <div className="editorial-modal-footer">
              <Link
                className="editorial-action-btn"
                to={`/plan?destinationId=${selectedDest.id}&city=${encodeURIComponent(selectedDest.city)}`}
                onClick={() => setSelectedDest(null)}
              >
                Plan Itinerary for {selectedDest.city} <IconArrowRight size={14} />
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
