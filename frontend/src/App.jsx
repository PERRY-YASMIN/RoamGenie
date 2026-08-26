import { useEffect } from "react";
import { Link, Route, Routes, useLocation } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { ToastProvider, useToast } from "./context/ToastContext";
import ToastContainer from "./components/ToastContainer";
import AuthPage from "./pages/AuthPage";
import DestinationsPage from "./pages/DestinationsPage";
import HomePage from "./pages/HomePage";
import PlanPage from "./pages/PlanPage";
import ProfilePage from "./pages/ProfilePage";
import ShowcasePage from "./pages/ShowcasePage";
import TripsPage from "./pages/TripsPage";
import AmbientWorld from "./components/immersive/AmbientWorld";

function Navigation() {
  const { isAuthenticated, user, logout } = useAuth();
  const { info } = useToast();
  const location = useLocation();

  const isActive = (path) => (location.pathname === path ? "nav-link active" : "nav-link");

  const handleLogout = () => {
    logout();
    info("You have logged out.");
  };

  return (
    <header className="app-header">
      <Link className="brand" to="/" aria-label="RoamGenie Home">
        <span className="brand-mark" aria-hidden="true" /> RoamGenie
      </Link>

      <nav aria-label="Main navigation" className="main-nav">
        <Link className={isActive("/")} to="/">Home</Link>
        <Link className={isActive("/plan")} to="/plan">Plan Trip</Link>
        <Link className={isActive("/destinations")} to="/destinations">Destinations</Link>
        {isAuthenticated && (
          <Link className={isActive("/trips")} to="/trips">My Trips</Link>
        )}
        <Link className={isActive("/showcase")} to="/showcase">
          <span className="showcase-pill">DBMS Showcase</span>
        </Link>
      </nav>

      <div className="auth-actions">
        {isAuthenticated ? (
          <div className="user-dropdown">
            <Link className="profile-link" to="/profile" aria-label="User Profile">
              <span className="avatar-chip" aria-hidden="true" />
              <span className="user-name">{user?.full_name?.split(" ")[0] || "Profile"}</span>
            </Link>
            <button type="button" className="button button-sm button-ghost" onClick={handleLogout} aria-label="Log out of account">
              Log out
            </button>
          </div>
        ) : (
          <div className="guest-actions">
            <Link className="button button-sm button-outline" to="/login">Log in</Link>
            <Link className="button button-sm button-primary" to="/register">Sign up</Link>
          </div>
        )}
      </div>
    </header>
  );
}

function NotFound() {
  return (
    <main className="panel not-found-panel" role="main">
      <p className="eyebrow">404 Error</p>
      <h1>Page Not Found</h1>
      <p>The requested route does not exist.</p>
      <Link className="button button-primary" to="/">Return Home →</Link>
    </main>
  );
}

function AppContent() {
  const location = useLocation();
  const { warning } = useToast();
  const isArrival = location.pathname === "/";

  useEffect(() => {
    function handleAuthExpired() {
      warning("Your session has expired. Please log in again.", 6000);
    }
    window.addEventListener("roamgenie:auth-expired", handleAuthExpired);
    return () => {
      window.removeEventListener("roamgenie:auth-expired", handleAuthExpired);
    };
  }, [warning]);

  return (
    <div className={`app-shell ${isArrival ? "is-arrival" : ""}`}>
      <ToastContainer />
      <AmbientWorld showScene />
      <div className="shell-header"><Navigation /></div>
      <main className={`app-main ${isArrival ? "arrival-main" : ""}`}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/plan" element={<PlanPage />} />
          <Route path="/destinations" element={<DestinationsPage />} />
          <Route path="/trips" element={<TripsPage />} />
          <Route path="/showcase" element={<ShowcasePage />} />
          <Route path="/login" element={<AuthPage />} />
          <Route path="/register" element={<AuthPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer className="app-footer">
        <div className="footer-content">
          <p>RoamGenie · Semester 5 DBMS Course Project · Powered by PostgreSQL 15+ & FastAPI</p>
          <div className="footer-links">
            <Link to="/showcase">18 SQL Benchmark Queries</Link>
            <span>·</span>
            <Link to="/destinations">Travel Catalogue</Link>
            <span>·</span>
            <Link to="/plan">Itinerary Planner</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ToastProvider>
  );
}
