# RoamGenie D2 Master Attractions Dataset Report

**Phase:** D2 — Attraction Master Dataset  
**Date:** 2026-08-20  
**Target Table:** `attractions`  
**Total Records:** 2,517  
**Destination Records Covered:** 500 / 500 (100.0%)  

---

## 1. Dataset Overview

The RoamGenie Phase D2 Attraction Master Dataset establishes a rich, geographically diverse catalog of 2,517 authentic attractions across 500 destinations worldwide. Every record maps directly to a verified `destination_id` in PostgreSQL, providing comprehensive coverage for itinerary planning, AI travel generation, activity filtering, and budget calculations.

```
+------------------------------------+----------------------------------+
| Attribute                          | Value                            |
+------------------------------------+----------------------------------+
| Total Records                      | 2,517                            |
| Existing Preserved Records         | 3 (Destination 1: Mysuru)        |
| Newly Seeded Records               | 2,514                            |
| Total Destinations Represented     | 500                              |
| Countries Represented              | 93                               |
| Average Attractions / Destination  | 5.03 (Min: 5, Max: 6)            |
| Category Count                     | 19 standardized categories       |
| Rated Attractions                  | 2,517 (100.0%)                   |
| Free Attractions Count             | 1,079 (42.87%)                   |
| Paid Attractions Count             | 1,438 (57.13%)                   |
| Average Entry Fee                  | ₹873.34                          |
| Maximum Entry Fee                  | ₹65,000.00 (Everest Flight / Tour)|
| Minimum Entry Fee                  | ₹0.00                            |
| Average Rating                     | 4.73 / 5.0 (Range: 4.2 – 5.0)    |
+------------------------------------+----------------------------------+
```

---

## 2. Category Distribution

The dataset spans 19 structured travel categories designed for optimal UX filtering and AI recommendations:

| Category | Record Count | % of Catalog | Description / Examples |
|----------|--------------|--------------|------------------------|
| `viewpoint` | 255 | 10.13% | Scenic overlooks, observation decks, sunset points (e.g., Tiger Hill, Top of the Rock) |
| `nature` | 251 | 9.97% | Natural wonders, gorges, caves, geothermal areas, lakes |
| `cultural` | 232 | 9.22% | Historic old towns, cultural districts, squares, performance centers |
| `museum` | 218 | 8.66% | Fine art galleries, world museums, science institutions |
| `heritage` | 182 | 7.23% | UNESCO heritage sites, ancient ruins, archaeological parks |
| `religious` | 159 | 6.32% | Cathedrals, historic mosques, pagodas, shrines, monasteries |
| `adventure` | 152 | 6.04% | Hiking passes, climbing routes, desert safaris, dive sites |
| `wildlife` | 127 | 5.05% | National parks, wildlife reserves, sanctuaries, safaris |
| `temple` | 124 | 4.93% | Historic Hindu, Buddhist, Jain, and Sikh temples |
| `historical` | 113 | 4.49% | War memorials, ancient citadels, historic battlegrounds |
| `beach` | 101 | 4.01% | Iconic coastal shores, promenades, coves |
| `fort` | 96 | 3.81% | Hill forts, medieval castles, coastal fortresses |
| `monument` | 95 | 3.77% | Iconic statues, triumphal arches, clock towers |
| `market` | 88 | 3.50% | Traditional souks, bazaars, floating markets, night markets |
| `architecture` | 77 | 3.06% | World-renowned architectural marvels, modern towers, bridges |
| `palace` | 71 | 2.82% | Royal residences, imperial palaces, havelis |
| `garden` | 71 | 2.82% | Botanical gardens, royal Mughal gardens, landscaped parks |
| `waterfall` | 55 | 2.19% | Cascade falls, tiered waterfalls, canyon drops |
| `park` | 50 | 1.99% | Urban civic parks, historic commons, public promenades |
| **Total** | **2,517** | **100.00%** | |

---

## 3. Pricing & Currency Analysis

Entry fees in the master catalog use the `entry_fee NUMERIC(12,2)` schema, standardized in INR (₹) across domestic and international locations:

- **Free Attractions (`entry_fee = ₹0.00`):** 1,079 attractions (**42.87%**). These comprise public viewpoints, religious shrines, historic quarters, public beaches, and walking promenades.
- **Paid Attractions (`entry_fee > ₹0.00`):** 1,438 attractions (**57.13%**).
- **Entry Fee Distribution:**
  - **₹0.00 (Free):** 1,079 records (42.87%)
  - **₹1.00 – ₹250.00:** 428 records (17.00%)
  - **₹251.00 – ₹750.00:** 395 records (15.69%)
  - **₹751.00 – ₹2,000.00:** 412 records (16.37%)
  - **₹2,001.00 – ₹5,000.00:** 152 records (6.04%)
  - **> ₹5,000.00:** 51 records (2.03%) *(e.g., premium safari permits, guided glacier flights, major theme parks)*
