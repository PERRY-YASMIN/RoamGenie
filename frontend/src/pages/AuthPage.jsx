import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function AuthPage() {
  const { search } = useLocation();
  const navigate = useNavigate();
  const { login, register } = useAuth();
  const { success, error: toastError } = useToast();

  const queryParams = new URLSearchParams(search);
  const initialMode = queryParams.get("mode") === "register" ? "register" : "login";

  const [mode, setMode] = useState(initialMode); // login | register
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    fullName: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function handleChange(e) {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (mode === "login") {
        await login(formData.email, formData.password);
        success("Welcome back! Logged in successfully.");
      } else {
        await register(formData.email, formData.password, formData.fullName);
        success("Account created and logged in!");
      }
      navigate("/plan");
    } catch (err) {
      const msg = err.message || "Authentication failed.";
      setError(msg);
      toastError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page-container">
      <div className="auth-card panel" role="region" aria-label="Authentication Form">
        <div className="auth-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={mode === "login"}
            className={`auth-tab-btn ${mode === "login" ? "active" : ""}`}
            onClick={() => {
              setMode("login");
              setError(null);
            }}
          >
            Log In
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === "register"}
            className={`auth-tab-btn ${mode === "register" ? "active" : ""}`}
            onClick={() => {
              setMode("register");
              setError(null);
            }}
          >
            Sign Up
          </button>
        </div>

        <p className="eyebrow">Argon2id & JWT Authentication</p>
        <h1>{mode === "login" ? "Welcome Back" : "Create Account"}</h1>
        <p className="auth-subtitle">
          {mode === "login"
            ? "Log in to access your saved multi-day itineraries and preferences."
            : "Register with RoamGenie to store custom plans, budgets, and checklists."}
        </p>

        {error && (
          <div className="error-banner" role="alert">
            <p>⚠️ {error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <div className="form-group">
              <label htmlFor="fullName">Full Name</label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                required
                disabled={loading}
                value={formData.fullName}
                onChange={handleChange}
                placeholder="e.g. Yasmin S"
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              required
              disabled={loading}
              value={formData.email}
              onChange={handleChange}
              placeholder="user@example.com"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              name="password"
              type="password"
              required
              disabled={loading}
              minLength={6}
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
            />
          </div>

          <button type="submit" className="button button-primary button-full" disabled={loading}>
            {loading ? "Processing..." : mode === "login" ? "Log In →" : "Create Account →"}
          </button>
        </form>

        <div className="auth-footer-text">
          {mode === "login" ? (
            <p>
              Don't have an account?{" "}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setMode("register");
                  setError(null);
                }}
              >
                Sign up here
              </button>
            </p>
          ) : (
            <p>
              Already registered?{" "}
              <button
                type="button"
                className="link-btn"
                onClick={() => {
                  setMode("login");
                  setError(null);
                }}
              >
                Log in here
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
