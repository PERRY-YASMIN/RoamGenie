# RoamGenie D5 Master Transport Options Dataset Report

**Phase:** D5 — Transport Master Dataset  
**Date:** 2026-08-20  
**Target Table:** `transport_options`  
**Total Records:** 6,000  
**Destination Records Covered:** 500 / 500 (100.0%)  

---

## 1. Dataset Overview

The RoamGenie Phase D5 Transport Master Dataset populates a comprehensive, authentic, and geographically intelligent catalog of **6,000 transport options** across all 500 destinations worldwide. Every record maps directly to a verified `destination_id` in PostgreSQL, enabling multi-modal route planning, intercity transit selection, local intra-city transit navigation, and budget-optimized itinerary generation from budget public buses to first-class high-speed rail and flights.

```
+------------------------------------+----------------------------------+
| Attribute                          | Value                            |
+------------------------------------+----------------------------------+
| Total Transport Records            | 6,000                            |
| Existing Preserved Records         | 8 (Destinations 1 to 5)          |
| Newly Seeded Records               | 5,992                            |
| Total Destinations Represented     | 500                              |
| Countries Represented              | 93                               |
| Transports per Destination         | 12.00 (Min: 12, Max: 12)         |
| Unique Transport Modes             | 14                               |
| Minimum Cost                       | ₹20.00                           |
| Maximum Cost                       | ₹16,830.00                       |
| Average Cost                       | ₹2,390.97                        |
| Median Cost                        | ₹960.00                          |
| Minimum Duration                   | 10 minutes                       |
| Maximum Duration                   | 720 minutes                      |
| Average Duration                   | 203.77 minutes                   |
| Median Duration                    | 94 minutes                       |
+------------------------------------+----------------------------------+
```

---

## 2. Transport Modes Breakdown & Geographic Realism

The dataset features 14 distinct modes of transportation carefully assigned based on geographical attributes (coastal waters, mountain topology, metropolitan infrastructure, and regional cultures):

| Transport Mode | Record Count | % of Catalog | Scope & Typical Use Cases |
|----------------|--------------|--------------|---------------------------|
| `bus` | 838 | 13.97% | Intercity express coaches (Volvo/FlixBus), regional buses, municipal city fleets |
| `train` | 758 | 12.63% | High-speed rail (Shinkansen, TGV, Vande Bharat, Eurostar), express & sleeper trains |
| `flight` | 742 | 12.37% | Domestic & regional flights connecting major gateway hubs to destination airports |
| `shuttle` | 585 | 9.75% | Airport express shuttles, heritage monument jeeps, tourist transfers |
| `taxi` | 501 | 8.35% | Official airport & city metered taxis, black cabs, yellow cabs |
| `private-transfer` | 499 | 8.32% | Dedicated private chauffeur sedans, luxury Mercedes transfers, VIP SUVs |
| `ride-hailing` | 499 | 8.32% | App-based ride-hailing services (Uber, Grab, Ola, Careem, Bolt, Lyft) |
| `car-rental` | 496 | 8.27% | Full-day self-drive car rentals (Hertz, Avis, Zoomcar, Sixt, Europcar) |
| `bike-rental` | 496 | 8.27% | City bicycle share, e-bike stations, beach cruiser & motorcycle rentals |
| `tram` | 192 | 3.20% | Historic and modern light rail tram systems in major urban centers |
| `auto-rickshaw` | 167 | 2.78% | Authentic local auto-rickshaws, e-rickshaws, and tuk-tuks (South/SE Asia & Middle East) |
| `metro` | 162 | 2.70% | High-capacity underground subway and elevated metro transit networks |
| `ferry` | 49 | 0.82% | Coastal catamarans, island speedboats, river bumboats, and canal water taxis |
| `cable-car` | 16 | 0.27% | High-altitude ropeways, aerial tramways, and alpine funiculars in mountain regions |
| **Total** | **6,000** | **100.00%** | |

