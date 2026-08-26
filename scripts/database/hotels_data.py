"""Master Hotel Dataset Generator (Phase D3)
Provides a rich, deterministic, geographically authentic catalog of ~6,000 hotels across all 500 destinations.
"""
import hashlib
import random
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

RANDOM_SEED = 20260820

# Known landmark and authentic hotels for prominent destinations across regions
CURATED_LANDMARK_HOTELS: Dict[Tuple[str, str], List[Tuple[str, float, float]]] = {
    ("Mysuru", "India"): [
        ("Heritage Garden Stay", 2800.0, 4.3),      # Preserved ID 1
        ("Royal Orchid Metropole", 4500.0, 4.7),    # Preserved ID 2
        ("Lalitha Mahal Palace Hotel", 8500.0, 4.6),
        ("Radisson Blu Plaza Hotel Mysuru", 6200.0, 4.7),
        ("Fortune JP Palace", 4200.0, 4.4),
        ("Grand Mercure Mysuru", 5400.0, 4.5),
        ("Southern Star Mysuru", 3800.0, 4.3),
        ("Hotel Pai Vista", 3100.0, 4.2),
        ("Roost Guesthouse & Homestay", 1400.0, 4.1),
        ("Zostel Mysuru", 850.0, 4.5),
        ("The Windflower Resort & Spa Mysuru", 7500.0, 4.6),
        ("Country Inn & Suites by Radisson Mysuru", 3600.0, 4.3),
    ],
    ("Kochi", "India"): [
        ("Brunton Boatyard - CGH Earth", 12500.0, 4.8),
        ("Grand Hyatt Kochi Bolgatty", 14000.0, 4.9),
        ("Taj Malabar Resort & Spa", 13000.0, 4.8),
        ("Old Harbour Hotel Fort Kochi", 8500.0, 4.7),
        ("Eighth Bastion - CGH Earth", 7200.0, 4.6),
        ("Forte Kochi Heritage Hotel", 9200.0, 4.8),
        ("Radisson Blu Kochi", 5400.0, 4.4),
        ("Fragrant Nature Kochi", 6800.0, 4.6),
        ("Hotel Arches Fort Kochi", 3200.0, 4.3),
        ("Zostel Kochi Fort Kochi", 950.0, 4.5),
        ("The Hosteller Fort Kochi", 850.0, 4.4),
        ("Rossitta Wood Castle Homestay", 1800.0, 4.2),
    ],
    ("Jaipur", "India"): [
        ("Rambagh Palace Jaipur", 42000.0, 4.9),
        ("The Oberoi Rajvilas", 38000.0, 4.9),
        ("Jai Mahal Palace", 18500.0, 4.8),
        ("ITC Rajputana, a Luxury Collection Hotel", 12000.0, 4.7),
        ("Samode Haveli", 14500.0, 4.8),
        ("Alsisar Haveli - Heritage Hotel", 6800.0, 4.5),
        ("Shahpura Haveli", 7500.0, 4.6),
        ("Hilton Jaipur", 5800.0, 4.4),
        ("Holiday Inn Jaipur City Centre", 4200.0, 4.3),
        ("Umaid Bhawan Heritage House Hotel", 3400.0, 4.3),
        ("Zostel Jaipur", 900.0, 4.6),
        ("The Moustache Hostel Jaipur", 800.0, 4.4),
    ],
    ("Udaipur", "India"): [
        ("Taj Lake Palace Udaipur", 48000.0, 4.9),
        ("The Oberoi Udaivilas", 52000.0, 5.0),
        ("The Leela Palace Udaipur", 45000.0, 4.9),
        ("Fateh Prakash Palace - Heritage Grand", 16000.0, 4.7),
        ("Shiv Niwas Palace", 14000.0, 4.6),
        ("Jagmandir Island Palace", 22000.0, 4.8),
        ("Trident Udaipur", 9500.0, 4.6),
        ("Amet Haveli on Lake Pichola", 8200.0, 4.6),
        ("Radisson Blu Udaipur Palace Resort & Spa", 7800.0, 4.5),
        ("Madri Haveli", 3600.0, 4.4),
        ("Zostel Udaipur", 950.0, 4.6),
        ("Jagat Niwas Palace Hotel", 4800.0, 4.5),
    ],
    ("Goa", "India"): [
        ("Taj Exotica Resort & Spa Goa", 22000.0, 4.8),
        ("The St. Regis Goa Resort", 26000.0, 4.9),
        ("W Goa - Vagator Beach", 24000.0, 4.7),
        ("Alila Diwa Goa", 14500.0, 4.7),
        ("Grand Hyatt Goa - Bambolim", 16000.0, 4.8),
        ("Heritage Village Resort & Spa Goa", 8500.0, 4.5),
        ("Ahilya By The Sea - Boutique Hotel", 18000.0, 4.8),
        ("Hard Rock Hotel Goa - Calangute", 7200.0, 4.3),
        ("Santana Beach Resort Candolim", 3800.0, 4.2),
        ("Casa Severina Boutique Hotel", 4600.0, 4.4),
        ("Zostel Morjim", 1100.0, 4.5),
        ("Pappi Chulo Hostel Vagator", 850.0, 4.3),
    ],
    ("Paris", "France"): [
        ("The Ritz Paris - Place Vendôme", 95000.0, 4.9),
        ("Le Meurice - Dorchester Collection", 88000.0, 4.9),
        ("Four Seasons Hotel George V Paris", 92000.0, 4.9),
        ("Hôtel Plaza Athénée", 85000.0, 4.8),
        ("Hôtel Madame Rêve Louvre", 38000.0, 4.7),
        ("Hôtel Monge Latin Quarter", 22000.0, 4.6),
        ("Novotel Paris Les Halles", 18500.0, 4.4),
        ("CitizenM Paris Gare de Lyon", 14500.0, 4.5),
        ("Hôtel de la Paix Montparnasse", 11000.0, 4.2),
        ("Ibis Paris Bastille Opera", 8800.0, 4.1),
        ("Generator Paris Canal Saint-Martin", 4200.0, 4.3),
        ("The People - Paris Marais Hostel", 3800.0, 4.4),
    ],
    ("Tokyo", "Japan"): [
        ("Aman Tokyo - Otemachi", 98000.0, 4.9),
        ("Park Hyatt Tokyo - Shinjuku", 65000.0, 4.8),
        ("The Ritz-Carlton Tokyo - Roppongi", 72000.0, 4.9),
        ("Hoshinoya Tokyo Luxury Ryokan", 82000.0, 4.9),
        ("Palace Hotel Tokyo - Marunouchi", 55000.0, 4.8),
        ("Cerulean Tower Tokyu Hotel Shibuya", 28000.0, 4.6),
        ("Hotel Gracery Shinjuku", 16500.0, 4.4),
        ("Candeo Hotels Tokyo Roppongi", 18000.0, 4.5),
        ("Sotetsu Fresa Inn Ginza-Nanachome", 12500.0, 4.3),
        ("APA Hotel Shinjuku Kabukicho Tower", 9500.0, 4.1),
        ("Nui. Hostel & Bar Lounge Asakusa", 3800.0, 4.6),
        ("UNPLAN Shinjuku Backpacker Hostel", 4200.0, 4.5),
    ],
    ("London", "United Kingdom"): [
        ("The Savoy London - Strand", 78000.0, 4.9),
        ("Claridge's Hotel Mayfair", 85000.0, 4.9),
        ("The Connaught Mayfair", 82000.0, 4.8),
        ("Shangri-La The Shard, London", 65000.0, 4.8),
        ("The Ned London - City of London", 34000.0, 4.7),
        ("Sea Containers London South Bank", 24000.0, 4.5),
        ("CitizenM Tower of London", 16500.0, 4.5),
        ("Park Plaza Westminster Bridge", 19000.0, 4.4),
        ("Premier Inn London County Hall", 11500.0, 4.3),
        ("Ibis London Blackfriars", 9200.0, 4.1),
        ("Wombat's City Hostel London", 3900.0, 4.4),
        ("Generator London Russell Square", 3500.0, 4.2),
    ],
    ("New York City", "United States"): [
        ("The Plaza Hotel Fifth Avenue", 88000.0, 4.8),
        ("The Carlyle, A Rosewood Hotel", 82000.0, 4.9),
        ("The Greenwich Hotel Tribeca", 75000.0, 4.8),
        ("The Standard High Line Meatpacking", 38000.0, 4.5),
        ("1 Hotel Brooklyn Bridge", 45000.0, 4.7),
        ("Arlo SoHo Boutique Hotel", 26000.0, 4.5),
        ("CitizenM New York Bowery", 19500.0, 4.5),
        ("Moxy NYC Times Square", 22000.0, 4.3),
        ("POD 39 Midtown East", 14000.0, 4.2),
        ("Hilton Garden Inn Manhattan Chelsea", 17500.0, 4.2),
        ("HI NYC Hostel Upper West Side", 5200.0, 4.4),
        ("Freehand New York Flatiron", 7500.0, 4.3),
    ],
    ("Rome", "Italy"): [
        ("Hotel de Russie, Rocco Forte Hotel", 78000.0, 4.9),
        ("Hotel Eden - Dorchester Collection", 72000.0, 4.8),
        ("The St. Regis Rome", 68000.0, 4.8),
        ("J.K. Place Roma", 55000.0, 4.9),
        ("Babuino 181 Luxury Boutique Hotel", 28000.0, 4.7),
        ("The Hoxton Rome - Parioli", 18500.0, 4.6),
        ("Hotel Quirinale Rome", 14000.0, 4.3),
        ("iQ Hotel Roma", 16000.0, 4.6),
        ("Hotel Forum Roma", 15500.0, 4.4),
        ("Hotel Canada, BW Premier Collection", 9800.0, 4.3),
        ("The RomeHello Hostel & Social Hub", 3800.0, 4.7),
        ("YellowSquare Rome Backpacker Hub", 3200.0, 4.4),
    ],
    ("Dubai", "United Arab Emirates"): [
        ("Burj Al Arab Jumeirah", 115000.0, 4.9),
        ("Atlantis The Royal Palm Jumeirah", 85000.0, 4.9),
        ("Armani Hotel Dubai - Burj Khalifa", 58000.0, 4.8),
        ("One&Only Royal Mirage Resort Dubai", 48000.0, 4.8),
        ("Address Downtown Dubai", 36000.0, 4.7),
        ("Palace Downtown Dubai", 32000.0, 4.7),
        ("JW Marriott Marquis Hotel Dubai", 16500.0, 4.6),
        ("Rove Downtown Dubai", 8500.0, 4.5),
        ("Aloft Palm Jumeirah", 11000.0, 4.4),
        ("Holiday Inn Express Dubai Airport", 5800.0, 4.2),
        ("Premier Inn Dubai International Airport", 4800.0, 4.2),
        ("Green Sky Hostel Dubai Marina", 2200.0, 4.3),
    ],
    ("Singapore", "Singapore"): [
        ("Marina Bay Sands Singapore", 58000.0, 4.8),
        ("Raffles Hotel Singapore", 75000.0, 4.9),
        ("The Fullerton Hotel Singapore", 36000.0, 4.8),
        ("Capella Singapore - Sentosa Island", 62000.0, 4.9),
        ("PARKROYAL COLLECTION Marina Bay", 24000.0, 4.7),
        ("The Clan Hotel Singapore", 21000.0, 4.7),
        ("Oasia Hotel Downtown Singapore", 16000.0, 4.5),
        ("YOTEL Singapore Orchard Road", 13500.0, 4.4),
        ("Hotel G Singapore", 9800.0, 4.2),
        ("Ibis on Bencoolen Singapore", 8900.0, 4.2),
        ("The Pod Boutique Capsule Hotel", 3600.0, 4.5),
        ("KINN Capsule Hotel Singapore River", 3200.0, 4.4),
    ],
    ("Sydney", "Australia"): [
        ("Park Hyatt Sydney - The Rocks", 78000.0, 4.9),
        ("Crown Towers Sydney - Barangaroo", 62000.0, 4.8),
        ("The Langham Sydney", 45000.0, 4.8),
        ("Four Seasons Hotel Sydney", 36000.0, 4.7),
        ("Ovolo 1888 Darling Harbour", 22000.0, 4.6),
        ("The Old Clare Hotel Chippendale", 19500.0, 4.5),
        ("Rydges Sydney Harbour", 16000.0, 4.3),
        ("Veriu Broadway Boutique Suites", 14500.0, 4.4),
        ("Mercure Sydney Central", 12000.0, 4.2),
        ("Ibis Sydney Darling Harbour", 9500.0, 4.1),
        ("Wake Up! Sydney Central Hostel", 3800.0, 4.5),
        ("YHA Sydney Harbour The Rocks", 4200.0, 4.6),
    ],
    ("Bangkok", "Thailand"): [
        ("Mandarin Oriental Bangkok", 48000.0, 4.9),
        ("The Siam Hotel Riverside", 52000.0, 4.9),
        ("The Peninsula Bangkok", 32000.0, 4.8),
        ("Capella Bangkok - Charoenkrung", 45000.0, 4.9),
        ("SO/ Bangkok - Lumphini Park", 18500.0, 4.7),
        ("Banyan Tree Bangkok", 16000.0, 4.6),
        ("Amara Bangkok Hotel", 8500.0, 4.4),
        ("Eastin Grand Hotel Phayathai", 9500.0, 4.6),
        ("Ibis Styles Bangkok Silom", 4200.0, 4.2),
        ("Lub d Bangkok Siam Backpacker", 1600.0, 4.5),
        ("Mad Monkey Hostel Bangkok", 1200.0, 4.4),
        ("Bed Station Hostel Khaosan", 1100.0, 4.5),
    ],
    ("Cape Town", "South Africa"): [
        ("The Silo Hotel V&A Waterfront", 68000.0, 4.9),
        ("Belmond Mount Nelson Hotel", 45000.0, 4.8),
        ("One&Only Cape Town", 48000.0, 4.8),
        ("Cape Grace, A Fairmont Managed Hotel", 42000.0, 4.7),
        ("The Twelve Apostles Hotel & Spa", 32000.0, 4.7),
        ("Radisson RED Hotel V&A Waterfront", 16000.0, 4.5),
        ("Victoria & Alfred Hotel", 18500.0, 4.6),
        ("Protea Hotel by Marriott Cape Town Waterfront", 9800.0, 4.3),
        ("City Lodge Hotel V&A Waterfront", 7500.0, 4.2),
        ("Mojo Hotel & Market Sea Point", 4500.0, 4.3),
        ("Never@home Kloof Street Hostel", 2200.0, 4.5),
        ("91 Loop Boutique Backpacker Hostel", 1800.0, 4.4),
    ],
    ("Cairo", "Egypt"): [
        ("Mena House Hotel Giza Pyramids", 34000.0, 4.8),
        ("Four Seasons Hotel Cairo at Nile Plaza", 38000.0, 4.8),
        ("The Nile Ritz-Carlton, Cairo", 32000.0, 4.7),
        ("Kempinski Nile Hotel Cairo", 22000.0, 4.6),
        ("Sofitel Cairo Nile El Gezirah", 24000.0, 4.6),
        ("Steigenberger Hotel El Tahrir Cairo", 12500.0, 4.5),
        ("Le Rêve Boutique Hotel Cairo", 6800.0, 4.4),
        ("Grand Nile Tower Hotel", 9500.0, 4.3),
        ("Cairo Marriott Hotel & Omar Khayyam Casino", 14000.0, 4.5),
        ("Tahrir Square Downtown Hotel", 3600.0, 4.2),
        ("Dahab Hostel Downtown Cairo", 1200.0, 4.4),
        ("Holy Sheet Hostel Cairo", 1100.0, 4.5),
    ],
}

