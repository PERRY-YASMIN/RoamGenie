import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { getUserPreferences, updateUserPreferences } from "../services/api";
import { IconUser, IconCheck, IconAlert } from "../components/icons";

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
      console.error(err);
      toastError(err.message || "Failed to load preferences.");
    } finally {
      setLoading(false);
    }
  }

  function handleInputChange(e) {
    const { name, value } = e.target;
    setPreferences((prev) => ({ ...prev, [name]: value }));
  }

  function toggleActivity(activity) {
    setPreferences((prev) => {
      const exists = prev.activities.includes(activity);
      return {
        ...prev,
        activities: exists
          ? prev.activities.filter((a) => a !== activity)
          : [...prev.activities, activity],
      };
    });
  }

  async function handleSave(e) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const updated = await updateUserPreferences(preferences);
      setPreferences(updated);
      setMessage({ type: "success", text: "Travel preferences saved successfully." });
      success("Preferences updated.");
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Failed to update preferences." });
      toastError(err.message || "Failed to save preferences.");
    } finally {
      setSaving(false);
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="profile-editorial-page">
        <header className="editorial-page-header">
          <p className="editorial-eyebrow">ACCOUNT</p>
          <h1 className="editorial-page-title">Traveller Profile</h1>
          <p className="editorial-page-subtitle">Please log in to manage your account details and travel preferences.</p>
          <div className="editorial-auth-actions">
            <Link className="editorial-action-btn" to="/login">Log In →</Link>
          </div>
        </header>
      </div>
    );
  }

  return (
    <div className="profile-editorial-page">
      <header className="editorial-page-header">
        <p className="editorial-eyebrow">ACCOUNT SETTINGS</p>
        <h1 className="editorial-page-title">Traveller Profile</h1>
        <p className="editorial-page-subtitle">
          Manage your account credentials, default travel preferences, and activity interests.
        </p>
      </header>

      <div className="profile-editorial-layout">
        {/* User Sidebar */}
        <aside className="profile-editorial-aside" aria-label="Traveller Account Information">
          <div className="profile-avatar-slot">
            <IconUser size={28} />
          </div>
          <h2 className="profile-user-name">{user?.full_name || "Traveller"}</h2>
          <p className="profile-user-email">{user?.email}</p>
          <span className="profile-role-tag">ROLE: {(user?.role || "traveller").toUpperCase()}</span>

          <div className="profile-stats-list">
            <div className="profile-stat-row">
              <span className="stat-label">REGISTERED</span>
              <strong className="stat-val">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : "Active"}
              </strong>
            </div>
            <div className="profile-stat-row">
              <span className="stat-label">AUTHENTICATION</span>
              <strong className="stat-val">Argon2id + JWT</strong>
            </div>
          </div>

          <button
            type="button"
            className="editorial-quiet-btn button-full"
            onClick={logout}
            aria-label="Log out of account"
          >
            Log Out
          </button>
        </aside>

        {/* Preferences Form */}
        <main className="profile-editorial-main" aria-label="Default Travel Preferences">
          <div className="profile-main-header">
            <h3>Default Travel Preferences</h3>
            <p className="profile-main-sub">
              These settings initialize the trip planner wizard for personalized itinerary recommendations.
            </p>
          </div>

          {loading ? (
            <div className="editorial-loading-state" role="status" aria-live="polite">
              <div className="editorial-spinner" />
              <p>Loading your preferences from database...</p>
            </div>
          ) : (
            <>
              {message && (
                <div className={`editorial-message-banner ${message.type}`} role="alert">
                  {message.type === "success" ? <IconCheck size={14} /> : <IconAlert size={14} />}
                  <span>{message.text}</span>
                </div>
              )}

              <form onSubmit={handleSave} className="profile-editorial-form">
                <div className="form-two-col">
                  <div className="editorial-field-block">
                    <label htmlFor="hotel_preference" className="field-label-editorial">
                      Accommodation Tier
                    </label>
                    <select
                      id="hotel_preference"
                      name="hotel_preference"
                      className="editorial-select"
                      value={preferences.hotel_preference}
                      onChange={handleInputChange}
                    >
                      <option value="budget">Budget (Hostels / Guesthouses)</option>
                      <option value="moderate">Moderate (Boutique / 3-Star)</option>
                      <option value="luxury">Luxury (Heritage / 5-Star)</option>
                    </select>
                  </div>

                  <div className="editorial-field-block">
                    <label htmlFor="food_preference" className="field-label-editorial">
                      Dining Style
                    </label>
                    <select
                      id="food_preference"
                      name="food_preference"
                      className="editorial-select"
                      value={preferences.food_preference}
                      onChange={handleInputChange}
                    >
                      <option value="vegetarian">Vegetarian</option>
                      <option value="vegan">Vegan</option>
                      <option value="halal">Halal</option>
                      <option value="local_specialties">Local Specialties</option>
                      <option value="fine_dining">Fine Dining</option>
                      <option value="street_food">Street Food & Markets</option>
                    </select>
                  </div>
                </div>

                <div className="form-two-col">
                  <div className="editorial-field-block">
                    <label htmlFor="transport_preference" className="field-label-editorial">
                      Transit Preference
                    </label>
                    <select
                      id="transport_preference"
                      name="transport_preference"
                      className="editorial-select"
                      value={preferences.transport_preference}
                      onChange={handleInputChange}
                    >
                      <option value="train">Rail & Train</option>
                      <option value="bus">Regional Bus / Coach</option>
                      <option value="flight">Domestic Flight</option>
                      <option value="self_drive">Self Drive / Rental</option>
                    </select>
                  </div>

                  <div className="editorial-field-block">
                    <label htmlFor="travel_style" className="field-label-editorial">
                      Primary Pace
                    </label>
                    <select
                      id="travel_style"
                      name="travel_style"
                      className="editorial-select"
                      value={preferences.travel_style}
                      onChange={handleInputChange}
                    >
                      <option value="relaxed">Relaxed (1-2 activities / day)</option>
                      <option value="moderate">Balanced (3-4 activities / day)</option>
                      <option value="fast_paced">Immersive / Fast Paced</option>
                      <option value="cultural">Heritage & Cultural Focus</option>
                    </select>
                  </div>
                </div>

                <div className="editorial-field-block">
                  <label htmlFor="special_requirements" className="field-label-editorial">
                    Special Notes or Dietary Needs
                  </label>
                  <textarea
                    id="special_requirements"
                    name="special_requirements"
                    className="editorial-textarea"
                    rows={3}
                    placeholder="e.g. Accessibility needs, allergies, preferred arrival times..."
                    value={preferences.special_requirements}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="editorial-field-block">
                  <label className="field-label-editorial">Activity & Sights Interests</label>
                  <div className="editorial-preference-list">
                    {ACTIVITY_OPTIONS.map((act) => (
                      <button
                        key={act}
                        type="button"
                        className={`preference-text-link ${preferences.activities.includes(act) ? "selected" : ""}`}
                        onClick={() => toggleActivity(act)}
                        disabled={saving}
                        aria-label={`Toggle interest in ${act}`}
                      >
                        {act}
                      </button>
                    ))}
                  </div>
                </div>

                <button type="submit" className="editorial-action-btn" disabled={saving}>
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