- **Overall Fee Mean:** ₹873.34  
- **Paid Fee Mean:** ₹1,528.65  
- **Overall Fee Median:** ₹100.00  

---

## 4. Rating & Quality Distribution

All 2,517 attraction records feature realistic user ratings constrained to the `NUMERIC(2,1)` schema (range 0.0 – 5.0):

- **Rating Range:** 4.2 to 5.0
- **Rating Mean:** 4.73
- **Rating Breakdown:**
  - **5.0:** 186 records (7.39%)
  - **4.8 – 4.9:** 1,215 records (48.27%)
  - **4.6 – 4.7:** 798 records (31.70%)
  - **4.4 – 4.5:** 254 records (10.09%)
  - **4.2 – 4.3:** 64 records (2.54%)

---

## 5. Destination Coverage Highlights

All 500 live destinations have between 5 and 6 authentic, curated attractions:

### Sample Representation Across Regions:
1. **India (144 Destinations, ~723 Attractions):**
   - *Mysuru*: Mysuru Palace, Chamundi Hill & Temple, Brindavan Gardens, St. Philomena's Cathedral, Mysuru Zoo
   - *Varanasi*: Kashi Vishwanath Temple, Dashashwamedh Ghat Ganga Aarti, Manikarnika Ghat, Sarnath Dhamek Stupa, Ramnagar Fort
   - *Leh*: Pangong Tso Lake, Thiksey Monastery, Khardung La Pass, Nubra Valley Dunes, Leh Palace
   - *Hampi*: Virupaksha Temple, Vijaya Vittala Temple & Stone Chariot, Matanga Hill, Lotus Mahal, Elephant Stables
2. **Europe (105 Destinations, ~528 Attractions):**
   - *Rome, Italy*: Colosseum & Roman Forum, St. Peter's Basilica & Vatican Museums, Trevi Fountain, Pantheon, Piazza Navona
   - *Paris, France*: Eiffel Tower, Louvre Museum, Notre-Dame Cathedral, Sacré-Cœur & Montmartre, Musée d'Orsay
   - *Santorini, Greece*: Oia Sunset Viewpoint, Red Beach & Akrotiri Ruins, Fira to Oia Caldera Trail, Prophet Elias Monastery, Ammoudi Bay
3. **Southeast & East Asia (85 Destinations, ~427 Attractions):**
   - *Kyoto, Japan*: Fushimi Inari Taisha Shrine, Kinkaku-ji (Golden Pavilion), Arashiyama Bamboo Grove, Kiyomizu-dera Temple, Gion Geisha District
   - *Bangkok, Thailand*: Grand Palace & Wat Phra Kaew, Wat Arun (Temple of Dawn), Wat Pho (Reclining Buddha), Chatuchak Weekend Market, Chao Phraya River Cruise
4. **North & Central America (51 Destinations, ~257 Attractions):**
   - *New York City, USA*: Central Park, Statue of Liberty & Ellis Island, Empire State Building & Top of the Rock, Metropolitan Museum of Art (Met), High Line & Hudson Yards
   - *Banff, Canada*: Lake Louise & Moraine Lake, Banff Gondola & Sulphur Mountain, Johnston Canyon Trail, Peyto Lake Viewpoint, Minnewanka Lake
5. **Middle East & Africa (69 Destinations, ~347 Attractions):**
   - *Cairo, Egypt*: Giza Pyramids & Great Sphinx, Egyptian Museum, Khan el-Khalili Bazaar, Citadel of Saladin, Al-Azhar Mosque
   - *Cape Town, South Africa*: Table Mountain Cableway, Cape Point & Cape of Good Hope, Boulders Beach Penguin Colony, Kirstenbosch Botanical Gardens, Robben Island
6. **South America & Oceania (46 Destinations, ~235 Attractions):**
   - *Cusco / Machu Picchu, Peru*: Machu Picchu Sanctuary, Sacsayhuamán Citadel, Plaza de Armas Cusco, Qorikancha Sun Temple, Rainbow Mountain (Vinicunca)
   - *Sydney, Australia*: Sydney Opera House, Sydney Harbour Bridge Climb & Walk, Bondi to Coogee Coastal Walk, Taronga Zoo Sydney, The Rocks Historic District

---

## 6. Storage & Seed Artifacts

The dataset is synchronized across the following files:
- `database/seeds/attractions_master_d2.json` — Complete JSON export of all 2,517 live database records with assigned PostgreSQL primary keys.
- `database/seeds/manifest_d2_attractions.json` — Comprehensive metadata manifest with statistical rollups.
- `scripts/database/seed_attractions_d2.py` — Transactional seeder script.
- `scripts/database/validate_attractions_d2.py` — Database validation script.
- `scripts/database/post_insert_verification_d2.py` — 14-point live audit script.