# Regional naming building blocks for procedural generation
REGIONAL_PROFILES: Dict[str, Dict[str, List[str]]] = {
    "India_Heritage": {
        "luxury_prefixes": ["The Grand", "Taj", "Welcomhotel by ITC", "The Oberoi", "Royal", "Heritage Palace", "Maharaja's", "Imperial"],
        "luxury_suffixes": ["Palace Resort & Spa", "Heritage Grand", "Vilas & Suites", "Royal Retreat", "Mahal Palace"],
        "upscale_prefixes": ["Fortune Select", "Radisson", "Lemon Tree Premier", "Sarovar Premiere", "Regenta Central", "Umaid", "Clarks"],
        "upscale_suffixes": ["Haveli & Spa", "Heritage Inn", "Boutique Stay", "Grand Residency", "Resort & Suites"],
        "mid_prefixes": ["Treebo Trend", "Ginger", "The Fern Residency", "Hotel Surya", "Hotel Landmark", "Pai", "Ambassador"],
        "mid_suffixes": ["Comfort Inn", "City Center Hotel", "Regency", "Executive Suites", "Manor Hotel"],
        "economy_prefixes": ["Zostel", "The Hosteller", "Moustache", "Gostops", "Cozy Nest", "Green Palm", "Traveler's Den"],
        "economy_suffixes": ["Homestay & Cafe", "Backpacker Hostel", "Guest House", "Tourist Home", "Boutique B&B"],
    },
    "India_Coastal": {
        "luxury_prefixes": ["The Leela", "Taj", "Grand Hyatt", "Marriott Resort", "Alila", "Coconut Lagoon", "Heritage Beach"],
        "luxury_suffixes": ["Cove Resort & Spa", "Waterfront Palace", "Beachside Sanctuary", "Lagoon Villa Retreat"],
        "upscale_prefixes": ["Radisson Blu", "CGH Earth", "Fragrant Nature", "Sterling", "Estuary", "Turtle Beach", "Seagull"],
        "upscale_suffixes": ["Beach Resort", "Backwater Retreat", "Coastline Boutique Stay", "Lighthouse Inn"],
        "mid_prefixes": ["Keys Lite", "Ginger", "Hotel Sea View", "Ocean Crest", "Arabian Sands", "Bay Breeze"],
        "mid_suffixes": ["Residency", "Coastal Inn", "Marine View Hotel", "Waterfront Suites"],
        "economy_prefixes": ["Zostel", "The Hosteller", "Cliff View", "Palm Shade", "Beach Shack &", "Fisherman's"],
        "economy_suffixes": ["Homestay", "Hostel & Hub", "Cottages & Cafe", "B&B Retreat"],
    },
    "India_Hill": {
        "luxury_prefixes": ["Wildflower Hall", "The Tamara", "Taj", "Welcomhotel", "Glenview", "Evolve Back", "Himalayan"],
        "luxury_suffixes": ["Resort & Mountain Spa", "Cloud Retreat", "Alpine Heritage Lodge", "Valley View Sanctuary"],
        "upscale_prefixes": ["Sterling", "The Fern", "Club Mahindra", "Pine & Cedar", "Misty Heights", "Cliff View"],
        "upscale_suffixes": ["Mountain Resort", "Hillside Boutique Stay", "Highland Manor", "Valley Crest Retreat"],
        "mid_prefixes": ["Treebo Trend", "Hotel Pine Wood", "Snow Crest", "Mountain Echoes", "Cedar Inn"],
        "mid_suffixes": ["Heights Hotel", "View Residency", "Alpine Inn", "Lodge & Suites"],
        "economy_prefixes": ["Zostel", "The Hosteller", "Gostops", "Pine Woods", "Backpacker's", "Mountain Wanderer"],
        "economy_suffixes": ["Homestay", "Hostel & Cafe", "Trekkers Lodge", "Valley Nest"],
    },
    "India_Standard": {
        "luxury_prefixes": ["ITC Grand", "Taj", "The Leela", "JW Marriott", "Hyatt Regency", "Radisson Blu Plaza"],
        "luxury_suffixes": ["Palace Hotel", "Suites & Spa", "Grand Hotel & Convention", "Regency Luxury"],
        "upscale_prefixes": ["Novotel", "Courtyard by Marriott", "Lemon Tree Premier", "Fortune Park", "Holiday Inn", "The Pride"],
        "upscale_suffixes": ["Executive Hotel", "Business Suites", "Boutique Inn", "Grand Residency"],
        "mid_prefixes": ["Ginger", "Fairfield by Marriott", "Treebo Trend", "Ibis", "Hotel Park View", "The Central"],
        "mid_suffixes": ["Express Hotel", "City Inn", "Plaza Hotel", "Executive Stay"],
        "economy_prefixes": ["Zostel", "The Hosteller", "FabHotel", "Gostops", "Cozy Corner", "Urban Stay"],
        "economy_suffixes": ["Hostel", "Guest House", "Tourist Inn", "Homestay"],
    },
    "Europe": {
        "luxury_prefixes": ["Grand Hotel", "The Ritz-Carlton", "Four Seasons", "Hotel de", "Palace Hotel", "Villa", "Relais & Châteaux"],
        "luxury_suffixes": ["Palace & Spa", "Luxury Collection", "Resort & Wellness", "Grand Suites", "Historic Manor"],
        "upscale_prefixes": ["Radisson Collection", "Novotel", "Mercure", "NH Collection", "Crowne Plaza", "Boutique Hotel", "Hotel Victoria"],
        "upscale_suffixes": ["Boutique Suites", "Old Town Hotel", "Riverside Inn", "Central Suites", "Heritage House"],
        "mid_prefixes": ["Ibis Styles", "Holiday Inn Express", "Best Western Plus", "Motel One", "CitizenM", "Hotel Leonardo"],
        "mid_suffixes": ["City Center", "Plaza Hotel", "Express Inn", "Station Hotel", "Comfort Suites"],
        "economy_prefixes": ["Generator", "Wombat's City", "A&O", "Meininger", "The People", "St Christopher's", "Old City"],
        "economy_suffixes": ["Hostel & Bar", "City Backpacker", "B&B Suites", "Guesthouse", "Pension"],
    },
    "East_Asia": {
        "luxury_prefixes": ["The Peninsula", "Aman", "Mandarin Oriental", "Shangri-La", "Park Hyatt", "Grand Palace", "Hoshinoya"],
        "luxury_suffixes": ["Luxury Hotel & Spa", "Grand Tower", "Riverside Palace", "Garden Resort", "Bay Suites"],
        "upscale_prefixes": ["Lotte Hotel", "Hotel Okura", "Prince Hotel", "Radisson Blu", "Sotetsu Grand", "Millennium"],
        "upscale_suffixes": ["Boutique Suites", "Harbor Hotel", "City Landmark Hotel", "Modern Inn", "Garden Wing"],
        "mid_prefixes": ["APA Hotel", "Daiwa Roynet", "Dormy Inn", "Toyoko Inn", "Ibis Ambassador", "Hotel Gracery"],
        "mid_suffixes": ["Ekimae Tower", "City Central", "Comfort Hotel", "Express Suites", "Plaza"],
        "economy_prefixes": ["Nui.", "UNPLAN", "Khaosan", "Space Capsule", "Backpacker's Nest", "Green Garden"],
        "economy_prefixes_alt": ["Hostel & Lounge", "Capsule Hotel", "Boutique Guesthouse", "Inn & Cafe"],
        "economy_suffixes": ["Hostel & Lounge", "Capsule Hotel", "Boutique Guesthouse", "Inn & Cafe"],
    },
    "SE_Asia": {
        "luxury_prefixes": ["Anantara", "The Siam", "Capella", "Banyan Tree", "Rosewood", "Amari", "Sofitel Legend"],
        "luxury_suffixes": ["Resort & Spa", "Villas & Retreat", "Palace Suites", "Heritage Sanctuary"],
        "upscale_prefixes": ["Centara Grand", "Avani+", "Pullman", "Pan Pacific", "Novotel", "Dusit Princess"],
        "upscale_suffixes": ["Boutique Resort", "Riverside Hotel", "City Suites", "Tropical Haven"],
        "mid_prefixes": ["Ibis Styles", "Holiday Inn Express", "U Hotel", "Citadines", "Hotel Royal", "Mercure"],
        "mid_suffixes": ["Center Inn", "Express Suites", "Terrace Hotel", "Urban Stay"],
        "economy_prefixes": ["Mad Monkey", "Lub d", "Bed Station", "Slumber Party", "Social Hub", "Tropical Palm"],
        "economy_suffixes": ["Backpacker Hostel", "Boutique Hostels", "Guesthouse & Bar", "Homestay Retreat"],
    },
    "Americas": {
        "luxury_prefixes": ["The Ritz-Carlton", "Four Seasons", "St. Regis", "1 Hotel", "Fairmont", "The Langham"],
        "luxury_suffixes": ["Resort & Club", "Grand Suites", "Luxury Tower", "Waterfront Lodge"],
        "upscale_prefixes": ["Omni", "Westin", "Kimpton", "Hyatt Centric", "Le Germain", "Loews", "Marriott"],
        "upscale_suffixes": ["Boutique Hotel", "Harbor Suites", "Downtown Hotel", "Manor & Spa"],
        "mid_prefixes": ["Hampton by Hilton", "Courtyard by Marriott", "Hilton Garden Inn", "Fairfield Inn", "Aloft"],
        "mid_suffixes": ["Suites", "City Center", "Inn & Suites", "Plaza Hotel"],
        "economy_prefixes": ["Freehand", "HI Hostel", "USA Hostels", "Pod Hotel", "Urban Nomad", "Cozy Haven"],
        "economy_suffixes": ["Hostel", "Micro Hotel", "Boutique Lodge", "Inn & Cafe"],
    },
    "MENA_Africa": {
        "luxury_prefixes": ["Kempinski", "Four Seasons", "The Silo", "Jumeirah", "One&Only", "Sofitel", "Al Bustan"],
        "luxury_suffixes": ["Palace & Spa", "Resort & Club", "Oasis Retreat", "Royal Tower"],
        "upscale_prefixes": ["Radisson Blu", "Steigenberger", "Mövenpick", "Protea Hotel by Marriott", "Rotana", "Millennium"],
        "upscale_suffixes": ["Waterfront Hotel", "Resort & Suites", "Grand Palace", "Downtown Hotel"],
        "mid_prefixes": ["Rove", "City Lodge", "Ibis", "Holiday Inn", "Aloft", "Tulip Inn"],
        "mid_suffixes": ["Express Hotel", "Central Suites", "City Inn", "Urban Stay"],
        "economy_prefixes": ["Never@home", "Dahab", "Urban Oasis", "Old Town", "Boutique Riad", "Nomad"],
        "economy_suffixes": ["Hostel & Hub", "Backpacker Lodge", "Guesthouse", "Traditional Inn"],
    },
    "Oceania": {
        "luxury_prefixes": ["Park Hyatt", "Crown Towers", "The Langham", "Qualia", "Spicers", "QT"],
        "luxury_suffixes": ["Harbour Resort & Spa", "Lodge & Sanctuary", "Boutique Luxury", "Grand Tower"],
        "upscale_prefixes": ["Ovolo", "Rydges", "Mantra", "Pullman", "Novotel", "Meriton Suites"],
        "upscale_suffixes": ["Boutique Hotel", "Harbour Suites", "Beach Resort", "Waterfront Inn"],
        "mid_prefixes": ["Ibis", "Travelodge Hotel", "Mercure", "Quest Apartment Hotels", "The Sebel"],
        "mid_suffixes": ["Central", "Apartments & Suites", "Plaza", "Express Hotel"],
        "economy_prefixes": ["Wake Up!", "YHA Australia", "Space Hotel", "Base Backpackers", "Nomads", "Pacific Breeze"],
        "economy_suffixes": ["Hostel & Bar", "Backpackers Hub", "Lodge", "B&B Suites"],
    },
}

