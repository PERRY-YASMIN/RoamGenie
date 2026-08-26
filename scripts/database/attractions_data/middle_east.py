"""Attractions for 34 Middle Eastern & North African destinations in RoamGenie (Phase D2)."""
from typing import Dict, List, Tuple

# Format: (name, category, entry_fee_inr, rating)
MIDDLE_EAST_ATTRACTIONS: Dict[Tuple[str, str], List[Tuple[str, str, float, float]]] = {
    # United Arab Emirates (4)
    ("Dubai", "United Arab Emirates"): [
        ("Burj Khalifa Level 124/125 Observation Deck", "viewpoint", 3800.00, 4.8),
        ("The Dubai Mall & Dubai Fountain Show", "cultural", 0.00, 4.9),
        ("Museum of the Future Arabic Calligraphy Ring", "museum", 3400.00, 4.8),
        ("Dubai Desert Conservation Reserve Dune Bashing", "adventure", 4500.00, 4.9),
        ("Dubai Creek & Historic Al Fahidi Gold/Spice Souqs", "market", 20.00, 4.7),
        ("Palm Jumeirah & The View at The Palm", "viewpoint", 2200.00, 4.7),
    ],
    ("Abu Dhabi", "United Arab Emirates"): [
        ("Sheikh Zayed Grand Mosque Pure White Marble", "religious", 0.00, 5.0),
        ("Louvre Abu Dhabi Floating Dome Museum", "museum", 1500.00, 4.9),
        ("Qasr Al Watan Presidential Palace & Light Show", "palace", 1500.00, 4.8),
        ("Ferrari World Yas Island (Formula Rossa Coaster)", "park", 7500.00, 4.7),
        ("Corniche Beach & Waterfront Promenade", "beach", 0.00, 4.6),
    ],
    ("Sharjah", "United Arab Emirates"): [
        ("Sharjah Museum of Islamic Civilization", "museum", 250.00, 4.8),
        ("Al Noor Mosque on Khalid Lagoon", "religious", 0.00, 4.7),
        ("Heart of Sharjah Heritage District & Souq Al Shanasiyah", "heritage", 0.00, 4.6),
        ("Sharjah Art Museum & Rain Room Experience", "cultural", 600.00, 4.7),
        ("Al Majaz Waterfront Musical Fountain", "viewpoint", 0.00, 4.6),
    ],
    ("Ras Al Khaimah", "United Arab Emirates"): [
        ("Jebel Jais (World's Longest Zipline 2.83km)", "adventure", 8500.00, 5.0),
        ("Jebel Jais Viewing Deck Park & Mountain Switchbacks", "viewpoint", 450.00, 4.8),
        ("Dhayah Fort Only Hilltop Fort in UAE", "fort", 0.00, 4.6),
        ("Suwaidi Pearl Farm Traditional Boat Tour", "cultural", 3500.00, 4.7),
        ("Al Marjan Island Coral Beach Resorts", "beach", 0.00, 4.6),
    ],

    # Saudi Arabia, Qatar, Oman, Bahrain & Kuwait (9)
    ("Riyadh", "Saudi Arabia"): [
        ("Kingdom Centre Sky Bridge (300m Lookout)", "viewpoint", 1600.00, 4.7),
        ("Al Masmak Historic Clay & Mud-Brick Fortress", "fort", 0.00, 4.7),
        ("Diriyah & At-Turaif UNESCO Heritage Mud Citadel", "heritage", 1100.00, 4.9),
        ("National Museum of Saudi Arabia", "museum", 220.00, 4.8),
        ("Souq Al Zal Traditional Antique & Oud Market", "market", 0.00, 4.6),
    ],
    ("Jeddah", "Saudi Arabia"): [
        ("Al-Balad UNESCO Historic Coral Stone Quarter", "heritage", 0.00, 4.9),
        ("King Fahd's Fountain (World's Tallest Water Fountain)", "monument", 0.00, 4.8),
        ("Jeddah Corniche & Floating Mosque (Al Rahma)", "religious", 0.00, 4.7),
        ("Tayebat International City Museum", "museum", 1800.00, 4.7),
        ("Red Sea Scuba Diving & Coral Reef Safari", "adventure", 6500.00, 4.9),
    ],
    ("AlUla", "Saudi Arabia"): [
        ("Hegra (Madain Salih) UNESCO Nabataean Tomb Facades", "heritage", 2200.00, 5.0),
        ("Elephant Rock (Jabal AlFil) Giant Sandstone Monolith", "nature", 0.00, 4.9),
        ("Maraya Concert Hall (World's Largest Mirrored Building)", "architecture", 0.00, 4.9),
        ("AlUla Old Town Labyrinth of Mudbrick Houses", "historical", 0.00, 4.7),
        ("Dadan & Jabal Ikmah Ancient Inscriptions Library", "historical", 1500.00, 4.8),
    ],
    ("Medina", "Saudi Arabia"): [
        ("Al-Masjid an-Nabawi (The Prophet's Sacred Mosque)", "religious", 0.00, 5.0),
        ("Quba Mosque (Oldest Mosque in Islamic History)", "religious", 0.00, 4.9),
        ("Mount Uhud Battle Site & Archers' Hill", "historical", 0.00, 4.8),
        ("Dar Al Madinah Museum of Cultural Heritage", "museum", 450.00, 4.7),
        ("Seven Mosques (Masajid Sab'ah) Historic Trench Area", "religious", 0.00, 4.6),
    ],
    ("Doha", "Qatar"): [
        ("Souq Waqif Falcon Souq & Traditional Alleyways", "market", 0.00, 4.9),
        ("Museum of Islamic Art (MIA) by I.M. Pei", "museum", 1100.00, 4.9),
        ("Katara Cultural Village & Greek-Style Amphitheater", "cultural", 0.00, 4.7),
        ("National Museum of Qatar (Desert Rose Architecture)", "museum", 1100.00, 4.9),
        ("Doha Corniche Traditional Dhow Harbour Cruise", "nature", 1200.00, 4.7),
    ],
    ("Muscat", "Oman"): [
        ("Sultan Qaboos Grand Mosque & Persian Carpet", "religious", 0.00, 5.0),
        ("Royal Opera House Muscat Architectural Tour", "architecture", 700.00, 4.8),
        ("Mutrah Souq & Waterfront Corniche Promenade", "market", 0.00, 4.7),
        ("Al Jalali and Al Mirani 16th-Century Portuguese Forts", "fort", 0.00, 4.6),
        ("Bait Al Zubair Omani Heritage Museum", "museum", 600.00, 4.6),
    ],
    ("Salalah", "Oman"): [
        ("Sultan Qaboos Mosque Salalah & Frankincense Groves", "religious", 0.00, 4.8),
        ("Wadi Darbat Emerald Waterfalls & Camel Grazing", "nature", 0.00, 5.0),
        ("Al Mughsail Beach & Marneef Cave Natural Blowholes", "nature", 0.00, 4.9),
        ("Land of Frankincense UNESCO Archaeological Park (Al Baleed)", "heritage", 400.00, 4.8),
        ("Taqah Castle Historic Omani Fortification", "fort", 200.00, 4.6),
    ],
    ("Manama", "Bahrain"): [
        ("Bab Al Bahrain & Historic Manama Souq", "market", 0.00, 4.7),
        ("Al Fateh Grand Mosque (One of World's Largest)", "religious", 0.00, 4.8),
        ("Bahrain National Museum & Dilmun Civilization", "museum", 250.00, 4.8),
        ("Qal'at al-Bahrain (Bahrain Fort UNESCO)", "fort", 0.00, 4.8),
        ("Tree of Life (Sharajat-al-Hayat in Desert)", "nature", 0.00, 4.4),
    ],
    ("Kuwait City", "Kuwait"): [
        ("Kuwait Towers Rotating Sphere Observation Deck", "viewpoint", 800.00, 4.7),
        ("Grand Mosque of Kuwait (Al-Masjid Al-Kabir)", "religious", 0.00, 4.8),
        ("Souk Al-Mubarakiya Historic Heritage Market", "market", 0.00, 4.8),
        ("Sheikh Jaber Al-Ahmad Cultural Centre", "cultural", 0.00, 4.7),
        ("Tareq Rajab Museum of Islamic Calligraphy & Ceramics", "museum", 500.00, 4.6),
    ],

    # Turkey (6)
    ("Istanbul", "Turkey"): [
        ("Hagia Sophia Grand Mosque (Ayasofya)", "heritage", 2200.00, 5.0),
        ("Blue Mosque (Sultanahmet Mosque) Iznik Tiles", "religious", 0.00, 4.8),
        ("Topkapi Palace & Imperial Harem", "palace", 3500.00, 4.9),
        ("Grand Bazaar (Kapalıçarşı 4000 Covered Shops)", "market", 0.00, 4.8),
        ("Basilica Cistern (Yerebatan Sarnıcı) Medusa Heads", "historical", 1800.00, 4.9),
        ("Bosphorus Strait Cruise Connecting Europe & Asia", "nature", 1200.00, 4.9),
    ],
    ("Goreme", "Turkey"): [
        ("Hot Air Balloon Sunrise Flight Over Fairy Chimneys", "adventure", 18000.00, 5.0),
        ("Göreme Open-Air Museum Rock-Cut Churches", "heritage", 1200.00, 4.9),
        ("Derinkuyu Underground Ancient Multi-Level City", "historical", 900.00, 4.8),
        ("Uchisar Castle High Natural Volcanic Rock Citadel", "viewpoint", 400.00, 4.8),
        ("Love Valley & Rose Valley Guided Sunset Hike", "nature", 0.00, 4.9),
    ],
    ("Antalya", "Turkey"): [
        ("Kaleiçi (Antalya Historic Roman/Ottoman Old Town)", "heritage", 0.00, 4.8),
        ("Hadrian's Gate (Üçkapılar Roman Arch)", "monument", 0.00, 4.7),
        ("Düden Waterfalls (Lower Cascade Plummeting to Sea)", "waterfall", 100.00, 4.7),
        ("Antalya Archaeological Museum Classical Sculptures", "museum", 750.00, 4.9),
        ("Konyaaltı Beach & Taurus Mountain Panorama", "beach", 0.00, 4.6),
    ],
    ("Bodrum", "Turkey"): [
        ("Bodrum Castle (Castle of St. Peter)", "fort", 900.00, 4.8),
        ("Museum of Underwater Archaeology (Shipwrecks)", "museum", 0.00, 4.8),
        ("Mausoleum at Halicarnassus Ancient Wonder Ruins", "historical", 300.00, 4.4),
        ("Bodrum Marina & Whitewashed Aegean Quays", "cultural", 0.00, 4.6),
        ("Yalıkavak Marina Luxury Yacht Basin & Sunsets", "viewpoint", 0.00, 4.7),
    ],
    ("Izmir", "Turkey"): [
        ("Kemeraltı Historic Covered Bazaar & Caravanserais", "market", 0.00, 4.8),
        ("Izmir Clock Tower & Konak Square", "monument", 0.00, 4.6),
        ("Ephesus UNESCO Ancient Greco-Roman City Excursion", "heritage", 1800.00, 5.0),
        ("Agora of Smyrna Ancient Roman Forum", "historical", 350.00, 4.6),
        ("Historical Elevator (Tarihi Asansör) Panoramic View", "viewpoint", 0.00, 4.7),
    ],
    ("Fethiye", "Turkey"): [
        ("Ölüdeniz Blue Lagoon & Babadağ Paragliding", "adventure", 9500.00, 5.0),
        ("Butterfly Valley (Kelebekler Vadisi) Hidden Beach", "nature", 500.00, 4.9),
        ("Tomb of Amyntas Ancient Lycian Rock-Cut Tomb", "historical", 250.00, 4.6),
        ("Saklıkent National Park Gorge Canyon River Trek", "adventure", 400.00, 4.8),
        ("Kayaköy Abandoned Ghost Village Excursion", "historical", 300.00, 4.7),
    ],

    # Jordan (3)
    ("Petra", "Jordan"): [
        ("Al-Khazneh (The Treasury) via The Siq Gorge", "heritage", 6000.00, 5.0),
        ("Ad-Deir (The Monastery) 800-Step Mountain Climb", "heritage", 0.00, 5.0),
        ("Royal Tombs & Urn Tomb Clifftop Carvings", "historical", 0.00, 4.9),
        ("High Place of Sacrifice Mountain Viewpoint", "viewpoint", 0.00, 4.8),
        ("Petra by Night Candlelit Treasury Experience", "cultural", 2200.00, 4.7),
    ],
    ("Amman", "Jordan"): [
        ("Amman Citadel (Jabal al-Qal'a) & Temple of Hercules", "heritage", 400.00, 4.8),
        ("Roman Theatre Amman (6,000-Seat Amphitheater)", "historical", 250.00, 4.7),
        ("Rainbow Street Cafes & Local Artisan Boutiques", "cultural", 0.00, 4.6),
        ("The Jordan Museum (Dead Sea Copper Scrolls)", "museum", 600.00, 4.8),
        ("King Abdullah I Mosque Blue Mosaic Dome", "religious", 250.00, 4.6),
    ],
    ("Aqaba", "Jordan"): [
        ("Aqaba Marine Park Coral Reef Snorkeling & Scuba", "adventure", 2500.00, 4.9),
        ("Wadi Rum 4x4 Protected Desert Safari Excursion", "adventure", 5500.00, 5.0),
        ("Aqaba Fortress (Mamluk Castle) & Flagpole", "fort", 250.00, 4.5),
        ("Berenice Beach Club Coral Bay Promenade", "beach", 1500.00, 4.6),
        ("Sharif Hussein bin Ali White Mosque", "religious", 0.00, 4.7),
    ],

    # Egypt (6)
    ("Cairo", "Egypt"): [
        ("Giza Pyramids Complex (Great Pyramid of Khufu)", "heritage", 1100.00, 5.0),
        ("Great Sphinx of Giza Ancient Limestone Guardian", "monument", 0.00, 4.9),
        ("Grand Egyptian Museum (GEM) & Tutankhamun Treasures", "museum", 2200.00, 5.0),
        ("Khan el-Khalili Historic Medieval Souq", "market", 0.00, 4.8),
        ("Saladin Citadel & Mosque of Muhammad Ali", "fort", 600.00, 4.8),
    ],
    ("Luxor", "Egypt"): [
        ("Valley of the Kings Pharaonic Royal Tombs", "heritage", 1400.00, 5.0),
        ("Karnak Temple Complex & Great Hypostyle Hall", "temple", 1100.00, 5.0),
        ("Luxor Temple on Nile River East Bank", "temple", 850.00, 4.9),
        ("Mortuary Temple of Hatshepsut at Deir el-Bahari", "heritage", 700.00, 4.9),
        ("Hot Air Balloon Sunrise Over West Bank Ruins", "adventure", 8500.00, 5.0),
    ],
    ("Aswan", "Egypt"): [
        ("Philae Temple of Isis on Agilkia Island", "temple", 900.00, 4.9),
        ("Abu Simbel Sun Temples of Ramesses II Excursion", "heritage", 1600.00, 5.0),
        ("Nile River Traditional Felucca Sunset Sailing", "nature", 1200.00, 4.9),
        ("Unfinished Obelisk Ancient Granite Quarry", "historical", 400.00, 4.5),
        ("Nubian Traditional Painted Village on Elephantine", "cultural", 800.00, 4.8),
    ],
    ("Alexandria", "Egypt"): [
        ("Bibliotheca Alexandrina (Revived Great Library)", "museum", 350.00, 4.9),
        ("Citadel of Qaitbay on Mediterranean Harbor", "fort", 400.00, 4.7),
        ("Catacombs of Kom El Shoqafa Roman Burial System", "historical", 350.00, 4.7),
        ("Montaza Palace Royal Gardens & Cove", "garden", 100.00, 4.6),
        ("Pompey's Pillar & Serapis Ancient Temple Ruins", "monument", 300.00, 4.4),
    ],
    ("Hurghada", "Egypt"): [
        ("Giftun Island National Park Coral Reef Snorkeling", "adventure", 2800.00, 4.9),
        ("Hurghada Marina Boulevard & Waterfront Dining", "cultural", 0.00, 4.6),
        ("El Dahar Historic Old Town & Spice Market", "market", 0.00, 4.4),
        ("Red Sea Quad Biking Desert Safari & Bedouin Camp", "adventure", 3200.00, 4.8),
        ("Hurghada Grand Aquarium & Shark Tunnel", "wildlife", 2200.00, 4.6),
    ],
    ("Sharm El Sheikh", "Egypt"): [
        ("Ras Mohammed National Park Coral Walls Diving", "nature", 2500.00, 5.0),
        ("Mount Sinai Sunrise Pilgrimage & St. Catherine Monastery", "adventure", 4500.00, 5.0),
        ("Naama Bay Promenade & Coral Reef Beaches", "beach", 0.00, 4.6),
        ("Tiran Island Marine Boat Tour & Snorkeling", "nature", 3000.00, 4.8),
        ("Al Sahaba Mosque Old Market Ottoman Marvel", "religious", 0.00, 4.8),
    ],

    # Morocco (6)
    ("Marrakech", "Morocco"): [
        ("Jemaa el-Fnaa Grand Square Acrobats & Food Stalls", "cultural", 0.00, 4.9),
        ("Jardin Majorelle & Yves Saint Laurent Museum", "garden", 1400.00, 4.9),
        ("Bahia Palace Intricate Cedar & Zellige Carvings", "palace", 600.00, 4.8),
        ("Koutoubia Mosque 12th-Century Minaret", "religious", 0.00, 4.7),
        ("Saadian Tombs Gilded Carrara Marble Vaults", "historical", 600.00, 4.6),
    ],
    ("Fes", "Morocco"): [
        ("Fes el-Bali (World's Largest Car-Free Urban Medina)", "heritage", 0.00, 4.9),
        ("Chouara Tannery Traditional Stone Dye Vats", "historical", 150.00, 4.8),
        ("Al-Qarawiyyin University & Mosque (Oldest in World)", "religious", 0.00, 4.9),
        ("Bou Inania Medersa Marinid Architecture", "heritage", 200.00, 4.8),
        ("Bab Bou Jeloud (The Famous Blue Gate of Fes)", "monument", 0.00, 4.7),
    ],
    ("Chefchaouen", "Morocco"): [
        ("The Blue Pearl Medina Narrow Cobalt Alleys", "cultural", 0.00, 5.0),
        ("Spanish Mosque Sunset Panoramic Mountain Hill", "viewpoint", 0.00, 4.9),
        ("Chefchaouen Kasbah Fortress & Ethnographic Museum", "fort", 500.00, 4.6),
        ("Ras El Maa Natural Mountain Spring Waterfall", "nature", 0.00, 4.6),
        ("Plaza Uta el-Hammam Central Square Cafes", "cultural", 0.00, 4.7),
    ],
    ("Casablanca", "Morocco"): [
        ("Hassan II Mosque over Atlantic Ocean (210m Minaret)", "religious", 1200.00, 5.0),
        ("Corniche Ain Diab Oceanfront Promenade", "beach", 0.00, 4.6),
        ("Quartier Habous (New Medina) Traditional Arcades", "cultural", 0.00, 4.6),
        ("Rick's Café Casablanca Historic Themed Lounge", "cultural", 1500.00, 4.7),
        ("Cathedral of the Sacred Heart (Sacre Coeur)", "architecture", 0.00, 4.4),
    ],
    ("Tangier", "Morocco"): [
        ("Cap Spartel (Where Mediterranean Meets Atlantic)", "viewpoint", 0.00, 4.8),
        ("Caves of Hercules (Grottes d'Hercule Sea Window)", "nature", 100.00, 4.7),
        ("Tangier Medina & Kasbah Museum of Mediterranean", "heritage", 200.00, 4.7),
        ("Café Hafa Historic Cliffside Mint Tea Terrace", "cultural", 0.00, 4.8),
        ("Grand Socco Square & Cinema Rif", "cultural", 0.00, 4.5),
    ],
    ("Essaouira", "Morocco"): [
        ("Essaouira UNESCO Seafront Ramparts & Cannons (Skala)", "fort", 400.00, 4.9),
        ("Historic Fishing Port & Blue Wooden Boats", "cultural", 0.00, 4.7),
        ("Essaouira Beach Kitesurfing & Windsurfing", "adventure", 2000.00, 4.8),
        ("Medina of Essaouira Thuja Woodcraft Guilds", "market", 0.00, 4.8),
        ("Mellah Historic Jewish Quarter", "historical", 0.00, 4.5),
    ],
}
