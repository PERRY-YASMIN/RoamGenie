import { createContext, useContext, useEffect, useState } from "react";
import { getMe, loginUser, registerUser } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadUser() {
      const token = localStorage.getItem("roamgenie_token");
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const profile = await getMe();
        setUser(profile);
      } catch (err) {
        localStorage.removeItem("roamgenie_token");
        setUser(null);
      } finally {
        setLoading(false);
      }
    }
    loadUser();

    function handleAuthExpired() {
      localStorage.removeItem("roamgenie_token");
      setUser(null);
    }

    window.addEventListener("roamgenie:auth-expired", handleAuthExpired);
    return () => {
      window.removeEventListener("roamgenie:auth-expired", handleAuthExpired);
    };
  }, []);

  async function login(email, password) {
    const data = await loginUser(email, password);
    const profile = await getMe();
    setUser(profile);
    return data;
  }

  async function register(email, password, fullName) {
    await registerUser(email, password, fullName);
    return login(email, password);
  }

  function logout() {
    localStorage.removeItem("roamgenie_token");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