def determine_region_key(city: str, country: str) -> str:
    """Determines the appropriate regional naming profile."""
    country_lower = country.lower().strip()
    city_lower = city.lower().strip()

    if country_lower == "india":
        coastal_cities = {
            "kochi", "goa", "mumbai", "chennai", "pondicherry", "varkala", "kovalam", "kumarakom",
            "alleppey", "puri", "daman", "diu", "karwar", "murudeshwar", "gokarna", "mangalore",
            "alibaug", "ratnagiri", "ganpatipule", "kashid", "havelock island", "neil island",
            "port blair", "visakhapatnam", "kanyakumari", "rameswaram", "dhanushkodi", "mahabalipuram"
        }
        hill_cities = {
            "shimla", "manali", "dharamshala", "leh", "srinagar", "gulmarg", "pahalgam",
            "mount abu", "coorg", "chikmagalur", "kabini", "bandipur", "munnar", "wayanad",
            "thekkady", "ooty", "kodaikanal", "coonoor", "yelagiri", "yercaud", "valparai",
            "darjeeling", "kalimpong", "gangtok", "pelling", "shillong", "cherrapunji",
            "tawang", "mussoorie", "nainital", "rishikesh", "haridwar", "kasol", "kaza",
            "spiti", "jibhi", "dalhousie", "khajjiar", "ranikhet", "kausani", "almora",
            "mukteshwar", "lansdowne", "chopta", "auli", "bir billing", "dhanaulti", "kanatal",
            "chakrata", "bhimtal", "pachmarhi", "saputara", "mahabaleshwar", "panchgani",
            "lonavala", "khandala", "matheran", "lavasa", "igatpuri", "bhandardara"
        }
        heritage_cities = {
            "jaipur", "udaipur", "jodhpur", "jaisalmer", "pushkar", "bikaner", "kumbhalgarh",
            "mandu", "hampi", "badami", "belur", "mysuru", "agra", "varanasi", "khajuraho",
            "orchha", "gwalior", "chittorgarh", "ajmer", "alwar", "shekhawati", "bundi",
            "rann of kutch", "bhuj", "patna", "gaya", "bodh gaya", "rajgir", "nalanda",
            "thanjavur", "madurai", "tiruchirappalli", "chettinad", "kanchipuram"
        }

        if city_lower in coastal_cities:
            return "India_Coastal"
        elif city_lower in hill_cities:
            return "India_Hill"
        elif city_lower in heritage_cities:
            return "India_Heritage"
        else:
            return "India_Standard"

    european_countries = {
        "france", "italy", "germany", "spain", "united kingdom", "greece", "switzerland",
        "austria", "portugal", "netherlands", "belgium", "norway", "sweden", "finland",
        "denmark", "ireland", "croatia", "czech republic", "hungary", "poland", "iceland",
        "turkey", "slovenia", "estonia", "latvia", "lithuania", "malta", "cyprus", "monaco"
    }
    if country_lower in european_countries:
        return "Europe"

    east_asia = {"japan", "south korea", "china", "taiwan", "hong kong", "macau"}
    if country_lower in east_asia:
        return "East_Asia"

    se_asia = {"thailand", "vietnam", "indonesia", "malaysia", "philippines", "cambodia", "laos", "myanmar", "singapore"}
    if country_lower in se_asia:
        return "SE_Asia"

    americas = {"united states", "canada", "mexico", "costa rica", "panama", "brazil", "argentina", "peru", "chile", "colombia", "ecuador", "jamaica", "bahamas", "cuba", "dominican republic"}
    if country_lower in americas:
        return "Americas"

    mena_africa = {
        "united arab emirates", "egypt", "saudi arabia", "qatar", "oman", "jordan", "israel",
        "morocco", "south africa", "kenya", "tanzania", "mauritius", "seychelles", "maldives",
        "namibia", "zimbabwe", "botswana", "madagascar"
    }
    if country_lower in mena_africa:
        return "MENA_Africa"

    oceania = {"australia", "new zealand", "fiji", "french polynesia", "vanuatu", "samoa"}
    if country_lower in oceania:
        return "Oceania"

    return "Europe"


