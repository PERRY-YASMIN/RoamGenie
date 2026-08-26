"""Attractions for 35 Sub-Saharan African & Island destinations in RoamGenie (Phase D2)."""
from typing import Dict, List, Tuple

# Format: (name, category, entry_fee_inr, rating)
AFRICA_ATTRACTIONS: Dict[Tuple[str, str], List[Tuple[str, str, float, float]]] = {
    # South Africa (6)
    ("Cape Town", "South Africa"): [
        ("Table Mountain Aerial Cableway & Summit", "viewpoint", 2200.00, 5.0),
        ("Robben Island Historic Prison Museum Ferry", "historical", 2500.00, 4.8),
        ("Kirstenbosch National Botanical Garden & Boomslang Walk", "garden", 1100.00, 4.9),
        ("Boulders Beach African Penguin Colony", "wildlife", 900.00, 4.8),
        ("Cape Point & Cape of Good Hope Funicular", "nature", 1800.00, 4.9),
        ("V&A Waterfront & Zeitz MOCAA Modern Art", "cultural", 1200.00, 4.7),
    ],
    ("Johannesburg", "South Africa"): [
        ("Apartheid Museum & Nelson Mandela Exhibits", "museum", 800.00, 4.9),
        ("Soweto Vilakazi Street & Mandela House", "historical", 400.00, 4.8),
        ("Constitution Hill Human Rights Precinct", "historical", 600.00, 4.7),
        ("Cradle of Humankind UNESCO Caves Excursion", "heritage", 1200.00, 4.8),
        ("Gold Reef City Theme Park & Mine Tour", "park", 1400.00, 4.5),
    ],
    ("Durban", "South Africa"): [
        ("uShaka Marine World Aquarium & Wet 'n Wild", "park", 1500.00, 4.6),
        ("Durban Golden Mile Beachfront Promenade", "beach", 0.00, 4.6),
        ("Durban Botanic Gardens (Oldest in Africa)", "garden", 0.00, 4.7),
        ("Moses Mabhida Stadium SkyCar & Big Rush Swing", "adventure", 1200.00, 4.6),
        ("Victoria Street Traditional Spice Market", "market", 0.00, 4.4),
    ],
    ("Nelspruit", "South Africa"): [
        ("Kruger National Park Open Safari (Malelane Gate)", "wildlife", 2500.00, 5.0),
        ("Lowveld National Botanical Garden & Waterfalls", "garden", 300.00, 4.7),
        ("Sudwala Caves (Oldest Known Caves in the World)", "nature", 850.00, 4.8),
        ("Chimp Eden (Jane Goodall Chimpanzee Sanctuary)", "wildlife", 1200.00, 4.8),
        ("Blyde River Canyon Panorama Route Excursion", "viewpoint", 600.00, 5.0),
    ],
    ("Stellenbosch", "South Africa"): [
        ("Spier Wine Farm Segway & Vineyard Tasting", "cultural", 1500.00, 4.8),
        ("Dorp Street Cape Dutch Historic Architecture", "heritage", 0.00, 4.7),
        ("Jonkershoek Nature Reserve Mountain Biking", "adventure", 350.00, 4.8),
        ("Stellenbosch Village Museum 4 Historic Eras", "museum", 400.00, 4.6),
        ("Waterford Estate Wine and Chocolate Pairing", "cultural", 1200.00, 4.9),
    ],
    ("Port Elizabeth", "South Africa"): [
        ("Addo Elephant National Park Safari Excursion", "wildlife", 2200.00, 4.9),
        ("The Boardwalk Waterfront Complex & Casino", "cultural", 0.00, 4.5),
        ("Donkin Reserve Heritage Trail & Lighthouse", "monument", 0.00, 4.6),
        ("Sardinia Bay Beach & Sand Dunes Reserve", "beach", 0.00, 4.8),
        ("Route 67 Public Art & Mandela Heritage Walk", "cultural", 0.00, 4.7),
    ],

    # Kenya (5)
    ("Nairobi", "Kenya"): [
        ("David Sheldrick Wildlife Trust Elephant Orphanage", "wildlife", 1200.00, 5.0),
        ("Giraffe Centre (Hand-Feeding Endangered Rothschild Giraffes)", "wildlife", 1200.00, 4.9),
        ("Nairobi National Park (Wildlife Against City Skyline)", "wildlife", 3500.00, 4.8),
        ("Karen Blixen Museum (Out of Africa Farmhouse)", "museum", 1000.00, 4.6),
        ("Maasai Market Traditional Beaded Crafts", "market", 0.00, 4.6),
    ],
    ("Narok", "Kenya"): [
        ("Masai Mara National Reserve Great Migration Safari", "wildlife", 7500.00, 5.0),
        ("Mara River Crossing Crocodile & Hippo Safari", "wildlife", 0.00, 5.0),
        ("Hot Air Balloon Sunrise Flight Over Mara Plains", "adventure", 35000.00, 5.0),
        ("Traditional Maasai Cultural Manyatta Village Tour", "cultural", 2500.00, 4.8),
        ("Enonkishu Conservancy Wildlife Conservation Trail", "nature", 3000.00, 4.8),
    ],
    ("Mombasa", "Kenya"): [
        ("Fort Jesus UNESCO 16th-Century Portuguese Stronghold", "fort", 1000.00, 4.7),
        ("Old Town Mombasa Swahili & Arab Architecture", "heritage", 0.00, 4.6),
        ("Mombasa Marine National Park Coral Glass Boat", "nature", 1800.00, 4.7),
        ("Haller Park Reclaimed Limestone Quarry Zoo", "wildlife", 800.00, 4.6),
        ("Nyali Beach White Sand Shoreline", "beach", 0.00, 4.5),
    ],
    ("Diani Beach", "Kenya"): [
        ("Diani Beach Pristine White Coral Sands", "beach", 0.00, 5.0),
        ("Wasini Island Dolphin Dhow Cruise & Snorkeling", "adventure", 5500.00, 4.9),
        ("Colobus Conservation Primate Eco Sanctuary", "wildlife", 750.00, 4.7),
        ("Kite Surfing & Wind Sports at Galu Beach", "adventure", 3500.00, 4.8),
        ("Kongo Mosque Ancient Coral River Estuary", "historical", 0.00, 4.5),
    ],
    ("Nakuru", "Kenya"): [
        ("Lake Nakuru National Park (Rhino Sanctuary & Flamingos)", "wildlife", 4500.00, 4.9),
        ("Menengai Crater (One of World's Largest Calderas)", "viewpoint", 400.00, 4.7),
        ("Hyrax Hill Prehistoric Site and Museum", "historical", 350.00, 4.4),
        ("Lord Egerton Castle European Fortress", "palace", 600.00, 4.5),
        ("Makalia Falls Nature Cascades", "waterfall", 0.00, 4.5),
    ],

    # Tanzania (4)
    ("Zanzibar City", "Tanzania"): [
        ("Stone Town UNESCO Walled Swahili Alleyways", "heritage", 0.00, 4.8),
        ("Prison Island (Changuu) Giant Aldabra Tortoises", "wildlife", 1500.00, 4.7),
        ("Zanzibar Spice Farm Guided Tasting Tour", "garden", 1200.00, 4.8),
        ("Forodhani Gardens Night Food Street Market", "market", 0.00, 4.7),
        ("House of Wonders (Beit-al-Ajaib) Landmark", "historical", 300.00, 4.5),
    ],
    ("Dar es Salaam", "Tanzania"): [
        ("National Museum and House of Culture", "museum", 350.00, 4.6),
        ("Village Museum (Makumbusho Traditional Living Museum)", "cultural", 300.00, 4.6),
        ("Bongoyo Island Marine Reserve Day Boat Trip", "beach", 1500.00, 4.8),
        ("Kivukoni Fish Market (Vibrant Local Port)", "market", 0.00, 4.5),
        ("Coco Beach Waterfront & Evening Food Stalls", "beach", 0.00, 4.4),
    ],
    ("Arusha", "Tanzania"): [
        ("Mount Meru & Arusha National Park Forest Safari", "nature", 3500.00, 4.8),
        ("Cultural Heritage Centre & African Art Gallery", "museum", 0.00, 4.8),
        ("Meserani Snake Park & Maasai Museum", "wildlife", 600.00, 4.6),
        ("Ngorongoro Crater Day Excursion Base Tour", "wildlife", 6500.00, 5.0),
        ("Lake Duluti Forest Walking & Canoeing Trail", "adventure", 1200.00, 4.7),
    ],
    ("Seronera", "Tanzania"): [
        ("Serengeti Central Plains Lion Pride Game Drive", "wildlife", 7500.00, 5.0),
        ("Seronera River Valley Leopard Sanctuary Safari", "wildlife", 0.00, 5.0),
        ("Serengeti Hot Air Balloon Sunrise Safari", "adventure", 45000.00, 5.0),
        ("Retima Hippo Pool (200 Hippos Walloing)", "wildlife", 0.00, 4.9),
        ("Seronera Visitor Center & Natural History Trail", "museum", 0.00, 4.7),
    ],

    # Rwanda & Uganda (4)
    ("Kigali", "Rwanda"): [
        ("Kigali Genocide Memorial & Reflection Gardens", "historical", 0.00, 5.0),
        ("Inema Arts Center Rwandan Contemporary Painting", "cultural", 0.00, 4.8),
        ("Kimironko Bustling Multi-Storey Market", "market", 0.00, 4.6),
        ("Nyamirambo Women's Center Walking Tour", "cultural", 1200.00, 4.8),
        ("Campaign Against Genocide Museum", "museum", 600.00, 4.7),
    ],
    ("Musanze", "Rwanda"): [
        ("Volcanoes National Park Mountain Gorilla Tracking", "wildlife", 65000.00, 5.0),
        ("Golden Monkey Bamboo Forest Safari", "wildlife", 8500.00, 4.9),
        ("Musanze Underground Lava Caves Guided Walk", "nature", 3500.00, 4.7),
        ("Twin Lakes of Burera and Ruhondo Viewpoint", "viewpoint", 0.00, 4.8),
        ("Gorilla Guardians Traditional Village (Iby'Iwacu)", "cultural", 2500.00, 4.8),
    ],
    ("Kampala", "Uganda"): [
        ("Kasubi Tombs UNESCO Royal Buganda Mausoleum", "heritage", 600.00, 4.7),
        ("Uganda National Mosque (Gaddafi Mosque) Minaret View", "religious", 400.00, 4.8),
        ("Uganda Museum (Oldest Museum in East Africa)", "museum", 300.00, 4.5),
        ("Ndere Cultural Centre Traditional Music & Dance", "cultural", 1800.00, 4.9),
        ("Bahai Mother Temple of Africa Gardens", "religious", 0.00, 4.7),
    ],
    ("Entebbe", "Uganda"): [
        ("Entebbe Botanical Gardens on Lake Victoria", "garden", 250.00, 4.7),
        ("Uganda Wildlife Conservation Education Centre (Zoo)", "wildlife", 600.00, 4.7),
        ("Mabamba Swamp Shoebill Stork Canoe Safari Excursion", "wildlife", 4500.00, 5.0),
        ("Ngamba Island Chimpanzee Sanctuary Lake Boat Trip", "wildlife", 8500.00, 4.9),
        ("Imperial Resort Beach & Sunset Cruise", "beach", 200.00, 4.4),
    ],

    # Ethiopia, Zimbabwe & Zambia (4)
    ("Addis Ababa", "Ethiopia"): [
        ("National Museum of Ethiopia (Lucy Australopithecus Fossil)", "museum", 100.00, 4.8),
        ("Holy Trinity Cathedral Imperial Graves (Haile Selassie)", "religious", 300.00, 4.7),
        ("Addis Merkato (Africa's Largest Open-Air Market)", "market", 0.00, 4.5),
        ("Mount Entoto Panoramic Forest & Royal Palace", "viewpoint", 200.00, 4.7),
        ("Ethnological Museum at Addis Ababa University", "museum", 200.00, 4.7),
    ],
    ("Lalibela", "Ethiopia"): [
        ("Church of Saint George (Bet Giyorgis Rock-Hewn Cross)", "heritage", 3500.00, 5.0),
        ("Northern Group of Monolithic Rock Churches", "heritage", 0.00, 5.0),
        ("Eastern Group of Rock-Cut Hypogeum Temples", "heritage", 0.00, 4.9),
        ("Asheton Maryam Mountain Monastery Trek", "adventure", 800.00, 4.8),
        ("Yemrehana Krestos Ancient Built Cave Church Excursion", "historical", 1200.00, 4.9),
    ],
    ("Victoria Falls", "Zimbabwe"): [
        ("Victoria Falls (The Smoke that Thunders) Rainforest Walk", "waterfall", 3500.00, 5.0),
        ("Devil's Pool Natural Rock Infinity Edge Swim", "adventure", 9500.00, 5.0),
        ("Zambezi River Sunset Wildlife Boat Cruise", "nature", 4500.00, 4.9),
        ("Victoria Falls Bridge Historic Gorge Lookout & Bungee", "viewpoint", 0.00, 4.8),
        ("Helicopter Flight of Angels Over Falls", "adventure", 16000.00, 5.0),
    ],
    ("Livingstone", "Zambia"): [
        ("Mosi-oa-Tunya National Park (Rhino Walking Safari)", "wildlife", 2000.00, 4.9),
        ("Livingstone Island Royal Tour & High Tea", "cultural", 8500.00, 4.9),
        ("Batoka Gorge White Water Rafting Grade 5", "adventure", 9500.00, 5.0),
        ("Livingstone Memorial Museum (David Livingstone)", "museum", 400.00, 4.6),
        ("Mukuni Traditional Village Royal Guided Tour", "cultural", 1200.00, 4.7),
    ],

    # Namibia & Botswana (5)
    ("Windhoek", "Namibia"): [
        ("Christuskirche Historic Lutheran Landmark", "historical", 0.00, 4.6),
        ("Heroes' Acre National Monument & Panoramic View", "monument", 150.00, 4.5),
        ("National Museum of Namibia & Alte Feste", "museum", 100.00, 4.4),
        ("Namibia Craft Centre Handcrafted Artisan Stalls", "market", 0.00, 4.6),
        ("Daan Viljoen Game Reserve Wildlife Trail", "wildlife", 500.00, 4.6),
    ],
    ("Sossusvlei", "Namibia"): [
        ("Dune 45 Sunrise Climb over Red Namib Sands", "nature", 1200.00, 5.0),
        ("Deadvlei 900-Year Dead Camel Thorn Trees Clay Pan", "nature", 0.00, 5.0),
        ("Big Daddy (World's Tallest Sand Dune 325m)", "adventure", 0.00, 5.0),
        ("Sesriem Canyon Carved Limestone Chasm", "nature", 0.00, 4.8),
        ("Namib-Naukluft Dark Sky Stargazing Reserve", "viewpoint", 0.00, 5.0),
    ],
    ("Swakopmund", "Namibia"): [
        ("Swakopmund German Colonial Architecture & Jetty 1905", "heritage", 0.00, 4.7),
        ("Walvis Bay Lagoon Flamingos & Marine Catamaran Cruise", "wildlife", 4500.00, 4.9),
        ("Sandwich Harbour Where Giant Dunes Meet the Ocean", "adventure", 8500.00, 5.0),
        ("Swakopmund Quad Biking & Dune Sandboarding", "adventure", 3500.00, 4.8),
        ("National Marine Aquarium of Namibia", "museum", 300.00, 4.4),
    ],
    ("Maun", "Botswana"): [
        ("Okavango Delta Mokoro Canoe Wilderness Safari", "adventure", 6500.00, 5.0),
        ("Moremi Game Reserve Wildlife Safari (Cheetahs & Wild Dogs)", "wildlife", 8500.00, 5.0),
        ("Scenic Flight Over Okavango Delta Waterways", "nature", 18000.00, 5.0),
        ("Nhabe Museum Indigenous Botswana Crafts", "museum", 100.00, 4.3),
        ("Thamalakane River Sunset Boat Cruise", "nature", 1800.00, 4.7),
    ],
    ("Kasane", "Botswana"): [
        ("Chobe Riverfront Sunset Boat Safari (Swimming Elephants)", "wildlife", 4000.00, 5.0),
        ("Chobe National Park Open 4x4 Game Drive", "wildlife", 5500.00, 5.0),
        ("Impalila Island Four-Country Confluence Viewpoint", "viewpoint", 0.00, 4.8),
        ("Kasane Hot Springs Natural Mineral Pool", "nature", 0.00, 4.4),
        ("CARACAL Biodiversity Center & Snake Rescue", "wildlife", 450.00, 4.6),
    ],

    # Island Nations & West Africa (6)
    ("Port Louis", "Mauritius"): [
        ("Aapravasi Ghat UNESCO Indentured Labour Site", "heritage", 0.00, 4.7),
        ("Le Caudan Waterfront Promenade & Umbrella Alley", "cultural", 0.00, 4.6),
        ("Sir Seewoosagur Ramgoolam Botanical Garden (Pamplemousses)", "garden", 400.00, 4.8),
        ("Citadel (Fort Adelaide) Hilltop Panoramic Lookout", "fort", 0.00, 4.6),
        ("Central Market Port Louis Tropical Fruits & Textiles", "market", 0.00, 4.5),
    ],
    ("Grand Baie", "Mauritius"): [
        ("Grand Baie Public Beach & Turquoise Lagoon", "beach", 0.00, 4.7),
        ("Île aux Cerfs Island Catamaran & Parasailing Excursion", "adventure", 3500.00, 4.9),
        ("Mont Choisy White Sand Casuarina Beach", "beach", 0.00, 4.8),
        ("Submarine Undersea Walk & Underwater Scooter", "adventure", 6500.00, 4.8),
        ("Cap Malheureux Red-Roofed Notre Dame Church", "architecture", 0.00, 4.7),
    ],
    ("Victoria", "Seychelles"): [
        ("Beau Vallon Beach & Creole Sunset Food Stalls", "beach", 0.00, 4.8),
        ("Victoria Botanical Gardens (Giant Aldabra Tortoises)", "garden", 300.00, 4.7),
        ("Victoria Clock Tower (Little Big Ben Monument)", "monument", 0.00, 4.5),
        ("Sir Selwyn Selwyn-Clarke Victorian Market", "market", 0.00, 4.6),
        ("Morne Seychellois National Park Forest Mountain Hike", "adventure", 450.00, 4.9),
    ],
    ("Antananarivo", "Madagascar"): [
        ("Rova of Antananarivo (Queen's Palace on Analamanga Hill)", "palace", 500.00, 4.7),
        ("Lemurs' Park Botanical Sanctuary (7 Lemur Species)", "wildlife", 750.00, 4.8),
        ("Ambohimanga UNESCO Sacred Royal Hill Excursion", "heritage", 400.00, 4.8),
        ("Analakely Traditional Daily Zoma Market", "market", 0.00, 4.4),
        ("Lake Anosy & Heart-Shaped Monument aux Morts", "nature", 0.00, 4.4),
    ],
    ("Nosy Be", "Madagascar"): [
        ("Lokobe National Park Ancient Rainforest & Black Lemurs", "wildlife", 1200.00, 4.9),
        ("Nosy Tanikely Marine Reserve Snorkeling", "nature", 2500.00, 5.0),
        ("Mont Passot Extinct Volcano 360 Sunset Lookout", "viewpoint", 250.00, 4.8),
        ("Andilana Beach Turquoise Crystal Waters", "beach", 0.00, 4.8),
        ("Lemuria Land Ylang-Ylang Distillery & Animal Park", "garden", 650.00, 4.6),
    ],
    ("Accra", "Ghana"): [
        ("Black Star Square (Independence Square) Monument", "monument", 0.00, 4.6),
        ("Cape Coast Castle Slave Dungeons UNESCO Excursion", "historical", 800.00, 5.0),
        ("Kwame Nkrumah Memorial Park & Mausoleum", "museum", 400.00, 4.8),
        ("Labadi Pleasure Beach & Cultural Drumming", "beach", 200.00, 4.5),
        ("Makola Market Bustling Vibrant Commercial Hub", "market", 0.00, 4.5),
    ],
    ("Dakar", "Senegal"): [
        ("Gorée Island (Île de Gorée) House of Slaves UNESCO", "historical", 600.00, 4.9),
        ("African Renaissance Monument (Taller than Statue of Liberty)", "monument", 500.00, 4.7),
        ("Lake Retba (Pink Lake / Lac Rose) Salt Flats", "nature", 1200.00, 4.8),
        ("Ngor Island Artists' Surfing Haven & Beach", "cultural", 300.00, 4.7),
        ("Grand Mosque of Dakar & Seafront Corniche", "religious", 0.00, 4.6),
    ],
}
