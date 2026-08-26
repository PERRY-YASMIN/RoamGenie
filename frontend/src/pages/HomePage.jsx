import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { getDestinations } from "../services/api";
import { getEnvironment } from "../components/immersive/environmentConfig";

export default function HomePage() {
  const { isAuthenticated, user } = useAuth();
  const [destinations, setDestinations] = useState([]);
  const [selectedDestination, setSelectedDestination] = useState(null);

  useEffect(() => {
    getDestinations().then(setDestinations).catch(() => setDestinations([]));
  }, []);

  const environment = getEnvironment(selectedDestination);
  const featuredDestinations = destinations.slice(0, 4);

  return (
    <div className="home-container immersive-home">
      <section className="arrival-scene">
        <div className="arrival-copy">
          <p className="arrival-mark">ROAMGENIE / 01</p>
          <p className="arrival-place">{environment.label} <span>{environment.region}</span></p>
          <h1>{environment.headline}</h1>
          <p className="arrival-subline">{environment.subline}</p>
          <div className="arrival-actions">
            <Link className="scene-button scene-button-solid" to="/plan">Begin exploring <span>↗</span></Link>
            <Link className="scene-button scene-button-quiet" to="/destinations">Browse the atlas</Link>
          </div>
          {isAuthenticated && <p className="arrival-welcome">Welcome back, {user?.full_name?.split(" ")[0]}.</p>}
        </div>
        <div className="weather-peek"><span>{environment.temperature}</span><small>{environment.weather}</small></div>
        <div className="scroll-cue"><span>Scroll to travel</span><i /></div>
      </section>

      <section className="discovery-section">
        <div className="journey-label"><span>02</span><span>Make it yours</span></div>
        <div className="home-planning-grid">
          <div className="discovery-heading">
            <p className="eyebrow">A quieter way to plan</p>
            <h2>Start with how you want to feel.</h2>
            <p>Set a place, a pace, and a budget. RoamGenie will shape the route around you.</p>
            <Link className="home-text-link" to="/plan">Open the trip planner <span>↗</span></Link>
          </div>
          <div className="home-planning-note">
            <span className="note-index">01</span>
            <strong>Tell us the essentials.</strong>
            <p>Dates, travellers, starting point, and the kind of day you want to have.</p>
            <span className="note-index">02</span>
            <strong>Let the route breathe.</strong>
            <p>Get a day-by-day itinerary, costs, weather context, and packing ideas.</p>
          </div>
        </div>

        <div className="home-destinations-heading">
          <div>
            <p className="eyebrow">From the catalogue</p>
            <h3>Places with a story to tell.</h3>
          </div>
          <Link className="home-text-link" to="/destinations">Explore all destinations <span>↗</span></Link>
        </div>
        <div className="destination-preview-grid">
          {featuredDestinations.map((destination) => {
            const active = selectedDestination?.id === destination.id;
            return (
              <button
                className={`destination-preview ${active ? "is-selected" : ""}`}
                key={destination.id}
                onClick={() => setSelectedDestination(destination)}
                type="button"
              >
                <span className="preview-country">{destination.country}</span>
                <strong>{destination.city}</strong>
                <span>{destination.description || "A considered place for your next journey."}</span>
                <small>From ₹{Number(destination.average_daily_cost || 3500).toLocaleString()} / day</small>
              </button>
            );
          })}
        </div>
      </section>
    </div>
  );
}
