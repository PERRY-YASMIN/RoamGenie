# Master Travel Catalogue Datasets Report (D1–D5)

**Project:** RoamGenie — AI Travel Planner & Budget Optimizer  
**Course:** Database Management Systems (Semester 5 Theory & Project)  
**Total Catalogue Records:** 21,017 Verified Records across 500 Destinations  
**Status:** Authoritative Dataset Baseline

---

## 1. Master Catalogue Dataset Summary

```
┌────────────────────────────────────────────────────────────────────────┐
│               ROAMGENIE MASTER TRAVEL CATALOGUE DATASETS               │
├────────────────────────────────────────────────────────────────────────┤
│ • D1: Destinations Master (500 Destinations across 93 Countries)       │
│ • D2: Attractions Master  (2,517 Sights across 19 Categories)          │
│ • D3: Accommodations      (6,000 Hotels from Hostels to Luxury 5-Star) │
│ • D4: Dining Venues       (6,000 Restaurants across 254 Cuisines)      │
│ • D5: Transport Options   (6,000 Intercity & Intra-City Transit Modes) │
│────────────────────────────────────────────────────────────────────────│
│ TOTAL VERIFIED CATALOGUE RECORDS: 21,017 ENTITIES (100% POSTGRESQL FK) │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Dataset Module Breakdown

### 2.1 Phase D1: Master Destinations Dataset
* **Target Table:** `destinations`
* **Total Records:** 500
* **Countries Represented:** 93
* **Regional Distribution:**
  - India: 144 destinations
  - Europe: 105 destinations
  - Southeast / East / South Asia: 85 destinations
  - North & Central America: 51 destinations
  - Sub-Saharan Africa & Island Nations: 35 destinations
  - Middle East & North Africa: 34 destinations
  - South America: 26 destinations
  - Oceania: 20 destinations
* **Cost Range:** ₹2,700/day to ₹28,000/day (Mean: ₹9,428.60/day).
* **Original Seed Preservation:** Original 5 seed destinations (IDs 1–5: Mysuru, Kochi, Jaipur, Udaipur, Goa) were preserved intact.

### 2.2 Phase D2: Master Attractions Dataset
* **Target Table:** `attractions`
* **Total Records:** 2,517
* **Coverage:** 500 / 500 Destinations (100.0%)
* **Density:** 5.03 attractions per destination (Min: 5, Max: 6).
* **Categories (19 Standardized Types):** `viewpoint`, `nature`, `cultural`, `museum`, `heritage`, `religious`, `adventure`, `palace`, `temple`, `beach`, `market`, `park`, `historic_monument`, `botanical_garden`, `wildlife`, `waterfall`, `island`, `lake`, `historic_bridge`.
* **Pricing:** 1,079 Free (42.87%), 1,438 Paid (57.13%). Mean entry fee: ₹873.34.
* **Ratings:** Mean 4.73 / 5.0 (Range: 4.2 to 5.0).

### 2.3 Phase D3: Master Accommodations Dataset
* **Target Table:** `hotels`
* **Total Records:** 6,000
* **Coverage:** 500 / 500 Destinations (100.0%)
* **Density:** Exactly 12 hotels per destination.
* **Tiers & Pricing:**
  - Budget Hostels / Guesthouses: ₹550 – ₹2,500/night
  - Moderate 3-Star / Boutique: ₹2,500 – ₹7,500/night
  - Luxury 4-Star / 5-Star: ₹7,500 – ₹25,000/night
  - Heritage Palaces / Ultra-Resorts: Up to ₹115,000/night
* **Ratings:** Mean 4.36 / 5.0 (Range: 3.8 to 5.0).

### 2.4 Phase D4: Master Restaurants Dataset
* **Target Table:** `restaurants`
* **Total Records:** 6,000
* **Coverage:** 500 / 500 Destinations (100.0%)
* **Density:** Exactly 12 restaurants per destination.
* **Cuisines:** 254 unique culinary specialties represented.
* **Pricing:** ₹100/person (street food) to ₹32,000/person (fine Michelin dining). Mean: ₹2,095.32/person.
* **Ratings:** Mean 4.49 / 5.0 (Range: 4.1 to 5.0).

### 2.5 Phase D5: Master Transport Options Dataset
* **Target Table:** `transport_options`
* **Total Records:** 6,000
* **Coverage:** 500 / 500 Destinations (100.0%)
* **Density:** Exactly 12 transport options per destination.
* **Modes (14 Transit Types):** High-speed rail, express train, direct flight, regional air, sleeper bus, AC express coach, private taxi, airport express metro, ferry, speed boat, local auto rickshaw, shared minivan, tramway, self-drive rental.
* **Pricing:** ₹20.00 (local metro) to ₹16,830.00 (first-class flight). Mean: ₹2,390.97.

---

## 3. Data Integrity & Foreign Key Guarantees

* **Zero Orphan Records:** Every hotel, restaurant, attraction, and transport option is explicitly linked to a valid `destination_id` matching `destinations.id`.
* **Zero Duplicate Names per Destination:** Enforced at DBMS level by composite unique constraints `(destination_id, name)`.
* **Nonnegative Numerical Check Constraints:** Enforced via `CHECK (price >= 0)` on all cost columns.
