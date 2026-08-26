# RoamGenie — Known Limitations & Future Enhancements

This document distinguishes verified MVP behaviors, known system boundaries, and proposed future enhancements for post-v1.0.0 releases.

---

## 1. Verified System Scope & Known Boundaries

1. **Synthetic Catalogue Data with Authentic Landmarks:** While destination landmarks, city descriptions, coordinates, and photo mappings represent authentic world locations, individual hotel and restaurant pricing represents realistic synthetic baseline entries generated for academic simulation.
2. **Open-Meteo Weather Dependency:** Live 5-day weather forecasts depend on external internet connectivity to the Open-Meteo public API; when offline, RoamGenie serves cached snapshots or graceful seasonal averages.
3. **AI LLM Rate Limits:** External Gemini/Groq providers are subject to third-party API quotas; when quotas are exceeded or network fails, RoamGenie automatically triggers the deterministic heuristic scheduler.
4. **Single Currency Base (INR):** Financial amounts and budget optimizations currently operate in Indian Rupees (₹ / INR).

---

## 2. Proposed Future Enhancements (Post-MVP)

1. **Multi-Currency Conversion:** Dynamic exchange rate conversion (USD, EUR, GBP, JPY).
2. **Real-Time Booking APIs:** Integration with live GDS/OTA booking APIs (Amadeus, Skyscanner, Booking.com).
3. **Collaborative Real-Time Editing:** WebSocket-powered multi-user itinerary editing for group travellers.
4. **Offline Mobile Application:** Progressive Web App (PWA) with local SQLite synchronization.