def generate_hotel_catalog_for_destinations(
    destinations: List[Tuple[int, str, str, Optional[float]]]
) -> Dict[Tuple[str, str], List[Tuple[str, float, float]]]:
    """Generates a complete dictionary of 12 hotels per destination for all 500 destinations.
    
    Returns:
        Dict mapping (city, country) to list of (name, price_per_night, rating).
    """
    catalog: Dict[Tuple[str, str], List[Tuple[str, float, float]]] = {}

    for dest_id, city, country, avg_daily_cost in destinations:
        dest_key = (city, country)

        # Check if already curated in landmark dictionary
        if dest_key in CURATED_LANDMARK_HOTELS:
            curated_list = list(CURATED_LANDMARK_HOTELS[dest_key])
            catalog[dest_key] = curated_list
            continue

        # Procedural deterministic generation
        region_key = determine_region_key(city, country)
        profile = REGIONAL_PROFILES[region_key]

        # Use deterministic PRNG seeded with city and country
        hash_seed = int(hashlib.sha256(f"{city}_{country}_{RANDOM_SEED}".encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(hash_seed)

        # Baseline cost factor
        daily_cost = float(avg_daily_cost) if avg_daily_cost and avg_daily_cost > 0 else 5000.0

        # Tier multipliers & rating ranges:
        # Tier 1 (Ultra Luxury 5-Star / Palace / Resort): 2.5x to 4.5x daily cost
        # Tier 2 (Grand Luxury 5-Star): 1.8x to 2.8x daily cost
        # Tier 3 (Boutique Upscale 4-Star): 1.1x to 1.7x daily cost
        # Tier 4 (Contemporary 4-Star): 0.85x to 1.3x daily cost
        # Tier 5 (Scenic / Waterfront 4-Star): 0.9x to 1.4x daily cost
        # Tier 6 (Central 3-Star Business): 0.55x to 0.85x daily cost
        # Tier 7 (Express 3-Star): 0.45x to 0.7x daily cost
        # Tier 8 (Cozy Family Hotel 3-Star): 0.4x to 0.65x daily cost
        # Tier 9 (Old Quarter / Landmark 3-Star): 0.45x to 0.75x daily cost
        # Tier 10 (Design Backpacker Hostel): 0.18x to 0.35x daily cost (min 600)
        # Tier 11 (Boutique Guesthouse / B&B): 0.22x to 0.4x daily cost (min 750)
        # Tier 12 (Homestay / Traveler Lodge): 0.15x to 0.3x daily cost (min 500)

        hotel_list: List[Tuple[str, float, float]] = []
        used_names: Set[str] = set()

        # Helper to generate unique hotel name
        def make_unique_name(name_candidate: str) -> str:
            clean_name = name_candidate.strip()
            if clean_name not in used_names:
                used_names.add(clean_name)
                return clean_name
            alt_name = f"{clean_name} {city}"
            if alt_name not in used_names:
                used_names.add(alt_name)
                return alt_name
            alt_name2 = f"{clean_name} Hotel & Suites"
            used_names.add(alt_name2)
            return alt_name2

        # 1. Ultra Luxury
        lux_p = rng.choice(profile["luxury_prefixes"])
        lux_s = rng.choice(profile["luxury_suffixes"])
        name_1 = make_unique_name(f"{lux_p} {city} {lux_s}")
        price_1 = round(daily_cost * rng.uniform(2.6, 4.2) / 50.0) * 50.0
        rate_1 = round(rng.uniform(4.7, 4.9), 1)
        hotel_list.append((name_1, max(price_1, 6000.0), rate_1))

        # 2. Grand Luxury
        lux_p2 = rng.choice([p for p in profile["luxury_prefixes"] if p != lux_p] or profile["luxury_prefixes"])
        name_2 = make_unique_name(f"{lux_p2} Grand Hotel {city}")
        price_2 = round(daily_cost * rng.uniform(1.8, 2.7) / 50.0) * 50.0
        rate_2 = round(rng.uniform(4.6, 4.8), 1)
        hotel_list.append((name_2, max(price_2, 4500.0), rate_2))

        # 3. Boutique Upscale 4-Star
        up_p = rng.choice(profile["upscale_prefixes"])
        up_s = rng.choice(profile["upscale_suffixes"])
        name_3 = make_unique_name(f"{up_p} {city} {up_s}")
        price_3 = round(daily_cost * rng.uniform(1.1, 1.65) / 50.0) * 50.0
        rate_3 = round(rng.uniform(4.4, 4.7), 1)
        hotel_list.append((name_3, max(price_3, 3200.0), rate_3))

        # 4. Contemporary 4-Star
        up_p2 = rng.choice([p for p in profile["upscale_prefixes"] if p != up_p] or profile["upscale_prefixes"])
        name_4 = make_unique_name(f"{up_p2} {city} Central")
        price_4 = round(daily_cost * rng.uniform(0.9, 1.35) / 50.0) * 50.0
        rate_4 = round(rng.uniform(4.3, 4.6), 1)
        hotel_list.append((name_4, max(price_4, 2800.0), rate_4))

        # 5. Scenic / Waterfront / Garden 4-Star
        name_5 = make_unique_name(f"{city} Panorama Resort & Suites")
        price_5 = round(daily_cost * rng.uniform(0.95, 1.45) / 50.0) * 50.0
        rate_5 = round(rng.uniform(4.3, 4.6), 1)
        hotel_list.append((name_5, max(price_5, 2900.0), rate_5))

        # 6. Central 3-Star Business
        mid_p = rng.choice(profile["mid_prefixes"])
        mid_s = rng.choice(profile["mid_suffixes"])
        name_6 = make_unique_name(f"{mid_p} {city} {mid_s}")
        price_6 = round(daily_cost * rng.uniform(0.55, 0.85) / 50.0) * 50.0
        rate_6 = round(rng.uniform(4.1, 4.4), 1)
        hotel_list.append((name_6, max(price_6, 1800.0), rate_6))

        # 7. Express 3-Star
        mid_p2 = rng.choice([p for p in profile["mid_prefixes"] if p != mid_p] or profile["mid_prefixes"])
        name_7 = make_unique_name(f"{mid_p2} {city} Downtown")
        price_7 = round(daily_cost * rng.uniform(0.48, 0.72) / 50.0) * 50.0
        rate_7 = round(rng.uniform(4.0, 4.3), 1)
        hotel_list.append((name_7, max(price_7, 1600.0), rate_7))

        # 8. Cozy Family Hotel 3-Star
        name_8 = make_unique_name(f"Hotel {city} Courtyard")
        price_8 = round(daily_cost * rng.uniform(0.42, 0.65) / 50.0) * 50.0
        rate_8 = round(rng.uniform(4.0, 4.3), 1)
        hotel_list.append((name_8, max(price_8, 1400.0), rate_8))

        # 9. Old Town / Heritage 3-Star
        name_9 = make_unique_name(f"The Old Town Inn {city}")
        price_9 = round(daily_cost * rng.uniform(0.45, 0.75) / 50.0) * 50.0
        rate_9 = round(rng.uniform(4.1, 4.4), 1)
        hotel_list.append((name_9, max(price_9, 1500.0), rate_9))

        # 10. Design Backpacker Hostel
        eco_p = rng.choice(profile["economy_prefixes"])
        eco_s = rng.choice(profile["economy_suffixes"])
        name_10 = make_unique_name(f"{eco_p} {city}")
        price_10 = round(daily_cost * rng.uniform(0.18, 0.32) / 10.0) * 10.0
        rate_10 = round(rng.uniform(4.2, 4.6), 1)
        hotel_list.append((name_10, max(price_10, 650.0), rate_10))

        # 11. Boutique Guesthouse / B&B
        eco_p2 = rng.choice([p for p in profile["economy_prefixes"] if p != eco_p] or profile["economy_prefixes"])
        name_11 = make_unique_name(f"{eco_p2} {city} {eco_s}")
        price_11 = round(daily_cost * rng.uniform(0.22, 0.38) / 10.0) * 10.0
        rate_11 = round(rng.uniform(3.9, 4.3), 1)
        hotel_list.append((name_11, max(price_11, 750.0), rate_11))

        # 12. Homestay / Traveler's Den
        name_12 = make_unique_name(f"{city} Green Oasis Homestay")
        price_12 = round(daily_cost * rng.uniform(0.16, 0.28) / 10.0) * 10.0
        rate_12 = round(rng.uniform(3.8, 4.2), 1)
        hotel_list.append((name_12, max(price_12, 550.0), rate_12))

        catalog[dest_key] = hotel_list

    return catalog
