import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    """Custom exception raised when an external LLM call fails."""
    pass


class LLMResponse(str):
    """
    Subclass of str providing backward compatibility with existing code that treats
    LLM output as a string, while attaching function_call, text, and raw parts when present.
    """
    function_call: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    raw_parts: List[Dict[str, Any]] = []

    def __new__(
        cls,
        content: str = "",
        function_call: Optional[Dict[str, Any]] = None,
        raw_parts: Optional[List[Dict[str, Any]]] = None,
    ):
        obj = super().__new__(cls, content)
        obj.function_call = function_call
        obj.text = content if content else None
        obj.raw_parts = raw_parts or []
        return obj

    @property
    def has_function_call(self) -> bool:
        return self.function_call is not None


class BaseLLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str,
        timeout_seconds: int = 15,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_config: Optional[Dict[str, Any]] = None,
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Invokes the external LLM and returns raw response string or LLMResponse."""
        pass


def _parse_prompt_facts(prompt: str) -> Dict[str, Any]:
    facts: Dict[str, Any] = {
        "user_query": "",
        "trip_id": None,
        "dest_name": "",
        "origin": "",
        "start_date": "",
        "end_date": "",
        "day_count": 0,
        "traveller_count": 1,
        "total_budget": 0.0,
        "estimated_total": 0.0,
        "remaining_budget": 0.0,
        "deficit": 0.0,
        "allocations": {},
        "itinerary_items": [],
        "packing_items": [],
        "hotels": [],
        "dining": [],
        "attractions": [],
        "weather_summary": "",
        "forecast_lines": [],
    }

    # 1. User query extraction
    for line in prompt.splitlines():
        if line.startswith("USER QUERY:"):
            facts["user_query"] = line[len("USER QUERY:"):].strip()
            break
    if not facts["user_query"]:
        first_line = prompt.strip().splitlines()[0] if prompt.strip() else ""
        if not any(first_line.startswith(h) for h in ("AUTHORIZED TRIP CONTEXT:", "DESTINATION CATALOGUE", "WEATHER FORECAST", "SYSTEM PROMPT", "JSON OUTPUT", "TRIP SPECIFICATION")):
            facts["user_query"] = first_line

    # 2. Trip metadata
    m = re.search(r"- Trip ID:\s*(\d+)", prompt)
    if m:
        facts["trip_id"] = int(m.group(1))

    m = re.search(r"- Destination:\s*([^\n(]+)", prompt)
    if m:
        facts["dest_name"] = m.group(1).strip()

    m = re.search(r"- Origin:\s*([^\n]+)", prompt)
    if m:
        facts["origin"] = m.group(1).strip()

    m = re.search(r"- Dates:\s*(\S+)\s+to\s+(\S+)\s+\((\d+)\s+days?\)", prompt)
    if m:
        facts["start_date"] = m.group(1)
        facts["end_date"] = m.group(2)
        facts["day_count"] = int(m.group(3))

    m = re.search(r"- Travellers:\s*(\d+)", prompt)
    if m:
        facts["traveller_count"] = int(m.group(1))

    m = re.search(r"- Total Budget:\s*₹?([0-9.,]+)", prompt)
    if m:
        facts["total_budget"] = float(m.group(1).replace(",", ""))

    m = re.search(r"- Estimated Total:\s*₹?([0-9.,]+)", prompt)
    if m:
        facts["estimated_total"] = float(m.group(1).replace(",", ""))

    m = re.search(r"- Remaining Budget:\s*₹?([0-9.,-]+)", prompt)
    if m:
        facts["remaining_budget"] = float(m.group(1).replace(",", ""))

    m = re.search(r"Deficit:\s*₹?([0-9.,]+)", prompt)
    if m:
        facts["deficit"] = float(m.group(1).replace(",", ""))

    # 3. Budget Allocations
    in_alloc = False
    for line in prompt.splitlines():
        if "- Budget Allocations:" in line:
            in_alloc = True
            continue
        if in_alloc:
            if line.startswith("- ") and ":" in line and not line.startswith("- Scheduled"):
                parts = line[2:].split(":", 1)
                cat = parts[0].strip()
                amt_str = re.sub(r"[^\d.]", "", parts[1])
                if amt_str:
                    facts["allocations"][cat] = float(amt_str)
            else:
                if line.startswith("- Scheduled") or line.startswith("DESTINATION") or not line.strip():
                    in_alloc = False

    # 4. Itinerary Preview
    in_itin = False
    for line in prompt.splitlines():
        if "- Scheduled Itinerary Preview:" in line:
            in_itin = True
            continue
        if in_itin:
            if line.startswith("- Day "):
                m = re.match(r"- Day (\d+)\s*\[Item #(\d+),\s*([^\]]+)\]:\s*(.+?)\s*\(₹([0-9.,]+)\)", line)
                if m:
                    facts["itinerary_items"].append({
                        "day": int(m.group(1)),
                        "item_id": int(m.group(2)),
                        "category": m.group(3).strip(),
                        "title": m.group(4).strip(),
                        "cost": float(m.group(5).replace(",", "")),
                    })
            elif line.startswith("- Current Packing Checklist:") or line.startswith("DESTINATION CATALOGUE") or line.startswith("WEATHER"):
                in_itin = False

    # 5. Packing Checklist
    in_pack = False
    for line in prompt.splitlines():
        if "- Current Packing Checklist:" in line:
            in_pack = True
            continue
        if in_pack:
            if line.startswith("- ["):
                facts["packing_items"].append(line[2:].strip())
            elif line.startswith("DESTINATION CATALOGUE") or line.startswith("WEATHER") or not line.strip():
                in_pack = False

    # 6. Catalogue Facts
    m = re.search(r"- Hotels:\s*([^\n]+)", prompt)
    if m:
        facts["hotels"] = [h.strip() for h in m.group(1).split(",") if h.strip()]

    m = re.search(r"- Dining:\s*([^\n]+)", prompt)
    if m:
        facts["dining"] = [d.strip() for d in m.group(1).split(",") if d.strip()]

    m = re.search(r"- Attractions:\s*([^\n]+)", prompt)
    if m:
        facts["attractions"] = [a.strip() for a in m.group(1).split(",") if a.strip()]

    # 7. Weather
    in_weather = False
    for line in prompt.splitlines():
        if "WEATHER FORECAST CONTEXT:" in line:
            in_weather = True
            continue
        if in_weather:
            if line.startswith("Current:"):
                facts["weather_summary"] = line.split("Current:", 1)[1].strip()
            elif line.startswith("- "):
                facts["forecast_lines"].append(line[2:].strip())
            elif line.startswith("JSON OUTPUT FORMAT:"):
                in_weather = False

    return facts


def answer_general_travel_query(
    q_clean: str,
    facts: Optional[Dict[str, Any]] = None,
    dest_name: Optional[str] = None,
) -> Tuple[str, List[str]]:
    """
    Universal travel intelligence engine providing expert ChatGPT-grade travel advice
    for open-ended inquiries, weekend escapes, solo travel, budget hacks, Tatkal/flight
    booking tricks, destination guides, and packing formulas.
    """
    dest_text = f" for **{dest_name}**" if dest_name else ""

    # 1. Weekend Escapes & Road Trips
    if any(k in q_clean for k in ("weekend", "getaway", "road trip", "short trip", "quick trip", "2 day trip", "short escape")) or any(
        k in q_clean for k in ("from delhi", "near delhi", "from mumbai", "near mumbai", "from bangalore", "near bangalore", "from kolkata", "near kolkata", "from pune", "near pune", "from hyderabad", "near hyderabad")
    ):
        if "delhi" in q_clean:
            reply = (
                "Here are the premier weekend getaways from **Delhi** (within 3 to 6 hours):\n\n"
                "1. **Rishikesh & Shivpuri (4.5–5 hrs):** World-class white-water rafting, serene Ganga Aarti at Parmarth Niketan, peaceful Beatles Ashram strolls, and riverside boutique camps.\n"
                "2. **Jaipur (4 hrs via Delhi-Mumbai Expressway):** The Pink City's majestic Amber Fort at sunrise, sunset panoramas from Nahargarh, and authentic pyaaz kachoris & Ghewar at LMB.\n"
                "3. **Agra & Fatehpur Sikri (3 hrs via Yamuna Expressway):** Sunrise viewing of the Taj Mahal without crowds, Mehtab Bagh gardens across the Yamuna, and imperial red sandstone architecture.\n"
                "4. **Neemrana & Lansdowne (2.5–5 hrs):** Zip-line over the 15th-century Neemrana Fort Palace, or escape into the quiet, pristine pine ridges of Lansdowne for cool mountain air.\n\n"
                "**Pro-Tip:** Depart by 5:30 AM on Saturday to beat Delhi's exit toll gridlock, giving you a full leisurely afternoon at your destination!"
            )
            actions = ["Plan Jaipur Trip", "Rishikesh Rafting Guide", "Tatkal Booking Hacks"]
        elif "mumbai" in q_clean or "pune" in q_clean:
            reply = (
                "Here are the best weekend escapes from **Mumbai & Pune**:\n\n"
                "1. **Alibaug (1 hr via Mandwa Ro-Ro Ferry):** Scenic coastal cruises, watersports at Nagaon beach, historic Kolaba Sea Fort, and fresh Konkani seafood thalis.\n"
                "2. **Lonavala & Khandala (1.5–2 hrs via Mumbai-Pune Expressway):** Tiger's Point vistas, Bhushi Dam cascades during monsoon, ancient Karla & Bhaja rock-cut caves, and warm chikki.\n"
                "3. **Mahabaleshwar & Panchgani (4–4.5 hrs):** Table Land plateau strolls, fresh strawberry cream at Mapro Garden, Arthur's Seat cliff views, and cool misty valley breezes.\n"
                "4. **Goa (8–9 hr coastal drive or 45-min flight / Vande Bharat):** Unwind along South Goa's tranquil shores or explore North Goa's energetic beach shacks and night markets.\n\n"
                "**Pro-Tip:** Take the morning Ro-Ro car ferry from Bhaucha Dhakka (Ferry Wharf) to Mandwa to bypass the heavy Panvel highway traffic!"
            )
            actions = ["Plan Goa Itinerary", "Alibaug Weekend Guide", "Solo Travel Safety"]
        elif "bangalore" in q_clean or "bengaluru" in q_clean:
            reply = (
                "Here are top weekend getaways from **Bangalore**:\n\n"
                "1. **Coorg / Kodagu (5 hrs):** Emerald coffee plantations, Abbey Falls, Raja's Seat sunset, and fragrant spice-infused Kodava pork and akki roti.\n"
                "2. **Mysore (2 hrs via Expressway or Vande Bharat):** The illuminated royal Mysore Palace, Chamundi Hills, vibrant Devaraja silk and flower markets, and melt-in-mouth Mysore Pak.\n"
                "3. **Ooty & Coonoor (6 hrs):** Heritage Nilgiri Mountain Toy Train, fragrant tea factory trails, Sim's Park, and misty eucalyptus ridges.\n"
                "4. **Wayanad (5.5 hrs):** Edakkal prehistoric petroglyphs, bamboo rafting at Kuruva Island, and misty treehouse stays.\n"
                "5. **Hampi (6 hrs):** Surreal boulder terrain, UNESCO World Heritage Vijayanagara ruins, and relaxing coracle rides on the Tungabhadra River.\n\n"
                "**Pro-Tip:** Take the early morning Mysore Vande Bharat (leaves 5:45 AM) to enjoy a royal morning palace tour and arrive in Coorg or Kabini before lunch!"
            )
            actions = ["Plan Coorg Getaway", "Explore Hampi Ruins", "Budget Travel Hacks"]
        elif "kolkata" in q_clean:
            reply = (
                "Here are the top weekend escapes from **Kolkata**:\n\n"
                "1. **Sundarbans (2.5 hrs drive + river boat safari):** World's largest mangrove delta, Royal Bengal Tiger tracking, watchtowers at Sajnekhali, and quiet river boat stays.\n"
                "2. **Darjeeling & Kurseong (Overnight train or 1 hr flight to Bagdogra):** Tiger Hill sunrise over Mount Kanchenjunga, heritage Himalayan Toy Train, and high-grown Darjeeling teas at Glenary's.\n"
                "3. **Shantiniketan (3 hrs via train / highway):** Rabindranath Tagore's Visva Bharati ashram, exquisite terracotta temples, Sonajhurir Haat Saturday handicrafts, and soulful Baul folk music.\n"
                "4. **Mandarmani & Tajpur (3.5 hrs):** Wide drive-in beaches, red ghost crabs, tranquil sea breezes, and fresh coastal fish curry.\n\n"
                "**Pro-Tip:** The Saturday handicrafts bazaar at Sonajhuri (Shantiniketan) under the sal trees is one of the most vibrant cultural experiences in eastern India!"
            )
            actions = ["Plan Darjeeling Trip", "Explore Sundarbans", "Tatkal Train Tricks"]
        else:
            reply = (
                "**The Golden Formula for a Flawless Weekend Getaway:**\n\n"
                "1. **Transit Cap:** Keep travel time under 4 to 5 hours each way so you don't exhaust your energy on transit.\n"
                "2. **The 'One-Hero-Anchor' Rule:** Choose only 1 signature morning activity per day (e.g., a sunrise viewpoint, fort hike, or water rafting) rather than overbooking.\n"
                "3. **Unstructured Afternoons:** Leave late afternoons open for spontaneous local cafe hopping, market browsing, and watching the sunset.\n"
                "4. **Early Exit Departure:** Start your drive or train by 5:30 AM Saturday to dodge suburban traffic bottlenecks and gain half a day at your destination!"
            )
            actions = ["Weekend Destinations", "Budget Hacks", "Tatkal Booking Tricks"]
        return reply, actions

    # 2. Solo Travel Tips & Safety
    if any(k in q_clean for k in ("solo", "travel alone", "traveling alone", "travelling alone", "by myself", "solo safety", "solo female")):
        reply = (
            "Solo travel is one of the most empowering adventures you can take! Here is your essential playbook for safe, seamless solo exploration:\n\n"
            "1. **Where to Stay:** Book reputable social backpacker hostels (e.g., Zostel, The Hosteller) or vetted heritage homestays. Common rooms, rooftop cafes, and community walks make it effortless to meet companions without any pressure.\n"
            "2. **The 3-Point Safety Rule:**\n"
            "   - **Live Location:** Share an ongoing WhatsApp or Google Maps location with 1 trusted family member or friend.\n"
            "   - **Arrive in Daylight:** Always book transit that arrives at your destination before sunset so you can orient yourself and navigate safely.\n"
            "   - **Digital Redundancy:** Store encrypted cloud copies of your passport/Aadhaar and flight/hotel bookings on Google Drive, and keep a backup credit/debit card and ₹2,000 emergency cash separate from your primary wallet.\n"
            "3. **Socializing Made Simple:** Sign up for free walking tours, morning yoga sessions, or group food crawls—it's the quickest way to make friends on day one!\n"
            "4. **Trust Your Instincts:** If a taxi driver, venue, or situation feels off, leave without hesitation. A confident posture and polite assertiveness go a long way."
        )
        actions = ["Packing Essentials", "Budget Travel Hacks", "Suggest Solo Destinations"]
        return reply, actions

    # 3. Budget Hacks & Saving Money
    if any(k in q_clean for k in ("save money", "cheapest way", "cheap travel", "shoestring", "budget hack", "budget tips", "cut costs", "low budget", "cheap way", "travel cheap")):
        reply = (
            "Here are the 4 highest-leverage insider hacks to stretch your travel budget without compromising comfort:\n\n"
            "1. **Travel During the Shoulder Season:** Visiting destinations in the shoulder months (e.g., Sep–Oct or Feb–March) unlocks 40% to 60% discounts on premium hotels and lets you enjoy monuments free of tourist crowds.\n"
            "2. **Transit Double-Duty (Overnight Travel):** Take overnight AC sleeper trains (like 3rd AC) or Volvo sleeper buses. You cover long distances while saving an entire night's hotel tariff!\n"
            "3. **Eat 2 Blocks Away from Tourist Landmarks:** Tourist-facing restaurants right next to monuments charge 3x prices for mediocre food. Walk two blocks into residential neighborhoods to find bustling local joints serving fresher, authentic regional meals at a fraction of the cost.\n"
            "4. **Split Transit & Use Metros:** Skip expensive prepaid airport taxis by using city metro lines or app-based shared rides. For regional exploration, renting a scooter for ₹350–₹500/day provides total freedom on a shoestring budget."
        )
        actions = ["Explore Free Attractions", "Tatkal Train Tricks", "Packing Checklist Guide"]
        return reply, actions

    # 4. Tatkal & Train Booking Tricks
    if any(k in q_clean for k in ("tatkal", "irctc", "train ticket", "train booking", "how to book train", "railway ticket", "railway")):
        reply = (
            "Mastering IRCTC Tatkal booking comes down to split-second speed and preparation. Here is the pro strategy:\n\n"
            "1. **Clock Timings:**\n"
            "   - **AC Classes (1A, 2A, 3A, 3E, CC):** Opens strictly at **10:00 AM IST**.\n"
            "   - **Non-AC / Sleeper (SL):** Opens strictly at **11:00 AM IST**.\n"
            "   - Tatkal bookings open 1 day prior to the train's departure date from its originating station.\n"
            "2. **The Master Passenger List Secret:** Log into IRCTC the night before and add your co-travellers under *My Profile -> Master Passenger List*. During Tatkal rush, you can select and autofill all passenger names with 1 click instead of typing names, ages, and berth preferences!\n"
            "3. **Payment Speed:** Choose **UPI (BHIM / Google Pay / PhonePe)** or the pre-funded **IRCTC e-Wallet**. UPI sends an instant notification to your phone that you approve in 3 seconds, avoiding credit card OTP delays that cause tickets to sell out.\n"
            "4. **Browser Hygiene:** Log into IRCTC at 9:58 AM (for AC) or 10:58 AM (for SL). Don't refresh the page while waiting; click Search right as the system clock strikes 10:00:00."
        )
        actions = ["Flight Booking Hacks", "Weekend Escapes", "Plan a New Trip"]
        return reply, actions

    # 5. Flight Booking Hacks & Cheap Airfare
    if any(k in q_clean for k in ("flight", "cheap flight", "airfare", "book flight", "plane ticket", "airline ticket", "skyscanner", "cheap tickets", "google flights")):
        reply = (
            "Here is how frequent flyers find the best airfares:\n\n"
            "1. **The Sweet Spot Booking Window:** Book domestic flights **6 to 8 weeks** in advance. For international routes, the optimal window is **2 to 3 months** prior to departure.\n"
            "2. **Fly Mid-Week:** Tuesday and Wednesday departures are consistently 15% to 25% cheaper than peak Friday evening and Sunday flights. Early morning flights (departing 5:00–7:00 AM) are also less prone to cascading air-traffic delays.\n"
            "3. **Use Date Grid Tools:** Use Google Flights' 'Date Grid' or Skyscanner's 'Whole Month' view to spot hidden low-fare dates. Always search in private/incognito mode to avoid cookie-driven algorithmic surge pricing.\n"
            "4. **The 7kg Carry-On Freedom:** If traveling on low-cost carriers (IndiGo, AirAsia, Akasa), travel with a 35L–40L cabin backpack. You bypass checked baggage queues and save ₹1,500–₹3,000 on excess baggage fees."
        )
        actions = ["Packing Checklist Guide", "Weekend Escapes", "Tatkal Train Tricks"]
        return reply, actions

    # 6. Packing Formulas & Capsule Wardrobe
    if any(k in q_clean for k in ("pack", "packing", "what to bring", "capsule wardrobe", "luggage", "carry-on", "5-4-3-2-1", "what should i pack")):
        reply = (
            "Here is the gold-standard **5-4-3-2-1 Capsule Packing Formula** designed for a 5 to 7-day trip without luggage bloat:\n\n"
            "- **5 Tops:** Mix of breathable cotton/linen t-shirts and casual shirts in neutral, inter-matching tones.\n"
            "- **4 Bottoms:** 2 pairs of lightweight travel pants/chinos, 1 pair of comfortable jeans, and 1 pair of relaxed shorts/culottes.\n"
            "- **3 Shoes & Accessories:** 1 pair of broken-in walking sneakers, 1 pair of versatile slip-ons/sandals, plus UV sunglasses and a sun hat.\n"
            "- **2 Weather Layers:** 1 light cardigan/windcheater and 1 versatile fleece or light jacket for chilly evenings or flight cabins.\n"
            "- **1 Special Outfit:** A dressier dinner ensemble or traditional outfit for heritage/spiritual landmarks.\n\n"
            "**Packing Essentials Checklist:**\n"
            "✓ Compression packing cubes (saves up to 40% volume and keeps categories organized)\n"
            "✓ 10,000–20,000 mAh power bank (must always be kept in cabin carry-on, never in check-in)\n"
            "✓ Mini medical kit (ORS electrolyte sachets, paracetamol, antacids, anti-histamines, motion sickness pills, Band-Aids)\n"
            "✓ Multi-port fast charger with universal adapter plugs"
        )
        actions = ["View Packing Checklist", "Weather Forecast", "Plan a New Trip"]
        return reply, actions

    # 7. Goa
    if any(k in q_clean for k in ("goa", "north goa", "south goa", "calangute", "palolem", "panaji", "beach trip")):
        reply = (
            "Goa is all about matching your vibe to the right coast:\n\n"
            "1. **North Goa (Energy & Buzz):** Perfect for lively beach shacks, watersports (Baga, Calangute), flea markets (Anjuna, Arpora), and vibrant music venues and nightlife (Vagator, Morjim, Assagao's upscale dining).\n"
            "2. **South Goa (Serenity & Heritage):** Pristine white sands (Palolem, Agonda, Benaulim), Portuguese colonial heritage villas (Chandor, Loutolim), aromatic spice plantations, and tranquil beachfront reading.\n"
            "3. **Panaji & Fontainhas:** Don't miss strolling through the Latin Quarter of Fontainhas with its vivid yellow and indigo heritage homes, artisan bakeries, and traditional Goan Portuguese cafes.\n\n"
            "**Insider Tip:** Rent a scooter (₹350–₹500/day) to cruise the scenic coastal roads, and indulge in a local Goan fish curry thali with fresh poee bread!"
        )
        actions = ["Plan Goa Itinerary", "Explore Beach Stays", "Budget Hacks"]
        return reply, actions

    # 8. Kerala
    if any(k in q_clean for k in ("kerala", "munnar", "alleppey", "kochi", "varkala", "god's own country")):
        reply = (
            "Kerala is a magical blend of heritage, misty mountains, and tranquil waterways. Here is the classic circuit:\n\n"
            "1. **Fort Kochi (1–2 days):** Portuguese and Dutch heritage alleys, vibrant contemporary art cafes, Kathakali performances, and sunset by the iconic Chinese fishing nets.\n"
            "2. **Munnar (2–3 days):** Rolling emerald tea estates, misty mountain viewpoints at Top Station, and wildlife spotting at Eravikulam National Park.\n"
            "3. **Alleppey / Kumarakom (1–2 days):** Overnight traditional Kettuvallam houseboat cruise along peaceful backwater canals with authentic Karimeen Pollichathu (pearl spot fish).\n"
            "4. **Varkala (2 days):** Dramatic red laterite cliffs towering over the Arabian Sea, bohemian clifftop cafes, and serene yoga retreats.\n\n"
            "**Best Season:** October to March offers ideal tropical weather; June to August brings breathtaking monsoon lushness with Ayurvedic rejuvenation retreats."
        )
        actions = ["Plan Kerala Trip", "Packing Checklist Guide", "Budget Travel Hacks"]
        return reply, actions

    # 9. Rajasthan
    if any(k in q_clean for k in ("rajasthan", "jaipur", "udaipur", "jodhpur", "jaisalmer", "forts", "palace")):
        reply = (
            "Rajasthan offers an unmatched tapestry of royal grandeur, desert horizons, and culinary feasts:\n\n"
            "1. **Jaipur (The Pink City):** Explore the grand courtyards of Amber Fort, the intricate facade of Hawa Mahal, Jantar Mantar observatory, and savor piping hot pyaaz kachoris at Rawat.\n"
            "2. **Udaipur (The City of Lakes):** Romantic sunset boat rides on Lake Pichola, the opulent City Palace museum, and fine rooftop dining overlooking the illuminated Jag Mandir.\n"
            "3. **Jodhpur (The Blue City):** The towering Mehrangarh Fort rising above blue-washed houses, Umaid Bhawan Palace, and spiced Makhaniya Lassi at Clock Tower.\n"
            "4. **Jaisalmer (The Golden City):** Living sandstone fort, intricate Jain temples, and camping under star-studded skies in the Sam Sand Dunes.\n\n"
            "**Best Season:** October through March provides crisp, sunny days and cool desert evenings."
        )
        actions = ["Plan Rajasthan Trip", "Heritage Hotel Tips", "What to Pack"]
        return reply, actions

    # 10. Mountain Retreats & Himalayas
    if any(k in q_clean for k in ("himachal", "manali", "kasol", "rishikesh", "ladakh", "spiti", "kashmir", "uttarakhand", "mountain", "hills", "trek")):
        reply = (
            "The Himalayas offer unforgettable vistas and high-altitude magic. Here are top recommendations:\n\n"
            "1. **Himachal Pradesh:** Explore Manali for Solang adventures, Kasol and Tirthan Valley for peaceful pine forests and river cafes, or Dharamshala/McLeodganj for Tibetan culture and mountain monasteries.\n"
            "2. **Uttarakhand:** Head to Rishikesh for yoga and rafting, Mussoorie/Dhanaulti for quiet ridge walks, or Auli for snow skiing and panoramic views of Nanda Devi.\n"
            "3. **Ladakh & Spiti (High Altitude Desert):** Dramatic mountain passes (Khardung La), sapphire blue Pangong Lake, and centuries-old Tibetan Buddhist monasteries.\n\n"
            "**High-Altitude Safety Rule:** When landing in Leh or reaching elevations above 10,000 ft, rest completely for the first 36–48 hours, drink 3–4 liters of water daily, and avoid physical exertion to acclimatize smoothly."
        )
        actions = ["Plan Mountain Journey", "Packing for Cold Weather", "Check Weather Forecast"]
        return reply, actions

    # 11. Northeast India & Agartala
    if any(k in q_clean for k in ("agartala", "tripura", "meghalaya", "shillong", "cherrapunji", "sikkim", "kaziranga", "northeast")):
        reply = (
            "Northeast India is an enchanted realm of living root bridges, royal water palaces, and pristine cloudscapes:\n\n"
            "1. **Tripura & Agartala:** The gleaming white Ujjayanta Palace, the ethereal Neermahal Water Palace floating in Rudrasagar Lake, and the ancient rock carvings of Unakoti.\n"
            "2. **Meghalaya (Abode of Clouds):** The living double-decker root bridges of Cherrapunji/Nongriat, the crystal-clear waters of the Umngot River in Dawki, and clean tribal hamlets like Mawlynnong.\n"
            "3. **Sikkim:** Breathtaking views of Mount Kanchenjunga from Pelling, sacred Tsomgo Lake, and tranquil Buddhist monasteries in Gangtok.\n"
            "4. **Assam:** One-horned Indian rhinos in Kaziranga National Park and lush rolling tea gardens along the Brahmaputra River."
        )
        actions = ["Explore Northeast Sights", "Check Weather Forecast", "Packing Tips"]
        return reply, actions

    # 12. International Destinations
    if any(k in q_clean for k in ("japan", "bali", "dubai", "thailand", "vietnam", "europe", "paris", "london", "singapore", "international trip", "international")):
        if "japan" in q_clean:
            reply = (
                "**Essential Guide for Visiting Japan:**\n\n"
                "1. **Best Time to Visit:** Spring (late March to mid-April) for cherry blossoms, or autumn (November) for blazing crimson maple foliage.\n"
                "2. **Transit & Logistics:** Get an IC transit card (Suica or Pasmo) for tap-and-go convenience on Tokyo subways and buses. For city-hopping between Tokyo, Kyoto, and Osaka, ride the world-class Shinkansen bullet train.\n"
                "3. **Food Culture:** Slurp steaming bowls of authentic tonkotsu ramen at local counter shops, experience lively izakaya dining, and pick up surprisingly gourmet onigiri at 7-Eleven or Lawson.\n"
                "4. **Key Etiquette:** Speak quietly on trains, avoid tipping (it's considered awkward or rude), and carry cash as smaller ramen shops still rely on ticket vending machines."
            )
            actions = ["Japan Packing Tips", "Forex Card Hacks", "Plan New Trip"]
        elif "bali" in q_clean:
            reply = (
                "**Essential Guide for Visiting Bali:**\n\n"
                "1. **Regions:** Ubud for cultural retreats, emerald rice terraces, and yoga sanctuaries; Seminyak and Canggu for beachfront clubs, surf schools, and chic cafes; Uluwatu for dramatic cliffside temples and Kecak fire dances.\n"
                "2. **Day Excursions:** Take a fast boat to Nusa Penida for Kelingking 'T-Rex' Beach and snorkel with manta rays at Manta Point.\n"
                "3. **Logistics:** Download the Grab or Gojek apps for easy food delivery and scooter taxis. Carry an International Driving Permit (IDP) if you plan to rent a scooter."
            )
            actions = ["Bali Packing Tips", "Forex Card Hacks", "Plan New Trip"]
        elif "vietnam" in q_clean:
            reply = (
                "**Essential Guide for Visiting Vietnam:**\n\n"
                "1. **Top Highlights:** Hanoi's atmospheric Old Quarter, overnight luxury junk boat cruise through Ha Long Bay's limestone karsts, lantern-lit evenings in ancient Hoi An, and vibrant street life in Ho Chi Minh City.\n"
                "2. **Culinary Scene:** Indulge in authentic Pho, crispy Banh Mi from street carts, Bun Cha, and sweet creamy Egg Coffee.\n"
                "3. **Budget Friendly:** Vietnam is remarkably economical—high-end boutique hotels cost under ₹3,500/night, and gourmet street meals rarely exceed ₹150!"
            )
            actions = ["Vietnam Budget Guide", "Packing Checklist", "Plan New Trip"]
        elif "dubai" in q_clean:
            reply = (
                "**Essential Guide for Visiting Dubai:**\n\n"
                "1. **Modern Marvels:** Take the high-speed lift up Burj Khalifa (levels 124/125), visit the futuristic Museum of the Future, and watch the Dubai Fountain show.\n"
                "2. **Heritage & Desert:** Take an Abra wooden boat across Dubai Creek for 1 AED, explore the Gold and Spice Souks in Deira, and book a desert dune-bashing safari with BBQ camp.\n"
                "3. **Best Months:** Visit between November and March for pleasant sunny weather suitable for outdoor promenades and beach clubs."
            )
            actions = ["Dubai Trip Guide", "Packing Checklist", "Plan New Trip"]
        elif "thailand" in q_clean:
            reply = (
                "**Essential Guide for Visiting Thailand:**\n\n"
                "1. **Route:** Bangkok for magnificent temples (Wat Arun, Grand Palace) and Michelin-rated street food; Chiang Mai for mountain elephant sanctuaries and night bazaars; Krabi or Phuket for island-hopping and limestone sea caves.\n"
                "2. **Street Food Culture:** Try Pad Thai, Som Tum (spicy papaya salad), Mango Sticky Rice, and Tom Yum soup at bustling night markets.\n"
                "3. **Etiquette:** Dress respectfully (shoulders and knees covered) when visiting Buddhist temples."
            )
            actions = ["Thailand Island Guide", "Packing Checklist", "Plan New Trip"]
        else:
            reply = (
                "**Top Tips for International Travel:**\n\n"
                "1. **Passport Validity:** Ensure your passport is valid for at least 6 months beyond your scheduled return date and has at least 2 blank pages.\n"
                "2. **Zero-Forex Cards:** Never pay foreign transaction markups! Use cards like Scapia, Niyo, or Fi to save 3.5% on international swipe fees.\n"
                "3. **Digital eSIMs:** Install an international eSIM (such as Airalo or Nomad) prior to boarding so you have instant mobile data when your flight lands.\n"
                "4. **Travel Insurance:** Always secure comprehensive travel medical insurance covering emergency medical expenses and trip cancellations."
            )
            actions = ["International Packing Tips", "Forex & Visa Hacks", "Plan New Trip"]
        return reply, actions

    # 13. Visa, Forex, eSIM & Tech
    if any(k in q_clean for k in ("visa", "forex", "passport", "currency exchange", "sim card", "esim", "insurance")):
        reply = (
            "Here is your essential travel finance and tech checklist:\n\n"
            "1. **Zero-Forex Debit/Credit Cards:** Never exchange currency at airport kiosks where exchange rates carry a punishing 8%–12% spread. Carry a zero-forex card (e.g. Scapia, Niyo Global, or Fi) for live interbank rates without extra transaction fees.\n"
            "2. **Travel eSIMs:** Download and install an eSIM via apps like Airalo or Nomad before you fly. You can switch your data line on upon touchdown and get instant 5G connectivity without looking for physical SIM kiosks.\n"
            "3. **6-Month Passport Rule:** Most international immigration authorities strictly require at least 6 months validity from your arrival date. Check your expiration date well in advance!\n"
            "4. **Digital Backups:** Keep encrypted copies of your passport, visa grant notices, and flight tickets in cloud storage accessible offline on your phone."
        )
        actions = ["Flight Booking Hacks", "Packing Checklist", "Plan a New Trip"]
        return reply, actions

    # 14. Universal Travel Copilot Fallback (Open-ended inquiry)
    reply = (
        f"I'm here as your RoamGenie AI Travel Copilot{dest_text}! Here is how we can bring your next travel vision to life:\n\n"
        "1. **Tailored Journey Planning:** Tell me your dream destination, travel dates, starting city, or budget, and I'll construct a day-by-day optimized itinerary with verified hotels and local sights.\n"
        "2. **Smart Budget Rebalancing:** I monitor allocations across lodging, food, and sightseeing to keep you on budget—or find luxury upgrades and royal dining when you're ready to treat yourselves.\n"
        "3. **Global & Regional Insights:** Ask me anything about weekend getaways, solo travel safety, packing formulas, or Tatkal train and cheap flight booking strategies!\n\n"
        "What would you like to explore next?"
    )
    actions = ["Suggest Weekend Getaways", "Budget Travel Hacks", "Packing Checklist Guide"]
    return reply, actions


class MockLLMProvider(BaseLLMProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        timeout_seconds: int = 15,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_config: Optional[Dict[str, Any]] = None,
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        # 1. Handle tool results in multi-turn conversation
        if contents:
            last_turn = contents[-1]
            parts = last_turn.get("parts", [])
            for p in parts:
                if "functionResponse" in p:
                    fr = p["functionResponse"]
                    tool_name = fr.get("name")
                    resp_data = fr.get("response", {})

                    if "error" in resp_data:
                        err_msg = resp_data["error"]
                        reply = (
                            f"I apologize, but I could not complete the operation: {err_msg} "
                            f"Could you please verify the details or clarify which trip you would like to inspect?"
                        )
                        actions = ["Show my trips", "Try again", "General travel advice"]
                        return LLMResponse(json.dumps({"reply": reply, "suggested_actions": actions}))

                    if tool_name == "get_travel_history":
                        trips = resp_data.get("trips", [])
                        count = resp_data.get("total_trips", len(trips))
                        reply = (
                            f"I retrieved your travel history. You have {count} trip{'s' if count != 1 else ''} on record. "
                            f"Let me know if you would like me to inspect or modify any specific journey!"
                        )
                        actions = ["View trip details", "What should I pack?", "Review my budget"]
                        return LLMResponse(json.dumps({"reply": reply, "suggested_actions": actions}))

                    elif tool_name == "get_itinerary_details":
                        dest = resp_data.get("destination", "your destination")
                        days_cnt = len(resp_data.get("days", []))
                        budget_tot = resp_data.get("total_budget", 0)
                        reply = (
                            f"Here is your itinerary for {dest}: {days_cnt} day{'s' if days_cnt != 1 else ''} scheduled "
                            f"with a total budget of ₹{budget_tot:,.2f}. Would you like me to suggest budget optimizations or alternative activities?"
                        )
                        actions = ["Swap Itinerary Items", "Reduce my budget", "Check packing checklist"]
                        return LLMResponse(json.dumps({"reply": reply, "suggested_actions": actions}))

                    elif tool_name == "propose_itinerary_modification":
                        summary = resp_data.get("summary", "I simulated your proposed itinerary change.")
                        target_d = resp_data.get("target_day_number") or resp_data.get("day_number") or 2
                        action_used = resp_data.get("action", "modification")

                        # Check if original user inquiry was about reducing budget, slow pacing, rest & roaming, or flexible eating
                        orig_text = ""
                        if contents and len(contents) > 0:
                            parts0 = contents[0].get("parts", [])
                            if parts0 and "text" in parts0[0]:
                                orig_text = parts0[0]["text"].lower()

                        is_roam_budget = any(
                            k in orig_text for k in (
                                "rest", "roam", "roaming", "slow", "fewer places",
                                "flexible", "eating", "food", "dining", "budget",
                                "deficit", "bring down", "reduce"
                            )
                        )

                        if is_roam_budget and action_used == "clear_day":
                            reply = (
                                f"**Yes, absolutely!** Slowing down your pace with more rest and roaming, along with flexible eating, "
                                f"is the most effective way to eliminate your deficit.\n\n"
                                f"**Key Strategic Suggestions:**\n"
                                f"- **Rest & Roaming:** Linger at complimentary landmarks (such as scenic waterfront promenades and iconic architectural sights) instead of rushing through crowded ticketed venues.\n"
                                f"- **Flexible Dining:** Switch from booked multi-course meals to artisan cafes and authentic street food stalls, reducing food costs by up to 75%.\n"
                                f"- **Paced Sights:** Give yourself 3–4 hours per landmark to avoid ticket burnout and transportation rush.\n\n"
                                f"I have prepared a proposal to clear **Day {target_d}** for dedicated rest, scenic roaming, and flexible dining ({summary}). "
                                f"Review the financial impact below and click **Apply Changes** to update your itinerary!"
                            )
                            actions = ["Apply Changes", "Swap dining instead", "Explore free attractions"]
                        elif is_roam_budget and action_used == "swap":
                            reply = (
                                f"**Yes, absolutely!** Replacing expensive scheduled plans with economical, flexible alternatives "
                                f"brings down your budget immediately.\n\n"
                                f"{summary}\n\n"
                                f"Take a look at the proposal card below and click **Apply Changes** to update your itinerary!"
                            )
                            actions = ["Apply Changes", "Clear a day for rest", "Keep plans as is"]
                        else:
                            reply = f"{summary} Would you like to confirm and apply this update to your trip?"
                            actions = ["Confirm change", "Cancel", "Explore alternatives"]
                        return LLMResponse(json.dumps({"reply": reply, "suggested_actions": actions}))

        # 2. Parse prompt facts and clean user query
        facts = _parse_prompt_facts(prompt)
        q_raw = facts["user_query"]
        q_clean = q_raw.lower().strip()
        trip_id = facts["trip_id"] or 1
        dest_name = facts["dest_name"]
        dest_text = f" for {dest_name}" if dest_name else ""

        # 3. Check if tools are enabled and user inquiry matches tool intents
        if tools:
            if any(k in q_clean for k in ("travel history", "past trips", "my trips", "all trips", "previous trips", "list trips", "show my trips", "history of trips")):
                return LLMResponse(
                    content="",
                    function_call={"name": "get_travel_history", "args": {}},
                )
            elif any(k in q_clean for k in ("itinerary details", "show itinerary", "view itinerary", "full schedule", "schedule details", "day-by-day", "get itinerary", "entire schedule")):
                target_trip_id = trip_id
                for word in q_clean.split():
                    if word.isdigit():
                        target_trip_id = int(word)
                        break
                return LLMResponse(
                    content="",
                    function_call={"name": "get_itinerary_details", "args": {"trip_id": target_trip_id}},
                )
            # Query explicitly about reducing budget through rest, roaming, slower pace, or flexible eating
            is_rest_roam_budget = (
                any(k in q_clean for k in ("bring down", "reduce", "lower", "cut", "save", "cheaper", "deficit", "over budget", "optimize budget")) and
                any(k in q_clean for k in ("rest", "roam", "roaming", "slow", "fewer places", "more time", "flexible", "eating", "food", "dining", "pacing", "relax"))
            ) or any(k in q_clean for k in (
                "rest and roaming", "roam and rest", "more time for rest",
                "flexible time for eating", "flexible eating", "slow down", "fewer places"
            ))

            if is_rest_roam_budget and facts["itinerary_items"]:
                day_match = re.search(r"day\s*(\d+)", q_clean)
                if day_match:
                    target_d = int(day_match.group(1))
                else:
                    available_days = sorted(list({itm["day"] for itm in facts["itinerary_items"]}))
                    target_d = 2 if 2 in available_days else available_days[0]

                return LLMResponse(
                    content="",
                    function_call={
                        "name": "propose_itinerary_modification",
                        "args": {
                            "trip_id": trip_id,
                            "action": "clear_day",
                            "day_number": target_d,
                        },
                    },
                )
            elif any(k in q_clean for k in (
                "cancel", "clear day", "remove day", "delete day", "cancel all", "clear all",
                "cancel plan", "clear plan", "drop day", "rest day", "free day", "roaming day",
                "make day", "rest on day", "roam on day"
            )) or (re.search(r"day\s*\d+", q_clean) and any(k in q_clean for k in ("clear", "cancel", "rest", "roam", "free"))):
                day_match = re.search(r"day\s*(\d+)", q_clean)
                if day_match:
                    target_d = int(day_match.group(1))
                    return LLMResponse(
                        content="",
                        function_call={
                            "name": "propose_itinerary_modification",
                            "args": {
                                "trip_id": trip_id,
                                "action": "clear_day",
                                "day_number": target_d,
                            },
                        },
                    )
                else:
                    reply = "I can help you clear those activities. Which day's schedule would you like to cancel?"
                    actions = ["Cancel Day 1", "Cancel Day 2", "Keep plans as is"]
                    clarification = {
                        "question": "Which day's plans would you like to cancel?",
                        "options": ["Day 1 - Oct 22", "Day 2 - Oct 23", "Day 3 - Oct 24"],
                        "allow_custom_input": True,
                    }
                    return LLMResponse(json.dumps({
                        "reply": reply,
                        "suggested_actions": actions,
                        "clarification_request": clarification,
                    }))
            elif any(k in q_clean for k in (
                "swap dining", "cheaper dining", "cheaper food", "swap restaurant", "casual dining",
                "street food", "swap meal", "cheaper meal", "swap lunch", "swap dinner"
            )):
                food_items = [itm for itm in facts["itinerary_items"] if itm["category"] in ("food", "dining", "restaurant")]
                target_item_id = food_items[0]["item_id"] if food_items else (facts["itinerary_items"][0]["item_id"] if facts["itinerary_items"] else 1)
                rep_id = 1
                for d_str in facts.get("dining", []):
                    m_id = re.search(r"\[ID\s*#(\d+)\]", d_str)
                    if m_id:
                        rep_id = int(m_id.group(1))
                        break
                return LLMResponse(
                    content="",
                    function_call={
                        "name": "propose_itinerary_modification",
                        "args": {
                            "trip_id": trip_id,
                            "action": "swap",
                            "item_id": target_item_id,
                            "replacement_type": "restaurant",
                            "replacement_id": rep_id,
                        },
                    },
                )
            elif any(k in q_clean for k in ("swap", "cheaper hotel", "modify itinerary", "change hotel", "remove activity", "reduce hotel", "change accommodation", "replace hotel", "swap item")):
                target_item_id = facts["itinerary_items"][0]["item_id"] if facts["itinerary_items"] else 1
                rep_id = 1
                for h_str in facts.get("hotels", []):
                    m_id = re.search(r"\[ID\s*#(\d+)\]", h_str)
                    if m_id:
                        rep_id = int(m_id.group(1))
                        break
                return LLMResponse(
                    content="",
                    function_call={
                        "name": "propose_itinerary_modification",
                        "args": {
                            "trip_id": trip_id,
                            "action": "swap",
                            "item_id": target_item_id,
                            "replacement_type": "hotel",
                            "replacement_id": rep_id,
                        },
                    },
                )

        # 4. Check if chat / assistant copilot prompt
        if "copilot" in system_prompt.lower() or "assistant" in system_prompt.lower() or "user query:" in prompt.lower():
            # A. Ambiguous request -> Clarification
            if any(k in q_clean for k in ("change my plan", "change plans", "plans for tonight", "modify tonight", "change tonight", "change something", "change my schedule")):
                reply = (
                    f"I'd love to help adjust your plans{dest_text}! Which specific day or evening would you like to update?"
                )
                actions = ["Change Day 1", "Change Day 2", "Keep plans as is"]
                clarification = {
                    "question": "Which night or day would you like to change?",
                    "options": ["Day 1 - Oct 22", "Day 2 - Oct 23", "Day 3 - Oct 24"],
                    "allow_custom_input": True,
                }
                return LLMResponse(json.dumps({
                    "reply": reply,
                    "suggested_actions": actions,
                    "clarification_request": clarification,
                }))
            elif any(k in q_clean for k in ("cancel", "clear day", "remove day", "delete day", "cancel all", "clear all", "cancel plan")):
                day_match = re.search(r"day\s*(\d+)", q_clean)
                if day_match:
                    d_num = int(day_match.group(1))
                    reply = f"I've identified your schedule for Day {d_num}{dest_text}. Would you like me to clear all scheduled plans for Day {d_num}?"
                    actions = [f"Clear Day {d_num}", "Swap items instead", "Keep plans as is"]
                    clarification = {
                        "question": f"Confirm cancellation for Day {d_num}?",
                        "options": [f"Clear all activities on Day {d_num}", f"Swap items on Day {d_num}", "Keep Day as is"],
                        "allow_custom_input": True,
                    }
                else:
                    reply = f"Which day's plans would you like to clear{dest_text}?"
                    actions = ["Cancel Day 1", "Cancel Day 2", "Keep plans as is"]
                    clarification = {
                        "question": "Which day would you like to cancel?",
                        "options": ["Day 1", "Day 2", "Day 3"],
                        "allow_custom_input": True,
                    }
                return LLMResponse(json.dumps({
                    "reply": reply,
                    "suggested_actions": actions,
                    "clarification_request": clarification,
                }))

            # B. Trip Duration & Length ("how many day trip is this", "how many days", "how long", etc.)
            elif any(k in q_clean for k in (
                "how many day", "how many days", "how many night", "how many nights",
                "how long", "duration", "trip length", "number of day", "number of days",
                "length of this trip", "length of my trip", "length of the trip", "total day", "total days",
                "day trip", "days trip", "days is this", "day is this", "days is my", "day is my",
                "how long is", "trip duration", "how long will", "how long do we"
            )) or re.search(r"how\s+many\s+days?", q_clean) or re.search(r"days?\s+(is|for|in|of)\s+(this|my|the)", q_clean):
                if facts["day_count"] > 0:
                    reply = (
                        f"Your trip to **{dest_name or 'your destination'}** is a **{facts['day_count']}-day** journey, "
                        f"running from **{facts['start_date']}** to **{facts['end_date']}** for **{facts['traveller_count']} traveller(s)**! 🎒\n\n"
                        f"Would you like me to walk you through Day 1's activities or review your budget allocations?"
                    )
                    actions = ["View Day 1 Schedule", "What is my budget?", "What should I pack?"]
                else:
                    reply = (
                        f"You are currently inquiring about trip duration{dest_text}. Once you connect a confirmed trip, "
                        f"I can give you its exact dates, total day count, and day-by-day timeline!"
                    )
                    actions = ["Plan a new trip", "View My Trips", "What should I pack?"]

            # C. Dates & Departure Timing
            elif any(k in q_clean for k in ("when is my trip", "what are the dates", "dates of my trip", "start date", "end date", "departure date", "return date", "when do we leave", "when are we going", "travel dates", "when does it start")):
                if facts["start_date"]:
                    origin_txt = f", departing from **{facts['origin']}**" if facts["origin"] else ""
                    reply = (
                        f"Your trip to **{dest_name or 'your destination'}** is scheduled from **{facts['start_date']}** "
                        f"to **{facts['end_date']}** ({facts['day_count']} days total){origin_txt}. "
                        f"Let me know if you would like to check the local weather forecast or inspect the daily schedule!"
                    )
                    actions = ["Check Live Forecast", "View Day 1 Schedule", "What is my budget?"]
                else:
                    reply = f"Please select a confirmed trip to view your departure and return travel dates{dest_text}."
                    actions = ["View My Trips", "Plan Trip", "Explore Destinations"]

            # D. Travellers & Group Count
            elif any(k in q_clean for k in ("how many people", "how many travellers", "who is travelling", "group size", "number of people", "traveller count", "who is coming", "travelers")):
                reply = (
                    f"This trip to **{dest_name or 'your destination'}** is planned for **{facts['traveller_count']} traveller(s)**. "
                    f"All accommodation tariffs, dining allowances, and entry tickets are scaled for this group size!"
                )
                actions = ["What is my budget?", "View Itinerary", "What should I pack?"]

            # E. Specific Day Schedule / Day 1, Day 2, etc.
            elif re.search(r"day\s*(\d+)", q_clean):
                day_match = re.search(r"day\s*(\d+)", q_clean)
                d_num = int(day_match.group(1))
                matching_items = [itm for itm in facts["itinerary_items"] if itm["day"] == d_num]
                if matching_items:
                    items_bullets = "\n".join([f"- **{itm['title']}** ({itm['category'].title()}, ₹{itm['cost']:,.2f})" for itm in matching_items])
                    reply = (
                        f"Here is your lineup for **Day {d_num}** in **{dest_name or 'your destination'}**:\n\n"
                        f"{items_bullets}\n\n"
                        f"Would you like to swap any of these activities or check alternative dining spots?"
                    )
                    actions = [f"Clear Day {d_num}", "Swap an activity", "Check Weather Forecast"]
                else:
                    reply = (
                        f"I've identified your schedule for Day {d_num}{dest_text}. "
                        f"Would you like to review alternative activities or swap events in your timeline?"
                    )
                    actions = [f"Clear Day {d_num}", "Swap items instead", "Keep plans as is"]

            # F1. Rest, Roaming & Budget Reduction / Flexible Dining (General Query)
            elif (
                (any(k in q_clean for k in ("bring down", "reduce", "lower", "cut", "save", "cheaper", "deficit", "over budget")) and
                 any(k in q_clean for k in ("rest", "roam", "roaming", "slow", "fewer places", "more time", "flexible", "eating", "food", "dining", "pacing", "relax")))
                or any(k in q_clean for k in ("rest and roaming", "roam and rest", "more time for rest", "flexible time for eating", "flexible eating", "slow down", "fewer places"))
            ):
                reply = (
                    f"**Yes, absolutely!** You can bring down your budget dramatically by building in dedicated rest, leisurely roaming, and flexible dining{dest_text}.\n\n"
                    f"**Strategic Budget Recommendations:**\n"
                    f"1. **Allocate Dedicated Rest & Roaming Days:** Clearing a packed sightseeing day eliminates costly entry tickets and lets you experience complimentary highlights like scenic beaches, waterfront promenades, and cultural landmarks.\n"
                    f"2. **Flexible & Casual Dining:** Scheduled multi-course dining is usually the largest budget drain. Shifting to flexible street food stalls and artisan cafes cuts food expenses by up to 70%.\n"
                    f"3. **Pace Out Visits:** Spending longer at 1–2 key attractions per day avoids transport hops and multiple ticket fees.\n\n"
                    f"You can easily apply these changes: click the **⇄ Replace activity** button on any timeline event to swap for cheaper/free options, or ask me to **'Clear Day 2 for rest and roaming'** to preview the savings and apply them directly!"
                )
                actions = ["Clear Day 2 for rest & roaming", "Swap expensive dining", "Review free attractions"]

            # F1_SPLURGE. Splurge / Luxury Upgrade / Add More Expenses / Treat Ourselves
            elif any(k in q_clean for k in (
                "add some more expense", "add more expense", "add some more expenses", "add more expenses",
                "more expense", "more expenses", "splurge", "upgrade", "treat ourselves", "treat myself",
                "luxury", "higher budget", "more spending", "spend more", "fine dining", "upscale",
                "fancier", "fancy hotel", "luxury hotel", "pamper", "splurge a bit", "splurge more",
                "add expense", "add expenses", "increase spending", "increase budget", "elevate"
            )):
                if facts["remaining_budget"] > 0:
                    surplus = facts["remaining_budget"]
                    reply = (
                        f"I love the way you think! You currently have a comfortable surplus of **₹{surplus:,.2f}** remaining in your budget for **{dest_name or 'your journey'}**, "
                        f"which means we have plenty of room to elevate your trip into a truly luxurious getaway! 🥂✨\n\n"
                        f"**Here are my top high-value upgrade recommendations:**\n\n"
                        f"1. **Luxury Accommodation Upgrade:** Elevate your stay to a premier boutique resort or heritage suite with scenic balconies and bespoke hospitality.\n"
                        f"2. **Fine-Dining & Royal Banquets:** Reserve signature chef's tasting dinners, royal regional thalis, or an atmospheric rooftop culinary experience.\n"
                        f"3. **Curated VIP & Private Heritage Tours:** Book a dedicated private heritage storyteller/guide or private chauffeured cab for effortless sightseeing and exclusive access.\n\n"
                        f"Would you like me to upgrade your hotel stay or swap in a fine-dining experience on one of your evenings?"
                    )
                    actions = ["Upgrade Hotel to Luxury", "Add Fine Dining Banquet", "Book Private Heritage Tour"]
                elif facts["deficit"] > 0:
                    deficit = facts["deficit"]
                    reply = (
                        f"We're currently tracking **₹{deficit:,.2f}** over your initial budget, but if you want to treat yourselves to memorable upgrades, "
                        f"we can easily balance the books! 🌟\n\n"
                        f"We can swap a couple of high-cost daytime activities for scenic viewpoints or cultural strolls to unlock funds for an upgraded luxury stay "
                        f"or a celebratory fine-dining dinner. Which part of your trip would you like to elevate first?"
                    )
                    actions = ["Upgrade Hotel", "Add Fine Dining Banquet", "Rebalance Itinerary"]
                else:
                    reply = (
                        f"Ready to treat yourselves? For your journey{dest_text}, you can elevate your trip with "
                        f"boutique heritage stays, exclusive guided cultural tours, and memorable fine-dining banquets. "
                        f"Let me know which day you'd like to make extra special!"
                    )
                    actions = ["Upgrade Hotel", "Add Fine Dining Banquet", "Explore Premier Tours"]

            # F2. Budget / Costs / Money / Deficit
            elif any(k in q_clean for k in ("budget", "cost", "how much money", "remaining money", "remaining budget", "deficit", "over budget", "under budget", "expenses", "spending", "how much is this trip")):
                if facts["total_budget"] > 0:
                    alloc_lines = "\n".join([f"- **{cat.title()}:** ₹{amt:,.2f}" for cat, amt in facts["allocations"].items()]) if facts["allocations"] else "- Accommodation, dining, transport, and sightseeing allocations recorded."
                    bal_status = f"⚠️ Deficit: ₹{facts['deficit']:,.2f}" if facts["deficit"] > 0 else "✓ Fully Aligned"
                    reply = (
                        f"Here is your financial snapshot for **{dest_name or 'your trip'}**:\n\n"
                        f"- **Total Budget:** ₹{facts['total_budget']:,.2f}\n"
                        f"- **Estimated Total:** ₹{facts['estimated_total']:,.2f}\n"
                        f"- **Remaining Balance:** ₹{facts['remaining_budget']:,.2f} ({bal_status})\n\n"
                        f"**Category Allocations:**\n{alloc_lines}\n\n"
                        f"You can use the **⇄ Swap** button on any itinerary event to replace it with a more economical option!"
                    )
                    actions = ["Review Budget Allocations", "Swap Itinerary Items", "Explore Free Attractions"]
                else:
                    reply = (
                        f"I've analyzed your trip budget{dest_text}. To optimize expenses, consider choosing budget-friendly dining or exploring our alternative hotels. "
                        f"You can use the ⇄ Swap button on any itinerary event to replace it with a more economical option!"
                    )
                    actions = ["Review Budget Allocations", "Swap Itinerary Items", "Explore Free Attractions"]

            # G. Weather / Rain / Forecast / Temperature / Monsoon (STRICTLY on user query!)
            elif any(k in q_clean for k in ("weather", "rain", "monsoon", "forecast", "temperature", "temp", "will it rain", "is it raining", "umbrella", "storm", "climate")):
                f_text = f" (Current condition: {facts['weather_summary']})" if facts["weather_summary"] else ""
                is_rainy = "rain" in facts["weather_summary"].lower() or any("rain" in f.split("(")[0].lower() for f in facts["forecast_lines"])
                if is_rainy:
                    reply = (
                        f"The weather forecast indicates potential rain during your trip{dest_text}{f_text}. "
                        f"Plan for indoor cultural sightseeing such as local museums, historic palace chambers, and covered markets. "
                        f"Pack a travel umbrella, waterproof footwear, and a dry pouch. You can also use the ⇄ Swap tool on your "
                        f"itinerary timeline to shift outdoor activities to indoor alternatives!"
                    )
                else:
                    reply = (
                        f"The live weather forecast for **{dest_name or 'your destination'}** looks great for travel{f_text}. "
                        f"Expect pleasant conditions for daytime sightseeing and evening strolls. Be sure to stay hydrated and dress comfortably!"
                    )
                actions = ["Swap Itinerary Items", "Check Live Weather Forecast", "View Packing Checklist"]

            # H. Where to stay / Hotels / Accommodations
            elif any(k in q_clean for k in ("where am i staying", "what hotel", "hotel details", "accommodations", "places to stay", "resort", "lodging", "where do we stay", "hotel", "stay")):
                hotel_info = ""
                if facts["hotels"]:
                    hotel_info = f"\n\nTop hotels in your destination catalogue:\n" + "\n".join([f"- {h}" for h in facts["hotels"][:3]])
                reply = (
                    f"For your stay in **{dest_name or 'your destination'}**, your itinerary includes comfortable accommodation tailored to your budget.{hotel_info}\n\n"
                    f"You can easily swap hotels anytime using the ⇄ Swap button on your schedule!"
                )
                actions = ["Swap Hotel", "Review Budget Allocations", "View Schedule"]

            # I. Food / Dining / Restaurants
            elif any(k in q_clean for k in ("food", "restaurant", "dining", "where to eat", "eat", "cuisine", "dishes", "cafe", "lunch", "dinner", "breakfast", "meal")):
                dining_info = ""
                if facts["dining"]:
                    dining_info = f"\n\nRecommended dining venues in your destination catalogue:\n" + "\n".join([f"- {d}" for d in facts["dining"][:3]])
                reply = (
                    f"For dining{dest_text}, you have great authentic local restaurants in your destination catalogue.{dining_info} "
                    f"Check out the dining recommendations or swap a meal in your itinerary timeline!"
                )
                actions = ["Browse Restaurants", "Swap Dining Spot", "Check Itinerary"]

            # J. Attractions / Sights / Things to do
            elif any(k in q_clean for k in ("attraction", "sight", "places to visit", "what should i see", "things to do", "monument", "places to go", "activity", "activities", "sights")):
                att_info = ""
                if facts["attractions"]:
                    att_info = f"\n\nTop sights in your destination catalogue:\n" + "\n".join([f"- {a}" for a in facts["attractions"][:3]])
                reply = (
                    f"Here are top verified cultural sights and experiences{dest_text}:{att_info}\n\n"
                    f"Use the ⇄ Swap tool on any sightseeing activity to customize your day!"
                )
                actions = ["Explore Attractions", "Swap Sightseeing", "Check Itinerary"]

            # K. Packing / Clothing / What to wear
            elif any(k in q_clean for k in ("5-4-3-2-1", "capsule", "packing formula", "packing rule", "how to pack light", "packing tips")) or (
                any(k in q_clean for k in ("pack", "wear", "clothes", "clothing", "checklist", "what should i bring", "luggage"))
                and not dest_name and not facts["packing_items"]
            ):
                reply, actions = answer_general_travel_query(q_clean, facts, dest_name)
            elif any(k in q_clean for k in ("pack", "wear", "clothes", "clothing", "checklist", "what should i bring", "luggage")):
                packing_summary = ""
                if facts["packing_items"]:
                    packing_summary = f"\n\nYour checklist currently tracks:\n" + "\n".join([f"- {p}" for p in facts["packing_items"][:4]])
                reply = (
                    f"Based on the local forecast and your travel dates{dest_text}, I recommend packing lightweight breathable clothing, "
                    f"comfortable walking shoes, sunscreen, and an umbrella if rain is likely.{packing_summary}\n\n"
                    f"Check your trip packing checklist to track packed items!"
                )
                actions = ["View Packing Checklist", "Check Live Weather Forecast", "Review Itinerary"]

            # L. Tips / Advice / Know before you go (Destination specific)
            elif any(k in q_clean for k in ("know before", "things to know", "before visiting", "local culture", "local etiquette", "local customs", "visitor tips", "what to know")):
                reply = (
                    f"Key tips before visiting{dest_text}: carry valid photo identification, keep digital and cash payment options ready, "
                    f"check local monument timings in advance, and dress comfortably for extensive walking. Be sure to review your packing "
                    f"checklist and live weather forecast on your RoamGenie dashboard before departure."
                )
                actions = ["View Packing Checklist", "Check Live Weather Forecast", "Review Itinerary"]

            # M. Itinerary Pacing / Overall Schedule
            elif any(k in q_clean for k in ("itinerary", "improve", "schedule", "pacing", "timeline")):
                reply = (
                    f"To improve your itinerary{dest_text}, balance high-energy morning sightseeing with relaxed afternoon local dining "
                    f"and sunset leisure. Make sure travel times between activities are comfortable. You can click ⇄ Swap on any event "
                    f"in your itinerary timeline to customize your schedule with alternative catalogue spots!"
                )
                actions = ["Swap Itinerary Items", "Review Budget Allocations", "What should I pack?"]

            # N. Create / Plan Trip
            elif any(k in q_clean for k in ("create a trip", "create trip", "plan a trip", "plan trip", "new trip", "book a trip")):
                reply = (
                    "I'd love to help you plan a new journey! You can launch the **Plan Trip** wizard to set your destination, "
                    "dates, budget, and travel style, and I'll generate a fully optimized, day-by-day itinerary for you."
                )
                actions = ["Plan Trip Wizard", "Explore Destinations", "View My Trips"]

            # O. Universal Travel Advice & Concierge Engine
            else:
                reply, actions = answer_general_travel_query(q_clean, facts, dest_name)

            return LLMResponse(json.dumps({
                "reply": reply,
                "suggested_actions": actions,
            }))

        # Returns structured mock json representation for itinerary planning
        return LLMResponse(json.dumps({
            "summary": "AI Curated Cultural Experience",
            "days": [
                {
                    "day_number": 1,
                    "date": "2026-09-15",
                    "items": [
                        {
                            "time": "09:00",
                            "title": "Welcome Orientation & Palace Visit",
                            "category": "attractions",
                            "estimated_cost": 200.00,
                            "notes": "Enjoy the magnificent royal courtyards",
                        },
                        {
                            "time": "13:00",
                            "title": "Authentic Regional Lunch",
                            "category": "food",
                            "estimated_cost": 400.00,
                            "notes": "Sample traditional culinary delights",
                        },
                    ],
                }
            ],
            "budget_split": [
                {"category": "accommodation", "amount": 2800.00},
                {"category": "food", "amount": 1200.00},
                {"category": "attractions", "amount": 600.00},
            ],
            "warnings": [],
            "packing_items": [
                "Comfortable walking shoes",
                "Sun protection hat",
                "Light breathable cottons",
            ],
            "weather_advice": "Pleasant morning temperatures with moderate sunshine.",
        }))


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name or "gemini-1.5-flash"

    @property
    def provider_name(self) -> str:
        return "gemini"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        timeout_seconds: int = 15,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_config: Optional[Dict[str, Any]] = None,
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"

        # Build contents array
        if contents is not None:
            request_contents = contents
        else:
            request_contents = [{"parts": [{"text": prompt}]}]

        gen_config: Dict[str, Any] = {
            "temperature": 0.2,
        }

        payload: Dict[str, Any] = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": request_contents,
            "generationConfig": gen_config,
        }

        # Apply tools and tool_config if provided
        if tools:
            if len(tools) > 0 and "function_declarations" in tools[0]:
                payload["tools"] = tools
            else:
                payload["tools"] = [{"function_declarations": tools}]
        else:
            gen_config["response_mime_type"] = "application/json"

        if tool_config:
            payload["tool_config"] = tool_config

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, json=payload)
                if resp.status_code != 200:
                    raise LLMProviderError(f"Gemini API returned HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise LLMProviderError("No response candidates returned by Gemini.")

                candidate_content = candidates[0].get("content", {})
                parts = candidate_content.get("parts", [])
                if not parts:
                    raise LLMProviderError("No content parts in Gemini candidate response.")

                # Check for functionCall in candidate parts
                for part in parts:
                    if "functionCall" in part:
                        return LLMResponse(
                            content="",
                            function_call=part["functionCall"],
                            raw_parts=parts,
                        )

                # Collect text parts
                text_segments = [p.get("text", "") for p in parts if "text" in p]
                joined_text = "".join(text_segments)
                return LLMResponse(
                    content=joined_text,
                    function_call=None,
                    raw_parts=parts,
                )
        except httpx.RequestError as exc:
            raise LLMProviderError(f"Network error communicating with Gemini API: {exc}")


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name or "gpt-4o-mini"

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        timeout_seconds: int = 15,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_config: Optional[Dict[str, Any]] = None,
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise LLMProviderError(f"OpenAI API returned HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                return LLMResponse(data["choices"][0]["message"]["content"])
        except httpx.RequestError as exc:
            raise LLMProviderError(f"Network error communicating with OpenAI API: {exc}")


class GroqLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        self.api_key = api_key
        self.model_name = model_name or "llama-3.1-8b-instant"

    @property
    def provider_name(self) -> str:
        return "groq"

    def generate(
        self,
        prompt: str,
        system_prompt: str,
        timeout_seconds: int = 15,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_config: Optional[Dict[str, Any]] = None,
        contents: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise LLMProviderError(f"Groq API returned HTTP {resp.status_code}: {resp.text[:200]}")
                data = resp.json()
                return LLMResponse(data["choices"][0]["message"]["content"])
        except httpx.RequestError as exc:
            raise LLMProviderError(f"Network error communicating with Groq API: {exc}")


def get_llm_provider(settings: Optional[Settings] = None) -> BaseLLMProvider:
    """Factory creating appropriate LLM provider based on settings and available API keys."""
    cfg = settings or get_settings()
    provider_type = cfg.ai_provider.lower().strip()

    if provider_type == "gemini":
        key = cfg.gemini_api_key or cfg.ai_api_key
        if key:
            return GeminiLLMProvider(api_key=key, model_name=cfg.ai_model)
        logger.info("Gemini provider selected but no key configured; using mock provider.")
    elif provider_type == "openai":
        key = cfg.openai_api_key or cfg.ai_api_key
        if key:
            return OpenAILLMProvider(api_key=key, model_name=cfg.ai_model)
        logger.info("OpenAI provider selected but no key configured; using mock provider.")
    elif provider_type == "groq":
        key = cfg.groq_api_key or cfg.ai_api_key
        if key:
            return GroqLLMProvider(api_key=key, model_name=cfg.ai_model)
        logger.info("Groq provider selected but no key configured; using mock provider.")

    return MockLLMProvider()
