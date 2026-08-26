const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function fetchWithTimeout(url, options = {}, timeoutMs = 8000) {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    window.clearTimeout(timeout);
  }
}

function getAuthHeader() {
  const token = localStorage.getItem("roamgenie_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function handleResponse(response, fallbackErrorMsg = "Operation failed.") {
  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem("roamgenie_token");
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("roamgenie:auth-expired"));
      }
    }
    const body = await response.json().catch(() => null);
    const errorMsg =
      body?.error?.message ??
      (typeof body?.detail === "string"
        ? body.detail
        : body?.detail?.[0]?.msg ?? fallbackErrorMsg);
    throw new Error(errorMsg);
  }
  if (response.status === 204) return null;
  return response.json();
}

/* ================= PREVIEW / STARTER API ================= */
export async function previewPlan(payload) {
  const response = await fetch(`${API_BASE}/plans/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, "Could not create the preview.");
}

/* ================= AUTHENTICATION APIS ================= */
export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await handleResponse(response, "Invalid email or password.");
  if (data?.access_token) {
    localStorage.setItem("roamgenie_token", data.access_token);
  }
  return data;
}

export async function registerUser(email, password, fullName) {
  const response = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  return handleResponse(response, "Registration failed. Please check inputs.");
}

export async function getMe() {
  const response = await fetch(`${API_BASE}/users/me`, {
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to load user profile.");
}

export async function getUserPreferences() {
  const response = await fetch(`${API_BASE}/users/me/preferences`, {
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to load preferences.");
}

export async function updateUserPreferences(payload) {
  const response = await fetch(`${API_BASE}/users/me/preferences`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, "Failed to update preferences.");
}

/* ================= CATALOGUE APIS ================= */
export async function getDestinations(search = "", activeOnly = true, limit = 500) {
  const params = new URLSearchParams();
  if (search) params.append("search", search);
  if (activeOnly) params.append("active_only", "true");
  if (limit) params.append("limit", limit.toString());
  const response = await fetchWithTimeout(`${API_BASE}/destinations?${params.toString()}`);
  return handleResponse(response, "Failed to load destinations.");
}

export async function getDestination(id) {
  const response = await fetch(`${API_BASE}/destinations/${id}`);
  return handleResponse(response, "Failed to load destination details.");
}

export async function getHotels(destinationId) {
  const response = await fetch(`${API_BASE}/hotels?destination_id=${destinationId}`);
  return handleResponse(response, "Failed to load hotels.");
}

export async function getRestaurants(destinationId) {
  const response = await fetch(`${API_BASE}/restaurants?destination_id=${destinationId}`);
  return handleResponse(response, "Failed to load restaurants.");
}

export async function getAttractions(destinationId) {
  const response = await fetch(`${API_BASE}/attractions?destination_id=${destinationId}`);
  return handleResponse(response, "Failed to load attractions.");
}

export async function getTransportOptions(destinationId) {
  const response = await fetch(`${API_BASE}/transport-options?destination_id=${destinationId}`);
  return handleResponse(response, "Failed to load transport options.");
}

/* ================= TRIPS & PLANNING APIS ================= */
export async function createTrip(payload) {
  const response = await fetch(`${API_BASE}/trips`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, "Failed to create trip.");
}

export async function listTrips() {
  const response = await fetch(`${API_BASE}/trips`, {
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to load trips.");
}

export async function listSavedTrips() {
  const response = await fetch(`${API_BASE}/trips/saved`, {
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to load saved trips.");
}

export async function getTrip(id) {
  const response = await fetch(`${API_BASE}/trips/${id}`, {
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to load trip details.");
}

export async function deleteTrip(id) {
  const response = await fetch(`${API_BASE}/trips/${id}`, {
    method: "DELETE",
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to delete trip.");
}

export async function generateTripPlan(id, preferences = [], forceAi = false) {
  const params = new URLSearchParams();
  if (forceAi) params.append("force_ai", "true");
  preferences.forEach((p) => params.append("preferences", p));
  const response = await fetch(`${API_BASE}/trips/${id}/generate?${params.toString()}`, {
    method: "POST",
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to generate itinerary plan.");
}

export async function toggleSaveTrip(id) {
  const response = await fetch(`${API_BASE}/trips/${id}/save`, {
    method: "POST",
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to update bookmark.");
}

export async function swapItineraryItem(tripId, itemId, payload) {
  const response = await fetch(`${API_BASE}/trips/${tripId}/itinerary/items/${itemId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify(payload),
  });
  return handleResponse(response, "Failed to swap itinerary item.");
}

export async function getTripWeather(id) {
  const response = await fetch(`${API_BASE}/trips/${id}/weather`, {
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to load weather forecast.");
}

/* ================= ASSISTANT & PACKING APIS ================= */
export async function chatAssistant(message, tripId = null, conversationId = null) {
  const response = await fetch(`${API_BASE}/assistant/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify({ message, trip_id: tripId, conversation_id: conversationId }),
  });
  return handleResponse(response, "AI Assistant is currently unavailable.");
}

export async function getPackingItems(tripId) {
  const response = await fetch(`${API_BASE}/assistant/trips/${tripId}/packing`, {
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to load packing items.");
}

export async function addPackingItem(tripId, item, category = "General") {
  const response = await fetch(`${API_BASE}/assistant/trips/${tripId}/packing`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify({ item, category }),
  });
  return handleResponse(response, "Failed to add packing item.");
}

export async function togglePackingItem(itemId, isPacked) {
  const response = await fetch(`${API_BASE}/assistant/packing/${itemId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify({ is_packed: isPacked }),
  });
  return handleResponse(response, "Failed to update packing status.");
}

export async function deletePackingItem(itemId) {
  const response = await fetch(`${API_BASE}/assistant/packing/${itemId}`, {
    method: "DELETE",
    headers: { ...getAuthHeader() },
  });
  return handleResponse(response, "Failed to delete packing item.");
}

/* ================= DBMS SHOWCASE & SQL APIS ================= */
export async function getReportQueries() {
  const response = await fetch(`${API_BASE}/reports/queries`);
  return handleResponse(response, "Failed to load DBMS queries.");
}

export async function executeReportQuery(queryId) {
  const response = await fetch(`${API_BASE}/reports/queries/${queryId}`);
  return handleResponse(response, `Failed to execute ${queryId}.`);
}

export async function executeCustomSQL(sql) {
  const response = await fetch(`${API_BASE}/reports/execute-sql`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...getAuthHeader() },
    body: JSON.stringify({ sql }),
  });
  return handleResponse(response, "Failed to execute custom SQL query.");
}

export async function getAuditLogs(limit = 50) {
  const response = await fetch(`${API_BASE}/reports/audit-logs?limit=${limit}`);
  return handleResponse(response, "Failed to load audit logs.");
}
