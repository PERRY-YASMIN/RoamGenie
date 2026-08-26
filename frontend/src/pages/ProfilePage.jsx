import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { getUserPreferences, updateUserPreferences } from "../services/api";

const ACTIVITY_OPTIONS = [
  "heritage",
  "culinary",
  "photography",
  "nature",
  "palaces",
  "temples",
  "adventure",
  "shopping",
  "beaches",
  "museums",
  "wildlife",
  "wellness",
];

export default function ProfilePage() {
  const { user, isAuthenticated, logout } = useAuth();
  const { success, error: toastError } = useToast();
  const [preferences, setPreferences] = useState({
    hotel_preference: "moderate",
    food_preference: "vegetarian",
    transport_preference: "train",
    travel_style: "cultural",
    special_requirements: "",
    activities: ["heritage", "culinary"],
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (isAuthenticated) {
      loadPreferences();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  async function loadPreferences() {
    setLoading(true);
    try {
      const data = await getUserPreferences();
      setPreferences({
        hotel_preference: data.hotel_preference || "moderate",
        food_preference: data.food_preference || "vegetarian",
        transport_preference: data.transport_preference || "train",
        travel_style: data.travel_style || "cultural",
        special_requirements: data.special_requirements || "",
        activities: data.activities || ["heritage", "culinary"],
      });
    } catch (err) {
      console.error("Failed to load preferences", err);
      toastError(err.message || "Failed to load preferences.");
    } finally {
      setLoading(false);
    }
  }

  function handleInputChange(e) {
    const { name, value } = e.target;
    setPreferences((prev) => ({ ...prev, [name]: value }));
  }

  function toggleActivity(act) {
    setPreferences((prev) => {
      const exists = prev.activities.includes(act);
      const next = exists ? prev.activities.filter((a) => a !== act) : [...prev.activities, act];
      return { ...prev, activities: next };
    });
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      await updateUserPreferences(preferences);
      const msg = "Preferences and activity tags updated successfully!";
      setMessage({ type: "success", text: msg });
      success(msg);
    } catch (err) {
      const msg = err.message || "Failed to update preferences.";
      setMessage({ type: "error", text: msg });
      toastError(msg);
    } finally {
      setSaving(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="panel" role="region" aria-label="Profile Required">
        <h1>Profile & Preferences</h1>
        <p>Please log in to manage your travel profile.</p>
        <Link className="button button-primary" to="/login">Log In →</Link>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="page-header">
        <p className="eyebrow">User Customization & Normalized Preferences</p>
        <h1>Traveller Profile</h1>
        <p>Manage your account credentials, default travel preferences, and normalized activity interests.</p>
      </div>

      <div className="profile-layout">
        {/* User Card */}
        <aside className="user-info-card" aria-label="Traveller Account Information">
          <div className="avatar-placeholder">👤</div>
          <h2>{user?.full_name || "Traveller"}</h2>
          <p className="user-email">{user?.email}</p>
          <span className="user-role-badge">Role: {user?.role || "traveller"}</span>

          <div className="account-stats">
            <div className="stat">
              <span className="label">Registered</span>
              <strong>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Active"}</strong>
            </div>
            <div className="stat">
              <span className="label">Security</span>
              <strong>Argon2id + JWT</strong>
            </div>
          </div>

          <button type="button" className="button button-outline button-full" onClick={logout} aria-label="Log out of account">
            Log Out
          </button>
        </aside>

        {/* Preferences Form */}
        <main className="preferences-card" aria-label="Default Travel Preferences">
          <h2>Default Travel Preferences</h2>
          <p>These settings automatically initialize the trip planner wizard for personalized itinerary recommendations.</p>

          {loading ? (
            <div className="loading-state" role="status" aria-live="polite">
              <div className="spinner"></div>
              <p>Loading your preferences from database...</p>
            </div>
          ) : (
            <>
              {message && (
                <div className={`message-banner ${message.type}`} role="alert">
                  <p>{message.type === "success" ? "✓" : "⚠️"} {message.text}</p>
                </div>
              )}

              <form onSubmit={handleSave}>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="hotel_preference">Accommodation Tier</label>
                    <select
                      id="hotel_preference"
                      name="hotel_preference"
                      value={preferences.hotel_preference}
                      onChange={handleInputChange}
                      disabled={saving}
                    >
                      <option value="budget">Budget (Hostels / Guesthouses)</option>
                      <option value="moderate">Moderate (3-Star Boutique)</option>
                      <option value="luxury">Luxury (Heritage Resorts / 5-Star)</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="food_preference">Food & Dining Preference</label>
                    <select
                      id="food_preference"
                      name="food_preference"
                      value={preferences.food_preference}
                      onChange={handleInputChange}
                      disabled={saving}
                    >
                      <option value="vegetarian">Vegetarian</option>
                      <option value="non-veg">Non-Vegetarian</option>
                      <option value="vegan">Vegan</option>
                      <option value="halal">Halal</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="transport_preference">Primary Transport Mode</label>
                    <select
                      id="transport_preference"
                      name="transport_preference"
                      value={preferences.transport_preference}
                      onChange={handleInputChange}
                      disabled={saving}
                    >
                      <option value="train">Train / Rail</option>
                      <option value="flight">Flight / Air</option>
                      <option value="bus">Bus / Coach</option>
                      <option value="self-drive">Self-Drive / Car Rental</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label htmlFor="travel_style">Travel Style</label>
                    <select
                      id="travel_style"
                      name="travel_style"
                      value={preferences.travel_style}
                      onChange={handleInputChange}
                      disabled={saving}
                    >
                      <option value="cultural">Cultural & Heritage Focus</option>
                      <option value="relaxed">Relaxed & Leisure</option>
                      <option value="fast-paced">Fast-Paced Explorer</option>
                      <option value="adventure">Outdoor Adventure</option>
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="special_requirements">Special Requirements / Dietary Notes</label>
                  <input
                    id="special_requirements"
                    name="special_requirements"
                    type="text"
                    value={preferences.special_requirements}
                    onChange={handleInputChange}
                    placeholder="e.g. Wheelchair access, gluten-free dining, near city center"
                    disabled={saving}
                  />
                </div>

                <div className="form-group">
                  <label>Normalized Activity Interests (Stored in <code>activity_preferences</code>)</label>
                  <div className="tag-cloud">
                    {ACTIVITY_OPTIONS.map((act) => (
                      <button
                        key={act}
                        type="button"
                        className={`tag-btn ${preferences.activities.includes(act) ? "selected" : ""}`}
                        onClick={() => toggleActivity(act)}
                        disabled={saving}
                        aria-label={`Toggle interest in ${act}`}
                      >
                        {preferences.activities.includes(act) ? "✓ " : "+ "}
                        {act}
                      </button>
                    ))}
                  </div>
                </div>

                <button type="submit" className="button button-primary" disabled={saving}>
                  {saving ? "Saving Changes..." : "Save Preferences"}
                </button>
              </form>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
