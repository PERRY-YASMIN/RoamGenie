"""Attractions for 20 Oceania destinations in RoamGenie (Phase D2)."""
from typing import Dict, List, Tuple

# Format: (name, category, entry_fee_inr, rating)
OCEANIA_ATTRACTIONS: Dict[Tuple[str, str], List[Tuple[str, str, float, float]]] = {
    # Australia (10)
    ("Sydney", "Australia"): [
        ("Sydney Opera House & Guided Architectural Tour", "architecture", 2400.00, 4.9),
        ("Sydney Harbour BridgeClimb & Pylon Lookout", "viewpoint", 9500.00, 4.9),
        ("Bondi to Coogee Coastal Walk & Icebergs Pool", "beach", 0.00, 4.9),
        ("Taronga Zoo Sydney (Harbour View Wildlife)", "wildlife", 2800.00, 4.8),
        ("The Rocks Historic Precinct & Weekend Markets", "cultural", 0.00, 4.7),
        ("Royal Botanic Garden Sydney & Mrs Macquarie's Chair", "garden", 0.00, 4.8),
    ],
    ("Melbourne", "Australia"): [
        ("Great Ocean Road & Twelve Apostles Limestone Stacks", "nature", 5500.00, 5.0),
        ("Federation Square & National Gallery of Victoria (NGV)", "museum", 0.00, 4.8),
        ("Melbourne Laneways & Degraves Street Street Art/Coffee", "cultural", 0.00, 4.8),
        ("Queen Victoria Market (Heritage Open-Air Market)", "market", 0.00, 4.7),
        ("Royal Botanic Gardens Victoria & Shrine of Remembrance", "garden", 0.00, 4.8),
    ],
    ("Brisbane", "Australia"): [
        ("South Bank Parklands & Streets Beach Lagoon", "park", 0.00, 4.8),
        ("Lone Pine Koala Sanctuary (Cuddling Koalas)", "wildlife", 2500.00, 4.8),
        ("Mount Coot-tha Summit Lookout & Botanic Gardens", "viewpoint", 0.00, 4.7),
        ("Story Bridge Adventure Climb", "adventure", 7500.00, 4.7),
        ("CityCat Brisbane River Ferry Cruise", "nature", 250.00, 4.6),
    ],
    ("Perth", "Australia"): [
        ("Kings Park and Botanic Garden (Glass Canopy Walk)", "park", 0.00, 4.9),
        ("Rottnest Island Day Tour & Quokka Selfies", "wildlife", 4500.00, 5.0),
        ("Fremantle Markets & Fremantle Prison UNESCO Tour", "historical", 1200.00, 4.7),
        ("Cottesloe Beach Golden Sands & Indiana Teahouse", "beach", 0.00, 4.7),
        ("Swan Bells (The Bell Tower) & Elizabeth Quay", "viewpoint", 850.00, 4.5),
    ],
    ("Cairns", "Australia"): [
        ("Great Barrier Reef Outer Reef Snorkeling & Scuba", "adventure", 12000.00, 5.0),
        ("Kuranda Scenic Railway & Skyrail Rainforest Cableway", "adventure", 6500.00, 4.9),
        ("Daintree Rainforest & Cape Tribulation 4WD Safari", "nature", 8500.00, 5.0),
        ("Cairns Esplanade Lagoon Public Pool", "park", 0.00, 4.7),
        ("Cairns Aquarium & Turtle Rehabilitation Centre", "wildlife", 2600.00, 4.6),
    ],
    ("Adelaide", "Australia"): [
        ("Adelaide Central Market (150-Year Food Hub)", "market", 0.00, 4.8),
        ("Barossa Valley Wine Tasting & Historic Chateaux", "cultural", 6500.00, 4.9),
        ("Glenelg Beach Tram & Seaside Promenade", "beach", 0.00, 4.6),
        ("Adelaide Botanic Garden & Bicentennial Conservatory", "garden", 0.00, 4.7),
        ("Adelaide Oval RoofClimb Stadium Experience", "viewpoint", 6000.00, 4.8),
    ],
    ("Gold Coast", "Australia"): [
        ("Surfers Paradise Beach & Coastal Boulevard", "beach", 0.00, 4.7),
        ("SkyPoint Observation Deck at Q1 (77th Floor)", "viewpoint", 1600.00, 4.7),
        ("Currumbin Wildlife Sanctuary (Lorikeet Feeding)", "wildlife", 2600.00, 4.8),
        ("Warner Bros. Movie World Theme Park", "park", 5500.00, 4.7),
        ("Springbrook National Park & Natural Bridge Glow Worms", "nature", 0.00, 4.9),
    ],
    ("Hobart", "Australia"): [
        ("MONA (Museum of Old and New Art Ferry & Vaults)", "museum", 2000.00, 4.9),
        ("Salamanca Place & Saturday Historic Market", "market", 0.00, 4.8),
        ("Mount Wellington (kunanyi) 1270m Pinnacle Lookout", "viewpoint", 0.00, 4.9),
        ("Port Arthur Historic Site UNESCO Convict Settlement", "historical", 2500.00, 4.9),
        ("Battery Point Historic Heritage Cottages Walk", "cultural", 0.00, 4.6),
    ],
    ("Darwin", "Australia"): [
        ("Mindil Beach Sunset Market & Asian Street Food", "market", 0.00, 4.8),
        ("Crocosaurus Cove (Cage of Death Giant Crocodiles)", "wildlife", 2200.00, 4.7),
        ("Litchfield National Park Waterfalls & Termite Mounds", "waterfall", 0.00, 4.9),
        ("Kakadu National Park UNESCO Yellow Water Billabong", "wildlife", 2500.00, 5.0),
        ("Darwin Waterfront Lagoon & Wave Pool", "park", 450.00, 4.5),
    ],
    ("Alice Springs", "Australia"): [
        ("Uluru (Ayers Rock) & Kata Tjuta National Park Excursion", "heritage", 2200.00, 5.0),
        ("Alice Springs Desert Park (Nocturnal House)", "wildlife", 1800.00, 4.7),
        ("Kings Canyon Rim Walk (Watarrka National Park)", "adventure", 0.00, 5.0),
        ("Royal Flying Doctor Service Visitor Centre", "museum", 900.00, 4.7),
        ("Anzac Hill Panoramic Outback Sunset Lookout", "viewpoint", 0.00, 4.6),
    ],

    # New Zealand (7)
    ("Auckland", "New Zealand"): [
        ("Sky Tower Auckland (328m SkyDeck & SkyJump)", "viewpoint", 2200.00, 4.7),
        ("Waiheke Island Vineyards & Ferry Cruise", "cultural", 2500.00, 4.9),
        ("Auckland War Memorial Museum & Maori Cultural Show", "museum", 1400.00, 4.8),
        ("Mount Eden (Maungawhau) Volcanic Crater Lookout", "viewpoint", 0.00, 4.8),
        ("Viaduct Harbour Waterfront Dining & Superyachts", "cultural", 0.00, 4.6),
    ],
    ("Queenstown", "New Zealand"): [
        ("Skyline Gondola & Luge Tracks to Bob's Peak", "adventure", 2800.00, 4.9),
        ("Milford Sound UNESCO Fiord Cruise Excursion", "nature", 8500.00, 5.0),
        ("AJ Hackett Kawarau Bridge (World's First Bungee Jump)", "adventure", 12000.00, 4.9),
        ("Shotover Jet Canyon Speedboat Thrill", "adventure", 7500.00, 4.9),
        ("Lake Wakatipu TSS Earnslaw Historic Steamship Cruise", "nature", 4500.00, 4.8),
    ],
    ("Rotorua", "New Zealand"): [
        ("Te Puia Geothermal Valley & Pohutu Geyser", "nature", 3500.00, 4.8),
        ("Hobbiton Movie Set Tour (Lord of the Rings Shire)", "cultural", 5500.00, 5.0),
        ("Redwoods Whakarewarewa Forest Treewalk", "adventure", 1800.00, 4.8),
        ("Polynesian Spa Natural Mineral Geothermal Pools", "nature", 2400.00, 4.7),
        ("Mitai Maori Traditional Village Hangi & Performance", "cultural", 6500.00, 4.9),
    ],
    ("Wellington", "New Zealand"): [
        ("Museum of New Zealand Te Papa Tongarewa", "museum", 0.00, 4.9),
        ("Wellington Cable Car & Botanic Garden Lookout", "viewpoint", 500.00, 4.7),
        ("Wētā Workshop Experience (Movie Special Effects)", "museum", 2500.00, 4.9),
        ("Zealandia Ecosanctuary (Fenced Wildlife Valley)", "wildlife", 1200.00, 4.8),
        ("Mount Victoria 360-Degree Lookout", "viewpoint", 0.00, 4.8),
    ],
    ("Christchurch", "New Zealand"): [
        ("Christchurch Botanic Gardens & Punting on the Avon", "garden", 1500.00, 4.8),
        ("Cardboard Cathedral (Transitional Cathedral)", "architecture", 0.00, 4.6),
        ("Christchurch Gondola & Port Hills Views", "viewpoint", 1800.00, 4.7),
        ("International Antarctic Centre (Storm Room & Huskies)", "museum", 3200.00, 4.8),
        ("Riverside Market Vibrant Indoor Food Hall", "market", 0.00, 4.7),
    ],
    ("Wanaka", "New Zealand"): [
        ("That Wanaka Tree (World-Famous Willow in Lake)", "nature", 0.00, 4.8),
        ("Roys Peak Challenging Alpine Track & Skyline View", "viewpoint", 0.00, 5.0),
        ("Cardrona Alpine Resort Skiing & Mountain Carts", "adventure", 6500.00, 4.8),
        ("Puzzling World Illusion Rooms & Great Maze", "park", 1200.00, 4.6),
        ("Lake Wanaka Kayaking & Mou Waho Island Cruise", "nature", 4500.00, 4.9),
    ],
    ("Napier", "New Zealand"): [
        ("Napier Art Deco Historic Quarter & Vintage Car Tour", "architecture", 1200.00, 4.8),
        ("Cape Kidnappers Gannet Colony 4WD Safari", "wildlife", 3500.00, 4.9),
        ("Marine Parade & Pania of the Reef Statue", "viewpoint", 0.00, 4.6),
        ("National Aquarium of New Zealand Oceanarium", "wildlife", 1500.00, 4.6),
        ("Mission Estate Winery (New Zealand's Oldest Winery)", "cultural", 1200.00, 4.8),
    ],

    # Fiji & French Polynesia (3)
    ("Nadi", "Fiji"): [
        ("Sri Siva Subramaniya Swami Temple (Largest in Pacific)", "temple", 200.00, 4.7),
        ("Garden of the Sleeping Giant Orchid Garden", "garden", 900.00, 4.7),
        ("Sabeto Natural Mud Pools & Thermal Geothermal Springs", "nature", 1200.00, 4.6),
        ("Mamanuca Islands Day Catamaran Sailing & Snorkeling", "adventure", 6500.00, 4.9),
        ("Port Denarau Marina Shopping & Island Ferries", "cultural", 0.00, 4.5),
    ],
    ("Suva", "Fiji"): [
        ("Fiji Museum & Thurston Botanical Gardens", "museum", 300.00, 4.6),
        ("Colo-I-Suva Rainforest Forest Park & Natural Pools", "nature", 250.00, 4.8),
        ("Suva Municipal Market Tropical Produce & Crafts", "market", 0.00, 4.5),
        ("Sacred Heart Cathedral Suva", "architecture", 0.00, 4.4),
        ("Suva Seawall Promenade on Laucala Bay", "viewpoint", 0.00, 4.4),
    ],
    ("Papeete", "French Polynesia"): [
        ("Marché de Papeete (Papeete Public Central Market)", "market", 0.00, 4.7),
        ("Bora Bora Lagoon & Mount Otemanu Excursion", "nature", 8500.00, 5.0),
        ("Papeete Waterfront Esplanade & Les Roulottes Food Trucks", "cultural", 0.00, 4.6),
        ("Tahiti Waterfalls (Faarumai Cascades & Ferns)", "waterfall", 0.00, 4.7),
        ("Pointe Vénus Black Sand Beach & Historical Lighthouse", "beach", 0.00, 4.6),
    ],
}
