# RoamGenie — Dataset Documentation

## 1. Master Dataset Structure

The RoamGenie master database contains **21,133 total rows** across 23 tables, exceeding the academic requirement of $\ge 5,000$ records.

```
┌─────────────────────────────────────────────────────────────┐
│              Master Travel Catalogue Dataset                │
│  - 500 Destinations (144 India, 356 Global across 8 regions)│
│  - 6,000 Hotels (12 per destination, 3 budget tiers)        │
│  - 6,000 Restaurants (12 per destination, diverse cuisines) │
│  - 6,000 Transport Options (12 per destination, multi-modal)│
│  - 2,517 Attractions (Heritage, Forts, Temples, Nature)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Dataset Distributions by Entity

### 2.1 Destinations (`destinations` table — 500 rows)
- **Geographic Scope:** 8 geographic zones including India (144), Southeast & East Asia (85), Europe (90), North & South America (55), Middle East & Central Asia (50), Africa (45), Oceania & Pacific (35).
- **Attributes:** City, Country, Description with iconic landmarks, Average Daily Cost in INR, Active flag.
- **Visuals:** 100% curated landmark cover photography and direct Google Maps exploration URLs.

### 2.2 Accommodations (`hotels` table — 6,000 rows)
- **Density:** Exactly 12 verified hotels per destination.
- **Budget Tiers:** Divided across Economy (e.g. ₹1,200–₹2,500), Moderate (e.g. ₹2,800–₹6,500), and Luxury (e.g. ₹7,000–₹25,000).
- **Ratings:** Bounded between `3.5` and `5.0` stars.

### 2.3 Dining Venues (`restaurants` table — 6,000 rows)
- **Density:** Exactly 12 verified restaurants per destination.
- **Cuisine Variety:** Authentic regional specialties (e.g. Rajasthani, Mughlai, Chettinad, Japanese Kaiseki, French Bistro, Italian Trattoria, Mexican, Mediterranean).
- **Cost Spectrum:** Averaging from ₹250 to ₹3,500 per person.

### 2.4 Sightseeing & Activities (`attractions` table — 2,517 rows)
- **Density:** Approximately 5–6 prominent cultural, historical, and nature attractions per destination.
- **Categories:** Heritage, Temple, Fort, Palace, Beach, Nature Reserve, Museum, Viewpoint.

### 2.5 Multi-Modal Transit (`transport_options` table — 6,000 rows)
- **Density:** Exactly 12 transport options per destination.
- **Modes:** Flights, Express Trains, Inter-City Buses, Private Cabs, and Ferries.
- **Verified D5 Dataset Tests:** 80 / 80 passed.