---

## 3. Cost Tiers & Budget Optimization

The dataset spans 5 structured transport cost tiers calibrated to INR benchmarks and destination cost-of-living indices:

| Tier | Cost Range (INR ₹) | Record Count | % of Catalog | Typical Mobility Formats |
|------|--------------------|--------------|--------------|--------------------------|
| **Budget** | < ₹400 | 1,518 | 25.30% | Municipal buses, metro tokens, public river ferries, shared autos, city bike shares |
| **Economy** | ₹400 – ₹1,200 | 1,809 | 30.15% | Standard taxis, auto-rickshaws, express airport shuttles, sleeper trains, scooter rentals |
| **Mid-Range** | ₹1,200 – ₹3,500 | 1,444 | 24.07% | AC express rail (Shatabdi/Vande Bharat), intercity AC coaches, standard self-drive cars |
| **Premium** | ₹3,500 – ₹9,000 | 785 | 13.08% | High-speed bullet trains (TGV/Shinkansen/Eurostar), economy domestic flights, SUV transfers |
| **Luxury** | > ₹9,000 | 444 | 7.40% | Business class flights, private Mercedes-Maybach chauffeurs, private yacht/boat transfers |
| **Total** | | **6,000** | **100.00%** | |

---

## 4. Duration Distribution

Durations represent realistic journey lengths measured in minutes:

- **Short Local Trips (< 45 min):** 2,243 options (37.38%) — Metro, local buses, auto-rickshaws, city cabs, cable cars.
- **Airport / Medium Connections (45 – 120 min):** 1,040 options (17.33%) — Airport express trains, short flights, airport shuttles, ferries.
- **Regional Intercity Trips (120 – 360 min):** 1,393 options (23.22%) — High-speed rail, intercity coaches, scenic drives.
- **Long-Distance / Daily Rentals (360+ min):** 1,324 options (22.07%) — Overnight express trains, long-distance buses, full-day car/bike rentals.

---

## 5. Destination-Aware Geographic Logic

1. **Coastal & Island Destinations (e.g. Venice, Maldives, Bali, Goa, Kochi, Santorini):**
   - Populated with water-based options including high-speed electric passenger ferries (Kochi Water Metro), river bumboats, and island catamarans.
2. **Mountain & Alpine Destinations (e.g. Zermatt, Manali, Shimla, Queenstown, Banff, Gulmarg):**
   - Populated with aerial tramways, scenic ropeways, mountain funiculars, and 4x4 alpine jeeps.
3. **Metropolitan Cities (e.g. Tokyo, London, Paris, New York, Singapore, Delhi):**
   - Populated with high-frequency metro lines, suburban rail, light rail trams, and rapid airport links.
4. **Cultural & Heritage Regions (e.g. Jaipur, Udaipur, Varanasi, Chiang Mai, Cairo):**
   - Populated with heritage auto-rickshaw guilds, tourist shuttles, and royal chauffeur sedans.

---

## 6. Deterministic Generation & Schema Integrity

- **Deterministic Seeding:** Generated using `hashlib.sha256(f"roamgenie_transport_{dest_id}_{city}_{country}_{RANDOM_SEED}")` ensuring 100% reproducible results across runs.
- **Preserved Records:** The 8 initial records in `001_seed.sql` for Mysuru, Kochi, Jaipur, Udaipur, and Goa are preserved intact.
- **Schema Compliance:** Adheres strictly to the PostgreSQL `transport_options` schema:
  - `origin`: VARCHAR(100) NOT NULL
  - `destination_id`: BIGINT REFERENCES `destinations(id)` ON DELETE CASCADE
  - `mode`: VARCHAR(40) NOT NULL
  - `provider`: VARCHAR(100) NULL
  - `estimated_cost`: NUMERIC(12, 2) NOT NULL (Check: >= 0)
  - `duration_minutes`: INTEGER NULL (Check: > 0)
