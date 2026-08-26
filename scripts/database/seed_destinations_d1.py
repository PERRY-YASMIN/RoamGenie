"""Destination Master Dataset Seeder (Phase D1)
Populates the `destinations` table with 495 new high-quality travel destinations
(bringing the total to 500 records including the 5 existing valid records).

Repeatable, deterministic, transactional, preserving existing data and foreign keys.
"""
import json
import logging
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Set up project path & load environment variables
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Ensure dotenv is loaded from backend/.env if not already in env
backend_env_file = backend_dir / ".env"
if backend_env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(backend_env_file)

from app.db.models.catalogue import Destination
from app.db.session import get_engine
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_destinations_d1")

# Deterministic random seed
RANDOM_SEED = 20260820

# 5 Existing destinations in the connected PostgreSQL database (MUST PRESERVE)
EXISTING_DESTINATIONS = [
    ("Mysuru", "India"),
    ("Kochi", "India"),
    ("Jaipur", "India"),
    ("Udaipur", "India"),
    ("Goa", "India"),
]

# Master Dataset: 495 new destinations across 8 geographic regions
# Format: (city, country, description, average_daily_cost)
NEW_DESTINATIONS_DATA: List[Tuple[str, str, str, float]] = [
    # =========================================================================
    # 1. INDIA (135 new destinations + 5 existing = 140 total India)
    # =========================================================================
    ("Agra", "India", "Home to the iconic Taj Mahal, Agra Fort, and rich Mughal architectural masterpieces along the Yamuna River.", 3800.00),
    ("Varanasi", "India", "Spiritual capital of India famous for ancient Ganga ghats, sacred evening aarti, and silk weaving.", 3200.00),
    ("Bengaluru", "India", "The Garden City and technology hub boasting vibrant brewpubs, lush botanical gardens, and tech culture.", 4800.00),
    ("Mumbai", "India", "The bustling financial capital with historic colonial architecture, Bollywood glamour, and coastal promenades.", 6000.00),
    ("Delhi", "India", "Historic national capital brimming with centuries-old monuments, bustling Chandni Chowk bazaars, and street food.", 4500.00),
    ("Kolkata", "India", "Cultural and artistic soul of India known for colonial landmarks, vintage trams, and legendary Bengali sweets.", 3600.00),
    ("Chennai", "India", "Gateway to South India renowned for classical Carnatic music, Dravidian temples, and Marina Beach.", 4000.00),
    ("Hyderabad", "India", "City of Pearls featuring the historic Charminar, Golconda Fort, and world-renowned Hyderabadi biryani.", 4200.00),
    ("Amritsar", "India", "Spiritual center of Sikhism featuring the serene Golden Temple, Wagah Border ceremony, and Punjabi cuisine.", 3400.00),
    ("Rishikesh", "India", "Yoga capital of the world nestled in the Himalayan foothills along the sacred Ganges river with white-water rafting.", 3200.00),
    ("Haridwar", "India", "Ancient pilgrimage city along the holy Ganges known for Har Ki Pauri ghat and evening Ganga Aarti.", 2800.00),
    ("Shimla", "India", "Colonial summer capital nestled in pine-clad Himalayan hills with historic Ridge and toy train rides.", 4200.00),
    ("Manali", "India", "High-altitude Himalayan resort town popular for snow-capped Solang Valley, Rohtang Pass, and pine forests.", 4000.00),
    ("Dharamshala", "India", "Scenic hillside town home to the Dalai Lama, Tibetan monasteries, and views of the Dhauladhar range.", 3400.00),
    ("Leh", "India", "High-desert mountain wonderland featuring Buddhist gompas, Pangong Tso lake, and dramatic high passes.", 5500.00),
    ("Srinagar", "India", "Paradise on Earth famed for tranquil Dal Lake houseboats, Shikara rides, and Mughal terraced gardens.", 4800.00),
    ("Gulmarg", "India", "Premier Himalayan ski resort famous for the world's highest gondola, snow meadows, and alpine trails.", 5800.00),
    ("Pahalgam", "India", "Idyllic valley along the Lidder River known for lush pine meadows, Betaab Valley, and trekking trails.", 4600.00),
    ("Jodhpur", "India", "The Sun City distinguished by blue-painted houses beneath the massive Mehrangarh Fort and desert culture.", 3800.00),
    ("Jaisalmer", "India", "The Golden City surrounded by Thar desert dunes, yellow sandstone havelis, and camel safaris.", 4200.00),
    ("Pushkar", "India", "Holy lakeside town surrounded by desert hills featuring the rare Brahma Temple and vibrant camel fair.", 3000.00),
    ("Bikaner", "India", "Desert citadel known for Junagarh Fort, camel breeding farm, and delectable bhujia savories.", 3400.00),
    ("Mount Abu", "India", "Rajasthan's only hill station featuring the intricately carved marble Dilwara Jain temples and Nakki Lake.", 3600.00),
    ("Kumbhalgarh", "India", "Formidable Aravalli fortress featuring the world's second-longest continuous stone wall and wildlife sanctuary.", 3500.00),
    ("Mandu", "India", "Romantic ruined fortress city celebrating the architectural love story of Baz Bahadur and Rani Roopmati.", 2800.00),
    ("Hampi", "India", "UNESCO World Heritage site showcasing boulder-strewn landscapes and magnificent ruins of the Vijayanagara Empire.", 3200.00),
    ("Badami", "India", "Ancient Chalukya capital renowned for dramatic rock-cut cave temples carved into red sandstone cliffs.", 2900.00),
    ("Belur", "India", "Hoysala architectural marvel featuring the 12th-century Chennakeshava Temple with intricate soapstone sculptures.", 2900.00),
    ("Murudeshwar", "India", "Coastal pilgrimage destination home to the world's second-tallest Shiva statue and scenic Arabian Sea beach.", 3100.00),
    ("Gokarna", "India", "Serene coastal haven with pristine Om Beach, Mahabaleshwar temple, and laid-back Arabian Sea vibe.", 3000.00),
    ("Coorg", "India", "Lush mountain sanctuary known as Scotland of India, famous for coffee plantations, mist-covered hills, and waterfalls.", 4400.00),
    ("Chikmagalur", "India", "Birthplace of Indian coffee nestled in the Western Ghats with Mullayanagiri peak trekking and lush estates.", 3800.00),
    ("Kabini", "India", "Premier wildlife safari haven famous for river cruises, tiger sightings, and dense Nagarhole forest canopy.", 6500.00),
    ("Bandipur", "India", "Renowned tiger reserve in the Nilgiri biosphere with rich biodiversity and thrilling elephant safari tracks.", 5200.00),
    ("Munnar", "India", "Idyllic hill station draped in emerald tea gardens, mist-kissed hills, and Anamudi peak views.", 4000.00),
    ("Alleppey", "India", "Venice of the East world-renowned for tranquil backwaters, traditional Kettuvallam houseboats, and lagoons.", 4600.00),
    ("Wayanad", "India", "Pristine green paradise with spice plantations, Edakkal prehistoric rock art, and mist-covered Chembra Peak.", 3800.00),
    ("Varkala", "India", "Stunning coastal cliff beach overlooking the Arabian Sea, known for Janardhana Swami Temple and beach cafes.", 3400.00),
    ("Kovalam", "India", "Famous crescent beaches lined with lighthouse views, Ayurvedic retreats, and coastal fresh seafood.", 3800.00),
    ("Thekkady", "India", "Home to Periyar Tiger Reserve featuring scenic boat safaris, spice garden walks, and bamboo rafting.", 3600.00),
    ("Kumarakom", "India", "Picturesque backwater village on Vembanad Lake known for tranquil bird sanctuaries and luxury water stays.", 5000.00),
    ("Ooty", "India", "Queen of Hill Stations in the Nilgiri hills featuring botanical gardens, tea estates, and heritage toy train.", 4200.00),
    ("Kodaikanal", "India", "Princess of Hill Stations set around a star-shaped lake, pine forests, and misty Coaker's Walk.", 3800.00),
    ("Madurai", "India", "Ancient temple city celebrated for the towering gopurams of Meenakshi Amman Temple and rich Tamil culture.", 3200.00),
    ("Rameswaram", "India", "Sacred coastal island town famed for Ramanathaswamy Temple corridors, Agnitheertham, and Pamban Bridge.", 3000.00),
    ("Dhanushkodi", "India", "Evocative ghost town at the eastern tip of Pamban Island where the Bay of Bengal meets the Indian Ocean.", 2800.00),
    ("Kanyakumari", "India", "Southernmost tip of mainland India where three oceans meet, featuring Vivekananda Rock Memorial and sunrises.", 3200.00),
    ("Pondicherry", "India", "Charming coastal enclave blending French colonial architecture, serene Promenade Beach, and Auroville.", 4200.00),
    ("Thanjavur", "India", "Cultural capital of Chola architecture featuring the grand Brihadisvara Temple and classical bronze art.", 3000.00),
    ("Mahabalipuram", "India", "UNESCO-listed coastal town known for monolithic rock-cut Shore Temple, Pancha Rathas, and stone carvings.", 3600.00),
    ("Coimbatore", "India", "Industrial and textile gateway to the Nilgiris known for the iconic Adiyogi Shiva statue and local cuisine.", 3400.00),
    ("Pune", "India", "Cultural and educational capital of Maharashtra with historic Shaniwar Wada, Sinhagad Fort, and food culture.", 4000.00),
    ("Lonavala", "India", "Popular Western Ghats monsoon getaway famous for mist-covered hills, Karla Caves, and sweet chikki.", 3800.00),
    ("Mahabaleshwar", "India", "Scenic hill resort on the Sahyadri ranges known for strawberry farms, Arthur's Seat, and panoramic valley views.", 4400.00),
    ("Alibaug", "India", "Coastal getaway near Mumbai with historic sea forts, sandy beaches, and fresh konkani seafood.", 4200.00),
    ("Nashik", "India", "Wine capital of India and sacred Kumbh Mela destination set along the Godavari River with vineyard stays.", 3600.00),
    ("Aurangabad", "India", "Tourism gateway to the magnificent rock-cut UNESCO caves of Ajanta and Ellora and Bibi Ka Maqbara.", 3400.00),
    ("Nagpur", "India", "The Orange City of India and tiger capital surrounded by premier wildlife sanctuaries like Tadoba and Pench.", 3600.00),
    ("Tadoba", "India", "Maharashtra's oldest and largest national park famous for high tiger density and teak forest safaris.", 5400.00),
    ("Shirdi", "India", "Renowned pilgrimage destination drawing millions of devotees to the sacred temple of Sai Baba.", 3000.00),
    ("Darjeeling", "India", "Queen of the Himalayas offering spectacular views of Kanchenjunga, world-famous tea estates, and toy train.", 4200.00),
    ("Kalimpong", "India", "Tranquil hill station in West Bengal with Buddhist monasteries, orchid nurseries, and Teesta river views.", 3400.00),
    ("Sundarbans", "India", "World's largest mangrove delta famous for royal Bengal tigers, estuarine crocodiles, and boat safaris.", 4500.00),
    ("Shantiniketan", "India", "Rabindranath Tagore's historic cultural haven celebrated for Visva-Bharati University, baul music, and art.", 2800.00),
    ("Siliguri", "India", "Strategic gateway city connecting the Northeast with vibrant tea auction centres and Coronation Bridge.", 3200.00),
    ("Gangtok", "India", "Vibrant capital of Sikkim offering breathtaking Himalayan vistas, Enchey Monastery, and MG Marg cafes.", 4400.00),
    ("Pelling", "India", "Sikkimese mountain town known for panoramic Kanchenjunga panoramas, Skywalk, and Pemayangtse Monastery.", 3800.00),
    ("Lachung", "India", "Picturesque North Sikkim alpine village gateway to Yumthang Valley of Flowers and zero point snowfields.", 4800.00),
    ("Guwahati", "India", "Gateway to the Northeast on the Brahmaputra River, famous for Kamakhya Temple and river cruises.", 3600.00),
    ("Kaziranga", "India", "UNESCO World Heritage wildlife sanctuary home to the world's largest population of great one-horned rhinos.", 5200.00),
    ("Manas", "India", "UNESCO biosphere reserve along the Himalayan foothills known for wild water buffaloes and pygmy hogs.", 4800.00),
    ("Majuli", "India", "World's largest river island on the Brahmaputra known for Vaishnavite Neo-Sattras and indigenous crafts.", 2800.00),
    ("Shillong", "India", "Scotland of the East featuring cascading waterfalls, vibrant indie music scene, and pine-scented hills.", 4000.00),
    ("Cherrapunji", "India", "Fabled high-rainfall wonder famous for living root bridges, Nohkalikai Falls, and limestone caves.", 3800.00),
    ("Dawki", "India", "Border town famous for the crystal-clear emerald waters of the Umngot River and boat rides.", 3200.00),
    ("Tawang", "India", "High-altitude Tibetan Buddhist sanctuary featuring India's largest monastery and scenic Sela Pass.", 4800.00),
    ("Ziro", "India", "Scenic pine-clad valley inhabited by the Apatani tribe, famous for lush paddy fields and music festival.", 3400.00),
    ("Kohima", "India", "Capital of Nagaland known for the historic World War II cemetery, Naga heritage village, and Hornbill Festival.", 3600.00),
    ("Imphal", "India", "Historical capital of Manipur known for Kangla Fort, world's only floating national park on Loktak Lake.", 3400.00),
    ("Aizawl", "India", "Serene cliffside capital of Mizoram overlooking lush valleys with rich Mizo tribal traditions and markets.", 3200.00),
    ("Agartala", "India", "Capital of Tripura showcasing the regal Ujjayanta Palace, Neermahal water palace, and heritage temples.", 3000.00),
    ("Puri", "India", "Sacred coastal city famed for Jagannath Temple, annual Rath Yatra, and golden Bay of Bengal beaches.", 3200.00),
    ("Bhubaneswar", "India", "City of Temples showcasing magnificent Kalinga architecture at Lingaraj Temple and ancient Udayagiri caves.", 3400.00),
    ("Konark", "India", "Home to the colossal 13th-century Sun Temple carved like a grand chariot on the Bay of Bengal coast.", 3000.00),
    ("Chilika", "India", "Asia's largest brackish water lagoon famous for migratory birds, Irrawaddy dolphin sightings, and islands.", 3600.00),
    ("Ahmedabad", "India", "India's first UNESCO World Heritage City famed for Sabarmati Ashram, pols architecture, and street food.", 3800.00),
    ("Kutch", "India", "Fabled white salt desert renowned for the vibrant Rann Utsav, traditional handicrafts, and starry nights.", 4800.00),
    ("Bhuj", "India", "Historic cultural gateway of Kutch famous for Aina Mahal, Prag Mahal, and intricate Rogan and bandhani art.", 3200.00),
    ("Gir", "India", "The sole global sanctuary of the Asiatic lion featuring dry deciduous forests and thrilling jeep safaris.", 5400.00),
    ("Dwarka", "India", "Ancient sacred Char Dham holy city on the Arabian Sea dedicated to Lord Krishna with Dwarkadhish Temple.", 3200.00),
    ("Somnath", "India", "First of the twelve sacred Jyotirlinga shrines located directly on the rugged Arabian Sea shoreline.", 3000.00),
    ("Vadodara", "India", "Cultural capital of Gujarat showcasing the opulent Laxmi Vilas Palace and Maharaja Fateh Singh Museum.", 3400.00),
    ("Surat", "India", "Diamond and textile metropolis known for Dutch colonial cemeteries, Dumas Beach, and street delicacies.", 3600.00),
    ("Khajuraho", "India", "UNESCO World Heritage site world-renowned for intricately sculpted medieval Hindu and Jain temples.", 3600.00),
    ("Gwalior", "India", "Historic fortress city boasting the formidable Gwalior Fort, Jai Vilas Palace, and classical musical legacy.", 3200.00),
    ("Orchha", "India", "Charming medieval town on the Betwa River frozen in time with cenotaphs, Raja Mahal, and Jahangir Mahal.", 2800.00),
    ("Bhopal", "India", "City of Lakes blending historic mosques, Upper Lake boating, and proximity to Sanchi Buddhist stupas.", 3200.00),
    ("Indore", "India", "India's cleanest city celebrated for Rajwada Palace, Sarafa Night Food Market, and culinary culture.", 3400.00),
    ("Ujjain", "India", "Ancient holy city on the Shipra River hosting the Kumbh Mela and the revered Mahakaleshwar Jyotirlinga.", 3000.00),
    ("Kanha", "India", "Iconic national park that inspired Rudyard Kipling's Jungle Book, famed for royal Bengal tigers and barasingha.", 5800.00),
    ("Bandhavgarh", "India", "Famed tiger reserve boasting the highest density of Royal Bengal tigers and ancient hilltop fort ruins.", 6000.00),
    ("Pench", "India", "Teak forest wildlife sanctuary straddling MP and Maharashtra, celebrated for predator sightings and nature camps.", 5200.00),
    ("Lucknow", "India", "City of Nawabs celebrated for its refined Awadhi culinary culture, Chikankari embroidery, and Bara Imambara.", 3600.00),
    ("Mathura", "India", "Sacred birthplace of Lord Krishna along the Yamuna River bustling with ancient temples and Janmashtami gaiety.", 2800.00),
    ("Vrindavan", "India", "Sacred Vaishnavite pilgrimage town filled with hundreds of historic temples dedicated to Radha and Krishna.", 2800.00),
    ("Ayodhya", "India", "Ancient sacred city along the Sarayu River celebrated for the grand Ram Mandir and deep spiritual heritage.", 3200.00),
    ("Prayagraj", "India", "Holy city at the sacred confluence of Ganga, Yamuna, and Saraswati, world-famous for the Maha Kumbh Mela.", 3000.00),
    ("Nainital", "India", "Scenic lake district in Kumaon hills centered around emerald Naini Lake with Naina Peak viewpoints.", 4000.00),
    ("Mussoorie", "India", "The Queen of the Hills perched on the Garhwal range with Mall Road strolls, Kempty Falls, and Gun Hill.", 4200.00),
    ("Almora", "India", "Cultural heart of Kumaon boasting panoramic Himalayan views, Bright End Corner sunsets, and Kasar Devi temple.", 3300.00),
    ("Auli", "India", "Premier Himalayan skiing haven offering panoramic vistas of Nanda Devi peak and alpine meadows.", 5600.00),
    ("Jim Corbett", "India", "India's oldest national park nestled in the Himalayan foothills, famed for wild tigers and riverine forests.", 5500.00),
    ("Kausani", "India", "Tranquil hill village offering spectacular 300-km wide views of snow-clad Himalayan peaks.", 3400.00),
    ("Kedarnath", "India", "Revered high-altitude Jyotirlinga shrine set against snow-clad Himalayan peaks in the Mandakini valley.", 4500.00),
    ("Badrinath", "India", "Sacred Char Dham shrine dedicated to Lord Vishnu situated between Nar and Narayana mountain ranges.", 4200.00),
    ("Spiti Valley", "India", "High-altitude cold desert valley featuring ancient Ki Monastery, fossil villages, and lunar landscapes.", 4600.00),
    ("Kasol", "India", "Scenic Parvati Valley haven popular with backpackers for pine-shaded riverside trails and Israeli cafes.", 3200.00),
    ("Dalhousie", "India", "Colonial-era hill station built across five hills with pine forests, Victorian buildings, and Khajjiar meadows.", 3800.00),
    ("Chandigarh", "India", "India's first planned modernist city designed by Le Corbusier, famous for Rock Garden and Sukhna Lake.", 4000.00),
    ("Patna", "India", "Ancient historical city of Pataliputra along the Ganges with Golghar, Bihar Museum, and Sikh pilgrimage sites.", 3000.00),
    ("Bodh Gaya", "India", "Supreme Buddhist pilgrimage site where Lord Buddha attained enlightenment beneath the sacred Bodhi Tree.", 3200.00),
    ("Nalanda", "India", "UNESCO World Heritage ruins of the ancient 5th-century residential monastic university.", 2800.00),
    ("Ranchi", "India", "City of Waterfalls surrounded by lush forests, Hundru Falls, and tribal cultural museums.", 3200.00),
    ("Jamshedpur", "India", "Steel city renowned for urban planning, Jubilee Park, and Dalma Wildlife Sanctuary.", 3400.00),
    ("Hazaribagh", "India", "Scenic plateau town known for dense wildlife sanctuary, Canary Hill viewpoints, and indigenous Sohrai wall art.", 2700.00),
    ("Raipur", "India", "Gateway to Chhattisgarh with ancient temples, tribal art hubs, and proximity to Chitrakote Falls.", 3200.00),
    ("Lepakshi", "India", "Historic Vijayanagara heritage village famous for the hanging pillar of Veerabhadra Temple and monolithic Nandi.", 2800.00),
    ("Visakhapatnam", "India", "Scenic coastal port city surrounded by Eastern Ghats with RK Beach, submarine museum, and Araku Valley.", 3800.00),
    ("Araku Valley", "India", "Picturesque hill station in the Eastern Ghats known for coffee plantations, tribal culture, and Borra Caves.", 3400.00),
    ("Tirupati", "India", "World-renowned holy pilgrimage destination home to the sacred hilltop Venkateswara Temple on Tirumala.", 3400.00),
    ("Vijayawada", "India", "Vibrant city on the Krishna River famous for Kanaka Durga Temple and ancient Undavalli rock caves.", 3200.00),
    ("Warangal", "India", "Historic Kakatiya capital showcasing the Thousand Pillar Temple, Ramappa Temple, and massive stone gateways.", 3000.00),
    ("Port Blair", "India", "Tropical island capital of Andaman & Nicobar, home to historic Cellular Jail and coral marine life.", 5800.00),
    ("Havelock Island", "India", "Tropical island paradise famous for Radhanagar Beach sunsets, scuba diving, and elephant beach reefs.", 6800.00),
    ("Neil Island", "India", "Tranquil Andaman island known for natural rock bridges, organic fruit farming, and pristine coral reefs.", 5500.00),
    ("Kavaratti", "India", "Pristine capital island of Lakshadweep famous for turquoise lagoons, coral atolls, and water sports.", 7500.00),
    ("Diu", "India", "Charming coastal island enclave with Portuguese sea fortress, Nagoa Beach, and relaxed coastal atmosphere.", 3600.00),
    ("Daman", "India", "Twin coastal heritage town featuring Portuguese forts of Moti Daman and Nani Daman with seaside promenades.", 3400.00),
    ("Silvassa", "India", "Green capital of Dadra and Nagar Haveli known for Portuguese churches, tribal art, and lake gardens.", 3200.00),

    # =========================================================================
    # 2. SOUTHEAST / EAST ASIA / SOUTH ASIA (85 destinations)
    # =========================================================================
    # Japan (12)
    ("Tokyo", "Japan", "Ultra-modern metropolis blending futuristic skyscrapers, neon districts, ancient Shinto shrines, and world-class dining.", 15500.00),
    ("Kyoto", "Japan", "Cultural heart of Japan boasting classical wooden machiya, thousands of Zen temples, Shinto shrines, and geisha districts.", 14000.00),
    ("Osaka", "Japan", "Japan's street-food capital renowned for lively Dotonbori canal, Osaka Castle, takoyaki, and nightlife.", 13000.00),
    ("Sapporo", "Japan", "Capital of Hokkaido famous for winter snow festivals, fresh seafood markets, ramen alley, and beer culture.", 12500.00),
    ("Hiroshima", "Japan", "City of peace showcasing the Peace Memorial Park, Atomic Bomb Dome, and nearby scenic Miyajima shrine island.", 11500.00),
    ("Nara", "Japan", "Historic first capital of Japan renowned for free-roaming sacred deer, Todai-ji giant Buddha, and ancient temples.", 10500.00),
    ("Fukuoka", "Japan", "Vibrant southern gateway known for Hakata tonkotsu ramen yatai street food stalls and ancient coastal shrines.", 11000.00),
    ("Hakone", "Japan", "Scenic mountain retreat nestled near Mount Fuji featuring relaxing volcanic onsen hot springs and Lake Ashi.", 16000.00),
    ("Takayama", "Japan", "Charming Edo-period historic town nestled in the Japanese Alps famous for morning markets and timber architecture.", 12000.00),
    ("Kanazawa", "Japan", "Edo-period arts capital known for Kenroku-en garden, preserved geisha and samurai quarters, and gold leaf crafts.", 12500.00),
    ("Nagoya", "Japan", "Historic castle city and industrial hub renowned for Nagoya Castle, Atsuta Jingu shrine, and hitsumabushi eel cuisine.", 11800.00),
    ("Okinawa", "Japan", "Subtropical island paradise known for turquoise waters, coral diving, Ryukyu kingdom castles, and beach resorts.", 14500.00),

    # South Korea (6)
    ("Seoul", "South Korea", "Dynamic capital blending royal Joseon palaces, futuristic Dongdaemun design plaza, K-pop culture, and night markets.", 13500.00),
    ("Busan", "South Korea", "Coastal metropolis famous for Haeundae Beach, Jagalchi fish market, Gamcheon Culture Village, and seafood.", 11500.00),
    ("Jeju City", "South Korea", "Volcanic island haven featuring dramatic basalt lava tubes, Hallasan mountain hiking, and pristine beaches.", 12000.00),
    ("Gyeongju", "South Korea", "The museum without walls showcasing ancient Silla royal burial mounds, Bulguksa Temple, and Cheomseongdae.", 9500.00),
    ("Incheon", "South Korea", "Coastal gateway city featuring Chinatown, Songdo futuristic smart city district, and island promenades.", 11000.00),
    ("Jeonju", "South Korea", "UNESCO City of Gastronomy celebrated for its sprawling traditional Hanok Village and authentic Jeonju bibimbap.", 9000.00),

    # China, Hong Kong, Macau, Taiwan (14)
    ("Beijing", "China", "Historic imperial capital home to the Forbidden City, Temple of Heaven, Summer Palace, and nearby Great Wall.", 11000.00),
    ("Shanghai", "China", "Futuristic financial mega-city featuring the historic Bund waterfront, Pudong skyline, and French Concession tree-lined avenues.", 12500.00),
    ("Xi'an", "China", "Ancient Silk Road starting point famed for the world-renowned Terracotta Army, city wall cycling, and Muslim Quarter.", 8500.00),
    ("Guilin", "China", "World-famous karst landscape along the winding Li River featuring limestone peaks, Reed Flute Cave, and rice terraces.", 8000.00),
    ("Chengdu", "China", "Laid-back capital of Sichuan celebrated for giant panda breeding centers, spicy hotpot, and teahouse culture.", 7800.00),
    ("Hangzhou", "China", "Scenic paradise celebrated for the tranquil West Lake, traditional Longjing tea plantations, and Lingyin Temple.", 8500.00),
    ("Guangzhou", "China", "Southern trade hub and culinary birthplace of Cantonese dim sum featuring Canton Tower and Shamian Island.", 9000.00),
    ("Lijiang", "China", "Picturesque ancient Naxi heritage town with cobblestone alleys, traditional water canals, and Jade Dragon Snow Mountain.", 8200.00),
    ("Hong Kong", "Hong Kong", "High-octane world city blending Victoria Harbour skyline, dim sum heritage, Peak Tram, and lively night markets.", 17500.00),
    ("Macau", "Macau", "Vibrant fusion of Portuguese colonial architecture at Ruins of St. Paul's, opulent casino resorts, and Macanese cuisine.", 16000.00),
    ("Taipei", "Taiwan", "Vibrant capital renowned for Taipei 101, bustling Shilin Night Market, National Palace Museum, and street food.", 10500.00),
    ("Kaohsiung", "Taiwan", "Southern maritime city known for Lotus Pond pagodas, Pier-2 Art Center, and Liuhe Night Market.", 8500.00),
    ("Taichung", "Taiwan", "Cultural hub in central Taiwan famous for Sun Moon Lake gateway, Rainbow Village, and Fengjia Night Market.", 8000.00),
    ("Tainan", "Taiwan", "Taiwan's oldest historic city celebrated for centuries-old Dutch forts, historic temples, and traditional street food.", 7500.00),

    # Thailand (8)
    ("Bangkok", "Thailand", "Vibrant capital known for ornate Grand Palace, Wat Arun, bustling street food stalls, and Chao Phraya river life.", 5500.00),
    ("Chiang Mai", "Thailand", "Cultural northern hub nestled in misty mountains featuring ancient Lanna temples, elephant sanctuaries, and night bazaars.", 4200.00),
    ("Phuket", "Thailand", "Thailand's largest island famous for Patong nightlife, Kata and Karon beaches, Big Buddha, and luxury resorts.", 7200.00),
    ("Krabi", "Thailand", "Coastal province renowned for towering limestone sea cliffs, Railay Beach rock climbing, and emerald lagoons.", 5800.00),
    ("Pattaya", "Thailand", "Lively seaside resort city known for Walking Street entertainment, Sanctuary of Truth temple, and water sports.", 5000.00),
    ("Koh Samui", "Thailand", "Tropical palm-fringed island paradise with luxury beachfront villas, Fisherman's Village, and coral diving.", 8000.00),
    ("Ayutthaya", "Thailand", "UNESCO-listed ancient Siamese capital featuring evocative red-brick temple ruins and Buddha head in tree roots.", 3800.00),
    ("Hua Hin", "Thailand", "Royal coastal resort town featuring peaceful sandy beaches, night food markets, and heritage railway station.", 4800.00),

    # Vietnam (8)
    ("Hanoi", "Vietnam", "Historic capital known for French-colonial Old Quarter, tranquil Hoan Kiem Lake, and fragrant street phở.", 3800.00),
    ("Ho Chi Minh City", "Vietnam", "Bustling southern metropolis featuring War Remnants Museum, Ben Thanh Market, and vibrant rooftop cafe culture.", 4200.00),
    ("Da Nang", "Vietnam", "Modern coastal hub known for My Khe Beach, illuminated Dragon Bridge, and the Golden Bridge at Ba Na Hills.", 4000.00),
    ("Hoi An", "Vietnam", "UNESCO-listed lantern-lit ancient port town famous for bespoke tailoring, wooden shophouses, and riverside dining.", 3600.00),
    ("Ha Long", "Vietnam", "Gateway city to world-famous Ha Long Bay emerald waters dotted with thousands of towering karst limestone islands.", 5200.00),
    ("Nha Trang", "Vietnam", "High-energy coastal resort city known for sweeping sandy beaches, island hopping cruises, and scuba diving.", 3800.00),
    ("Sapa", "Vietnam", "Misty northern mountain sanctuary surrounded by sculpted rice terraces, Fansipan peak, and ethnic hill tribes.", 3400.00),
    ("Hue", "Vietnam", "Imperial capital of the Nguyen Dynasty boasting the sprawling Citadel, royal mausoleums along the Perfume River.", 3200.00),

    # Indonesia (7)
    ("Bali", "Indonesia", "Island of the Gods famous for lush rice terraces, sacred sea temples, surf breaks, and vibrant beach clubs.", 6200.00),
    ("Ubud", "Indonesia", "Cultural heart of Bali known for sacred Monkey Forest, traditional dance performances, yoga retreats, and art galleries.", 5200.00),
    ("Jakarta", "Indonesia", "Sprawling Indonesian mega-capital featuring Monas monument, Old Batavia colonial square, and modern shopping malls.", 4500.00),
    ("Yogyakarta", "Indonesia", "Javanese cultural capital gateway to the majestic UNESCO temples of Borobudur and Prambanan and batik arts.", 3600.00),
    ("Lombok", "Indonesia", "Pristine island retreat featuring Mount Rinjani volcano trekking, deserted white beaches, and Gili island ferries.", 4400.00),
    ("Labuan Bajo", "Indonesia", "Harbor town gateway to Komodo National Park, famous for giant Komodo dragons and pink sand beaches.", 7500.00),
    ("Bandung", "Indonesia", "Lush highland city in West Java known for Art Deco architecture, volcano crater tea estates, and factory outlets.", 3800.00),

    # Malaysia & Singapore (7)
    ("Kuala Lumpur", "Malaysia", "Dynamic metropolis crowned by the glittering Petronas Twin Towers, Batu Caves, and multicultural food havens.", 5800.00),
    ("George Town", "Malaysia", "UNESCO-listed cultural gem in Penang famed for world-class street food, street murals, and heritage clan houses.", 4200.00),
    ("Langkawi", "Malaysia", "Duty-free tropical archipelago featuring the Langkawi Sky Bridge, mangrove boat safaris, and luxury beach resorts.", 6500.00),
    ("Melaka", "Malaysia", "Historic trading port showcasing Dutch red square architecture, Jonker Street night market, and Baba-Nyonya culture.", 3800.00),
    ("Kota Kinabalu", "Malaysia", "Coastal capital of Sabah in Malaysian Borneo, gateway to Mount Kinabalu climbing and rainforest wildlife.", 4800.00),
    ("Kuching", "Malaysia", "Charming riverside capital of Sarawak in Borneo known for historic waterfront, orangutan sanctuaries, and caves.", 4200.00),
    ("Singapore", "Singapore", "Futuristic garden city-state featuring Marina Bay Sands, Gardens by the Bay supertrees, and UNESCO hawker centres.", 18500.00),

    # Philippines (6)
    ("Manila", "Philippines", "High-energy historic capital featuring walled Intramuros fortress, Rizal Park, and vibrant modern BGC dining.", 4500.00),
    ("Cebu City", "Philippines", "Queen City of the South known for Magellan's Cross, Kawasan Falls canyoneering, and whale shark swimming in Oslob.", 4400.00),
    ("Boracay", "Philippines", "World-renowned island paradise famous for powder-soft White Beach, vibrant nightlife, and water sports.", 6800.00),
    ("El Nido", "Philippines", "Stunning paradise in Palawan famous for dramatic limestone cliffs, secret lagoons, and Bacuit Bay island hopping.", 6200.00),
    ("Coron", "Philippines", "Pristine diving haven in Palawan famous for crystal Kayangan Lake, WWII shipwrecks, and coral gardens.", 5800.00),
    ("Siargao", "Philippines", "Surfing capital of the Philippines known for Cloud 9 wave break, palm tree roads, and Magpupungko rock pools.", 5200.00),

    # Cambodia, Laos, Myanmar (6)
    ("Siem Reap", "Cambodia", "Gateway to the magnificent 12th-century Angkor Wat temple complex, ancient jungle ruins, and Pub Street.", 4200.00),
    ("Phnom Penh", "Cambodia", "Riverside capital city featuring the Royal Palace, Silver Pagoda, and bustling Tonle Sap promenade.", 3600.00),
    ("Luang Prabang", "Laos", "UNESCO-listed serene town at the confluence of Mekong and Nam Khan rivers with morning almsgiving and Kuang Si Falls.", 3800.00),
    ("Vang Vieng", "Laos", "Riverside adventure town framed by dramatic karst peaks, famous for blue lagoons, cave tubing, and hot air balloons.", 3200.00),
    ("Yangon", "Myanmar", "Former capital dominated by the glittering 325-foot Shwedagon Pagoda, colonial architecture, and street markets.", 3400.00),
    ("Bagan", "Myanmar", "Ancient archaeological wonderland with thousands of historic Buddhist temples rising across the plains at sunrise.", 4000.00),

    # South Asia (Sri Lanka, Maldives, Nepal, Bhutan) (11)
    ("Colombo", "Sri Lanka", "Commercial capital blending colonial architecture, Galle Face Green sunset promenade, and Pettah bazaars.", 4000.00),
    ("Kandy", "Sri Lanka", "Sacred mountain city home to the Temple of the Sacred Tooth Relic, scenic lake, and royal botanical gardens.", 3600.00),
    ("Galle", "Sri Lanka", "Historic southern coastal city enclosed by the 17th-century UNESCO-listed Dutch Galle Fort and ocean ramparts.", 4500.00),
    ("Ella", "Sri Lanka", "Picturesque hill country haven famous for Demodara Nine Arches Bridge, tea plantations, and Ella Rock hike.", 3200.00),
    ("Sigiriya", "Sri Lanka", "Home to the monumental 5th-century Lion Rock fortress with ancient frescoes, water gardens, and viewpoints.", 4200.00),
    ("Nuwara Eliya", "Sri Lanka", "Little England hill station perched among rolling tea estates with cool climate, colonial bungalows, and Gregory Lake.", 3800.00),
    ("Male", "Maldives", "Dense island capital featuring colorful buildings, Islamic Centre, fish market, and speedboats to resort atolls.", 8500.00),
    ("Maafushi", "Maldives", "Popular local island in South Male Atoll famous for bikini beaches, manta ray excursions, and budget water stays.", 9500.00),
    ("Kathmandu", "Nepal", "Historic Himalayan capital filled with UNESCO heritage squares, Swayambhunath monkey temple, and Pashupatinath.", 3000.00),
    ("Pokhara", "Nepal", "Tranquil lakeside adventure capital with Phewa Lake boating, Annapurna mountain views, and paragliding.", 3400.00),
    ("Paro", "Bhutan", "Scenic valley home to Bhutan's international airport and the legendary cliffside Tiger's Nest Monastery (Paro Taktsang).", 19500.00),

    # =========================================================================
    # 3. EUROPE (105 destinations)
    # =========================================================================
    # United Kingdom & Ireland (9)
    ("London", "United Kingdom", "World capital brimming with iconic landmarks like Big Ben, Tower Bridge, West End theatre, and British Museum.", 19500.00),
    ("Edinburgh", "United Kingdom", "Scotland's majestic historic capital crowned by Edinburgh Castle, the Royal Mile, and Arthur's Seat hike.", 15500.00),
    ("Oxford", "United Kingdom", "Historic university city known as the City of Dreaming Spires with historic colleges and Bodleian Library.", 14000.00),
    ("Cambridge", "United Kingdom", "Prestigious university town famous for punting along the River Cam, King's College Chapel, and gothic courts.", 14000.00),
    ("Manchester", "United Kingdom", "Vibrant northern powerhouse celebrated for industrial heritage, world-famous football clubs, and music scene.", 13000.00),
    ("Belfast", "United Kingdom", "Northern Irish capital known for Titanic Belfast shipyard museum, vibrant murals, and culinary pubs.", 12500.00),
    ("Bath", "United Kingdom", "UNESCO-listed Georgian city renowned for ancient Roman Baths, honey-colored Royal Crescent, and thermal spas.", 14500.00),
    ("Dublin", "Ireland", "Friendly literary capital famous for Trinity College, the Book of Kells, lively Temple Bar pubs, and Guinness Storehouse.", 16000.00),
    ("Galway", "Ireland", "Bohemian harbor city on the Wild Atlantic Way renowned for traditional Irish folk music, buskers, and seafood.", 13500.00),

    # France (10)
    ("Paris", "France", "The City of Light famed for the Eiffel Tower, Louvre Museum, Notre-Dame, haute cuisine, and romantic Seine river cruises.", 21000.00),
    ("Nice", "France", "Glamorous French Riviera coastal resort city boasting the palm-lined Promenade des Anglais and Mediterranean beaches.", 17500.00),
    ("Lyon", "France", "Gastronomic capital of France featuring UNESCO Renaissance Old Lyon, hidden traboules passageways, and bouchon bistros.", 14000.00),
    ("Marseille", "France", "Vibrant Mediterranean port city known for historic Old Port, Basilique Notre-Dame de la Garde, and Calanques.", 13500.00),
    ("Bordeaux", "France", "World-renowned wine capital with elegant 18th-century architecture, Place de la Bourse water mirror, and vineyards.", 15000.00),
    ("Strasbourg", "France", "Alsatian cultural bridge city featuring a stunning Gothic cathedral, timbered Petite France canal district, and European Parliament.", 13500.00),
    ("Annecy", "France", "Venice of the Alps featuring crystal-clear Lake Annecy, pastel canals, and panoramic mountain backdrop.", 16500.00),
    ("Avignon", "France", "Historic Provencal city enclosed by medieval ramparts, celebrated for the Gothic Palais des Papes and historic bridge.", 13000.00),
    ("Colmar", "France", "Fairytale Alsatian town with vibrant half-timbered houses, flower-lined Little Venice canals, and wine route.", 14000.00),
    ("Cannes", "France", "Glamorous French Riviera film festival resort known for luxury yacht marinas, Boulevard de la Croisette, and sandy private beaches.", 19500.00),

    # Italy (11)
    ("Rome", "Italy", "The Eternal City filled with ancient monuments including the Colosseum, Roman Forum, Vatican City, and Trevi Fountain.", 17500.00),
    ("Florence", "Italy", "Cradle of the Renaissance boasting the iconic Duomo, Uffizi Gallery masterworks, Ponte Vecchio, and Tuscan cuisine.", 16500.00),
    ("Venice", "Italy", "Floating city of romantic canals, gondolas, Saint Mark's Basilica, Doge's Palace, and marble palazzos.", 19000.00),
    ("Milan", "Italy", "Global fashion and design capital featuring the magnificent Duomo di Milano, Galleria Vittorio Emanuele II, and Da Vinci art.", 18000.00),
    ("Naples", "Italy", "Birthplace of wood-fired pizza with vibrant historic center, Royal Palace, and gateway to Pompeii and Mount Vesuvius.", 12000.00),
    ("Bologna", "Italy", "Italy's culinary powerhouse known as La Grassa, featuring medieval two towers, endless porticoes, and handmade pasta.", 13000.00),
    ("Amalfi", "Italy", "Dramatic cliffside coastal gem along the Amalfi Coast with pastel villas, lemon groves, and azure Mediterranean vistas.", 22000.00),
    ("Verona", "Italy", "Romantic setting of Shakespeare's Romeo and Juliet featuring the ancient Roman Arena amphitheater and Piazza delle Erbe.", 13500.00),
    ("Palermo", "Italy", "Capital of Sicily known for Arab-Norman architecture, bustling street markets like Ballaro, and Sicilian cannoli.", 11000.00),
    ("Siena", "Italy", "Tuscan medieval hill town famous for the fan-shaped Piazza del Campo, Gothic cathedral, and Palio horse race.", 13500.00),
    ("Lucca", "Italy", "Charming Tuscan gem enclosed by intact Renaissance tree-lined defensive walls, Roman amphitheater plaza, and cobblestone alleys.", 12800.00),

    # Spain (11)
    ("Madrid", "Spain", "Vibrant capital renowned for the Prado Museum, grand Royal Palace, lively tapas bars, and Retiro Park.", 14500.00),
    ("Barcelona", "Spain", "Catalan coastal capital celebrated for Antoni Gaudi's Sagrada Familia, Park Guell, Gothic Quarter, and beaches.", 16000.00),
    ("Seville", "Spain", "Sun-drenched Andalusian capital famous for the grand Alcazar palace, Plaza de Espana, and passionate Flamenco dance.", 12500.00),
    ("Valencia", "Spain", "Coastal birthplace of authentic paella featuring the futuristic City of Arts and Sciences and Mediterranean beaches.", 12000.00),
    ("Granada", "Spain", "Moorish jewel nestled beneath the Sierra Nevada mountains boasting the breathtaking UNESCO Alhambra palace complex.", 11500.00),
    ("Malaga", "Spain", "Costa del Sol coastal city featuring Picasso's birthplace museum, Moorish Alcazaba fortress, and sandy beaches.", 12000.00),
    ("San Sebastian", "Spain", "Basque culinary capital famous for La Concha crescent beach and world-renowned pintxos bars.", 17000.00),
    ("Bilbao", "Spain", "Basque industrial hub transformed into an arts metropolis by Frank Gehry's titanium Guggenheim Museum.", 13500.00),
    ("Cordoba", "Spain", "Historic Andalusian city famed for the stunning Mezquita-Cathedral with hundreds of red-and-white Moorish arches.", 11000.00),
    ("Toledo", "Spain", "Imperial City of Three Cultures perched on a gorge above the Tagus River with medieval Alcazar and El Greco art.", 11500.00),
    ("Palma de Mallorca", "Spain", "Mediterranean island capital boasting a grand Gothic seaside cathedral, historic Arab baths, and yacht marinas.", 15000.00),

    # Portugal (5)
    ("Lisbon", "Portugal", "Sun-kissed coastal capital famous for yellow Tram 28, Belem Tower, pastel de nata pastries, and Fado music.", 13000.00),
    ("Porto", "Portugal", "Historic northern riverside city famous for Douro River bridges, colorful Ribeira district, and Port wine cellars.", 11500.00),
    ("Sintra", "Portugal", "Romantic fairytale mountain town filled with colorful Pena Palace, Quinta da Regaleira estate, and misty forests.", 12500.00),
    ("Faro", "Portugal", "Charming gateway to the Algarve region featuring a walled old town and access to pristine golden barrier islands.", 11000.00),
    ("Funchal", "Portugal", "Subtropical capital of Madeira island known for lush botanical gardens, dramatic ocean cliffs, and cable car rides.", 13000.00),

    # Germany (8)
    ("Berlin", "Germany", "Dynamic capital celebrated for the Brandenburg Gate, Berlin Wall art, Museum Island, and avant-garde culture.", 14000.00),
    ("Munich", "Germany", "Bavarian capital famous for Marienplatz, historic beer halls, Oktoberfest grounds, and gateway to Neuschwanstein Castle.", 16000.00),
    ("Hamburg", "Germany", "Maritime port metropolis known for the UNESCO Speicherstadt warehouse district, Elbphilharmonie, and harbor cruises.", 14500.00),
    ("Frankfurt", "Germany", "Financial center blending modern banking skyscrapers with rebuilt medieval Romerberg historic square.", 14000.00),
    ("Cologne", "Germany", "Rhine river cultural hub dominated by the awe-inspiring Gothic twin-spired Cologne Cathedral.", 13000.00),
    ("Dresden", "Germany", "Baroque jewel on the Elbe River known as Florence on the Elbe, featuring the reconstructed Frauenkirche and Zwinger palace.", 11500.00),
    ("Heidelberg", "Germany", "Romantic university town on the Neckar River featuring ruined sandstone castle and Philosopher's Walk.", 13000.00),
    ("Nuremberg", "Germany", "Historic Bavarian city famous for Imperial Castle, medieval city walls, and famous gingerbread Christmas markets.", 12000.00),

    # Switzerland (7)
    ("Zurich", "Switzerland", "Lakeside banking metropolis known for luxury shopping on Bahnhofstrasse, historic Altstadt, and alpine views.", 24000.00),
    ("Geneva", "Switzerland", "International diplomatic hub on Lake Geneva featuring the iconic Jet d'Eau water fountain and UN headquarters.", 23000.00),
    ("Lucerne", "Switzerland", "Picturesque lakeside town known for the 14th-century wooden Chapel Bridge, Lion Monument, and Mount Pilatus.", 21000.00),
    ("Interlaken", "Switzerland", "Alpine adventure capital nestled between Lake Thun and Lake Brienz, gateway to Jungfraujoch and Eiger peak.", 22000.00),
    ("Zermatt", "Switzerland", "Car-free mountain resort town at the foot of the iconic pyramid-shaped Matterhorn peak, famous for skiing.", 26000.00),
    ("St. Moritz", "Switzerland", "Glamorous alpine resort town world-famous for champagne climate, frozen lake polo, and world-class ski slopes.", 28000.00),
    ("Basel", "Switzerland", "Cultural city on the Rhine River bordering France and Germany, celebrated for Art Basel and world-class museums.", 21000.00),

    # Austria (5)
    ("Vienna", "Austria", "Imperial capital of classical music featuring Schonbrunn Palace, St. Stephen's Cathedral, and historic coffeehouses.", 15500.00),
    ("Salzburg", "Austria", "Mozart's birthplace and Sound of Music setting featuring Hohensalzburg Fortress and baroque Mirabell Gardens.", 14500.00),
    ("Innsbruck", "Austria", "Capital of the Alps featuring the Golden Roof (Goldenes Dachl), Nordkette cable cars, and alpine winter sports.", 14000.00),
    ("Hallstatt", "Austria", "Breathtaking UNESCO alpine lake village surrounded by sheer mountains, 7000-year-old salt mines, and wooden chalets.", 16500.00),
    ("Graz", "Austria", "Styrian capital known for the hilltop Schlossberg clock tower, futuristic Kunsthaus Graz, and culinary heritage.", 12000.00),

    # Netherlands & Belgium (7)
    ("Amsterdam", "Netherlands", "Canal-ringed capital famous for Rijksmuseum, Van Gogh masterpieces, Anne Frank House, and cycling culture.", 18000.00),
    ("Rotterdam", "Netherlands", "Architectural innovation hub known for futuristic Cube Houses, Erasmus Bridge, and bustling modern port.", 14500.00),
    ("Utrecht", "Netherlands", "Charming student city featuring split-level canals, centuries-old Dom Tower, and vibrant waterside cafes.", 14000.00),
    ("Brussels", "Belgium", "Belgian capital and EU seat known for the ornate Grand Place, Atomium, chocolate boutiques, and waffle shops.", 14500.00),
    ("Bruges", "Belgium", "Fairytale medieval town crisscrossed by picturesque canals, cobblestone squares, and towering Belfry.", 15000.00),
    ("Ghent", "Belgium", "Vibrant medieval university city boasting Gravensteen castle, Saint Bavo's Cathedral, and canal walkways.", 13000.00),
    ("Antwerp", "Belgium", "Global diamond trading capital and fashion hub featuring Rubens' home and magnificent Central Station.", 13500.00),

    # Nordics & Scandinavia (9)
    ("Copenhagen", "Denmark", "Danish design capital known for colorful Nyhavn waterfront, Tivoli Gardens, Little Mermaid, and New Nordic cuisine.", 19000.00),
    ("Stockholm", "Sweden", "Capital built across 14 islands featuring historic Gamla Stan, Vasa maritime museum, and Royal Palace.", 18000.00),
    ("Oslo", "Norway", "Fjord-side capital famous for the futuristic Oslo Opera House, Munch Museum, Vigeland sculpture park, and fjord cruises.", 20500.00),
    ("Bergen", "Norway", "Gateway to the dramatic Norwegian fjords featuring the UNESCO-listed Bryggen colorful wooden wharf.", 19500.00),
    ("Stavanger", "Norway", "Coastal city famous for historic wooden old town and launching point for hiking to Preikestolen Pulpit Rock.", 18500.00),
    ("Helsinki", "Finland", "Design-centric Nordic seaside capital known for neoclassical Senate Square, Suomenlinna sea fortress, and saunas.", 16500.00),
    ("Reykjavik", "Iceland", "World's northernmost capital, gateway to the Golden Circle, geothermal Blue Lagoon, and Northern Lights.", 22000.00),
    ("Tromso", "Norway", "Arctic adventure hub in northern Norway famous for Northern Lights viewing, dog sledding, and Arctic Cathedral.", 21000.00),
    ("Rovaniemi", "Finland", "Official hometown of Santa Claus on the Arctic Circle with reindeer sleigh rides and snow hotels.", 20000.00),

    # Central & Eastern Europe (11)
    ("Prague", "Czech Republic", "City of a Hundred Spires famous for Charles Bridge, Prague Castle, Old Town Astronomical Clock, and Bohemian beer.", 9800.00),
    ("Budapest", "Hungary", "Pearl of the Danube boasting Hungarian Parliament, historic Szechenyi thermal baths, and Buda Castle hill.", 9200.00),
    ("Krakow", "Poland", "Historic royal capital with Europe's largest medieval market square, Wawel Royal Castle, and Kazimierz Jewish quarter.", 8000.00),
    ("Gdansk", "Poland", "Baltic amber port city boasting magnificent Flemish-style Long Market, historic shipyard, and seaside pier.", 7800.00),
    ("Warsaw", "Poland", "Resilient Polish capital featuring the faithfully reconstructed Old Town, Royal Castle, and bustling modern center.", 8500.00),
    ("Bratislava", "Slovakia", "Danube riverside capital crowned by Bratislava Castle, charming pedestrian old town, and quirky street statues.", 8800.00),
    ("Bucharest", "Romania", "Romania's vibrant Little Paris featuring the colossal Palace of the Parliament and lively Lipscani nightlife.", 7500.00),
    ("Dubrovnik", "Croatia", "Pearl of the Adriatic renowned for intact medieval stone walls, limestone Stradun street, and ocean panoramas.", 15500.00),
    ("Split", "Croatia", "Coastal Dalmatian city built inside the colossal 4th-century Roman ruins of Diocletian's Palace.", 13000.00),
    ("Zagreb", "Croatia", "Charming Austro-Hungarian capital featuring historic Upper Town, St. Mark's tiled roof church, and museum cafes.", 9500.00),
    ("Ljubljana", "Slovenia", "Green dragon capital featuring picturesque Triple Bridge, hilltop castle, and riverside outdoor cafes.", 11000.00),

    # Baltic & Balkans (6)
    ("Bled", "Slovenia", "Enchanting emerald alpine lake with a tiny church island reached by wooden pletna boats and cliffside castle.", 12500.00),
    ("Tallinn", "Estonia", "Intact medieval fairytale walled town in the Baltics with cobblestone alleys and modern digital tech culture.", 9500.00),
    ("Riga", "Latvia", "Baltic capital celebrated for Europe's finest collection of Art Nouveau architecture and historic Old Town.", 8800.00),
    ("Vilnius", "Lithuania", "Baroque jewel of the Baltics featuring Gediminas Tower, bohemian Uzupis artistic republic, and church spires.", 8200.00),
    ("Sofia", "Bulgaria", "Ancient Balkan capital nestled under Vitosha mountain featuring the golden-domed Alexander Nevsky Cathedral.", 7000.00),
    ("Belgrade", "Serbia", "High-energy Balkan crossroads city at the confluence of Sava and Danube rivers with Kalemegdan fortress.", 7200.00),

    # Greece (6)
    ("Athens", "Greece", "Cradle of Western civilization crowned by the ancient Acropolis, Parthenon temple, and vibrant Plaka district.", 12500.00),
    ("Santorini", "Greece", "Iconic Aegean volcanic island renowned for whitewashed cliffside villages of Oia, blue-domed churches, and caldera sunsets.", 21000.00),
    ("Mykonos", "Greece", "Glamorous Cycladic island famous for vibrant beach clubs, historic 16th-century windmills, and Little Venice.", 22000.00),
    ("Crete", "Greece", "Largest Greek island boasting Minoan palace ruins of Knossos, dramatic Samaria Gorge, and pink sand beaches.", 11500.00),
    ("Rhodes", "Greece", "Sun-drenched Aegean island featuring the massive walled medieval Old Town of the Knights of Saint John.", 11000.00),
    ("Thessaloniki", "Greece", "Greece's cultural co-capital renowned for Byzantine UNESCO monuments, waterfront White Tower, and vibrant culinary scene.", 10500.00),

    # =========================================================================
    # 4. NORTH AMERICA (51 destinations)
    # =========================================================================
    # USA (26)
    ("New York City", "United States", "Global metropolis featuring Times Square, Central Park, Broadway theatres, Statue of Liberty, and diverse food.", 24000.00),
    ("San Francisco", "United States", "Iconic hilly city by the bay famous for Golden Gate Bridge, historic cable cars, Alcatraz, and tech culture.", 22500.00),
    ("Los Angeles", "United States", "Entertainment capital home to Hollywood Walk of Fame, Beverly Hills glamour, Santa Monica Pier, and Pacific beaches.", 21000.00),
    ("Chicago", "United States", "Architectural showcase city on Lake Michigan famous for Millennium Park Bean, deep-dish pizza, and blues music.", 17500.00),
    ("Las Vegas", "United States", "World-famous desert entertainment capital known for dazzling Strip casino resorts, world-class dining, and shows.", 18500.00),
    ("Miami", "United States", "Sun-soaked coastal metropolis celebrated for South Beach Art Deco architecture, Latin dining, and nightlife.", 19500.00),
    ("Seattle", "United States", "Pacific Northwest tech and coffee hub featuring the Space Needle, Pike Place Market, and Puget Sound waters.", 18000.00),
    ("Boston", "United States", "Historic birthplace of American revolution featuring the Freedom Trail, Harvard University, and seafood.", 19000.00),
    ("Washington D.C.", "United States", "National capital featuring free Smithsonian museums, Lincoln Memorial, Capitol Hill, and cherry blossoms.", 18500.00),
    ("New Orleans", "United States", "Cultural gem on the Mississippi River famous for French Quarter jazz, Mardi Gras celebrations, and Creole cuisine.", 15500.00),
    ("Austin", "United States", "Live music capital of the world known for South Congress food trucks, Zilker Park, and barbecue.", 15000.00),
    ("Honolulu", "United States", "Hawaiian island capital boasting Waikiki Beach, Diamond Head volcanic crater, and Polynesian culture.", 23000.00),
    ("Orlando", "United States", "Global theme park capital home to Walt Disney World, Universal Studios, and family entertainment resorts.", 17000.00),
    ("San Diego", "United States", "SoCal coastal haven known for idyllic year-round climate, Balboa Park, world-famous zoo, and Pacific beaches.", 17500.00),
    ("Denver", "United States", "The Mile High City gateway to the Rocky Mountains, celebrated for craft breweries and Red Rocks Amphitheatre.", 16000.00),
    ("Nashville", "United States", "Music City USA celebrated for the Grand Ole Opry, Ryman Auditorium, Broadway honky-tonks, and hot chicken.", 16500.00),
    ("Portland", "United States", "Quirky Pacific Northwest city known for microbreweries, Powell's Books, urban food cart pods, and gardens.", 15000.00),
    ("Philadelphia", "United States", "Historic city of brotherly love featuring the Liberty Bell, Independence Hall, and famous Philly cheesesteaks.", 14500.00),
    ("Salt Lake City", "United States", "Scenic mountain capital surrounded by Wasatch peaks, world-class ski resorts, and historic Temple Square.", 14000.00),
    ("Savannah", "United States", "Charming Southern coastal city famous for historic oak-canopied squares, antebellum architecture, and ghost tours.", 14000.00),
    ("Santa Fe", "United States", "Artistic desert capital known for Pueblo-style adobe architecture, Georgia O'Keeffe art, and Southwestern cuisine.", 16000.00),
    ("Anchorage", "United States", "Alaskan wilderness hub offering glacier cruises, wildlife viewing, Chugach mountain trails, and midnight sun.", 21000.00),
    ("Sedona", "United States", "Arizona red rock sanctuary renowned for towering sandstone formations, spiritual energy vortexes, and hiking.", 18000.00),
    ("San Antonio", "United States", "Historic Texan city famous for the iconic Alamo mission and the scenic tree-lined River Walk promenade.", 13000.00),
    ("Atlanta", "United States", "Southern cultural and civil rights hub featuring the Georgia Aquarium, World of Coca-Cola, and Martin Luther King Jr. sites.", 14500.00),
    ("Charleston", "United States", "Historic coastal South Carolina port known for pastel antebellum French Quarter houses, cobblestone streets, and Lowcountry cuisine.", 16500.00),

    # Canada (11)
    ("Vancouver", "Canada", "Scenic Pacific coast metropolis nestled between snow-capped mountains and ocean, featuring Stanley Park.", 19000.00),
    ("Toronto", "Canada", "Multicultural commercial metropolis crowned by the CN Tower, Royal Ontario Museum, and diverse neighborhoods.", 17500.00),
    ("Montreal", "Canada", "French-Canadian cultural hub known for historic Old Montreal, Mount Royal park, and world-class culinary scene.", 15000.00),
    ("Quebec City", "Canada", "Charming fortified French-speaking city featuring the iconic Fairmont Le Chateau Frontenac and cobblestone alleys.", 14500.00),
    ("Banff", "Canada", "Premier Canadian Rockies alpine resort town surrounded by turquoise Lake Louise and Moraine Lake.", 21000.00),
    ("Calgary", "Canada", "Western Canadian gateway famous for the Calgary Stampede rodeo, cowboy heritage, and proximity to the Rockies.", 14000.00),
    ("Victoria", "Canada", "British Columbia's island capital known for Butchart Gardens, Inner Harbour, and British colonial tea rooms.", 16000.00),
    ("Ottawa", "Canada", "National capital showcasing the Gothic Parliament Hill, Rideau Canal ice skating, and national art galleries.", 14000.00),
    ("Jasper", "Canada", "Pristine Rocky Mountain national park sanctuary famous for dark sky stargazing, Athabasca glaciers, and wildlife.", 19000.00),
    ("Whistler", "Canada", "World-renowned ski and mountain resort offering Peak 2 Peak gondola, alpine downhill trails, and village nightlife.", 22500.00),
    ("Halifax", "Canada", "Historic Atlantic maritime port city known for seaside boardwalk, Citadel fortress, and fresh lobster dining.", 13500.00),

    # Mexico (9)
    ("Mexico City", "Mexico", "Vibrant high-altitude capital featuring Zocalo historic square, Frida Kahlo Museum, and world-class street food.", 7200.00),
    ("Cancun", "Mexico", "World-famous Caribbean beach resort destination known for turquoise waters, Hotel Zone nightlife, and Mayan ruins.", 11500.00),
    ("Playa del Carmen", "Mexico", "Riviera Maya coastal town with vibrant Fifth Avenue shopping, pristine beaches, and nearby cenotes.", 9500.00),
    ("Oaxaca", "Mexico", "Culinary and indigenous cultural soul of Mexico celebrated for mole sauces, mezcal tastings, and Monte Alban ruins.", 5800.00),
    ("Guadalajara", "Mexico", "Birthplace of mariachi music and tequila featuring historic colonial plazas, Hospicio Cabanas, and vibrant markets.", 6200.00),
    ("Puerto Vallarta", "Mexico", "Pacific coastal resort town blending traditional cobblestone Romantic Zone with golden beaches and whale watching.", 9000.00),
    ("San Miguel de Allende", "Mexico", "UNESCO colonial hill town renowned for the pink neo-Gothic Parroquia church, art galleries, and rooftop bars.", 8500.00),
    ("Tulum", "Mexico", "Bohemian eco-chic beach town famous for cliffside Mayan ruins overlooking turquoise Caribbean waters and cenotes.", 13500.00),
    ("Merida", "Mexico", "Cultural capital of Yucatan known for pastel colonial mansions on Paseo de Montejo and gateway to Chichen Itza.", 6000.00),

    # Central America & Caribbean (5)
    ("Havana", "Cuba", "Timeless Caribbean capital filled with vintage classic cars, Spanish colonial plazas in Old Havana, and salsa rhythms.", 6500.00),
    ("San Jose", "Costa Rica", "Capital city gateway to Costa Rica's cloud forests, active volcanoes, and biodiverse national parks.", 7800.00),
    ("Panama City", "Panama", "Modern skyline metropolis famous for the engineering marvel of the Panama Canal and historic Casco Viejo.", 8500.00),
    ("Antigua Guatemala", "Guatemala", "UNESCO World Heritage city framed by three volcanoes, featuring preserved Spanish Baroque colonial ruins.", 4800.00),
    ("San Juan", "Puerto Rico", "Vibrant Caribbean city featuring colorful Old San Juan cobblestone streets, El Morro fortress, and beach resorts.", 14500.00),

    # =========================================================================
    # 5. SOUTH AMERICA (26 destinations)
    # =========================================================================
    # Peru (4)
    ("Lima", "Peru", "Gastronomic capital of the Americas known for fresh ceviche, cliffside Miraflores district, and colonial architecture.", 6200.00),
    ("Cusco", "Peru", "Historic capital of the Inca Empire nestled in the Andes, gateway to the sacred wonder of Machu Picchu.", 5500.00),
    ("Arequipa", "Peru", "The White City built from volcanic sillar stone featuring the Santa Catalina Monastery and Colca Canyon access.", 4600.00),
    ("Puno", "Peru", "High-altitude city on Lake Titicaca famous for the floating reed islands of the indigenous Uros people.", 4200.00),

    # Brazil (7)
    ("Rio de Janeiro", "Brazil", "The Marvelous City famous for Christ the Redeemer, Sugarloaf Mountain, Copacabana and Ipanema beaches, and Samba.", 8500.00),
    ("Sao Paulo", "Brazil", "Vast cultural and financial mega-city renowned for world-class gastronomy, MASP art museum, and Ibirapuera Park.", 8000.00),
    ("Salvador", "Brazil", "Afro-Brazilian cultural heart in Bahia featuring colorful colonial Pelourinho district and capoeira martial arts.", 5800.00),
    ("Foz do Iguacu", "Brazil", "Home to the monumental Iguazu Falls, one of the world's most spectacular waterfalls in the rainforest.", 7200.00),
    ("Manaus", "Brazil", "Jungle metropolis in the heart of the Amazon rainforest featuring the historic Amazon Theatre opera house and river trips.", 6500.00),
    ("Florianopolis", "Brazil", "Island city famous for 42 stunning Atlantic beaches, surfing culture, and fresh oyster farming.", 6800.00),
    ("Paraty", "Brazil", "Preserved Portuguese colonial coastal town nestled between lush rainforest mountains and emerald tropical bays.", 6400.00),

    # Argentina (6)
    ("Buenos Aires", "Argentina", "Paris of South America celebrated for passionate Tango, colorful La Boca, historic cafes, and prime beef steakhouses.", 7200.00),
    ("Bariloche", "Argentina", "Andean resort town known for Swiss-style wooden architecture, artisanal chocolates, and Nahuel Huapi lake.", 8500.00),
    ("Mendoza", "Argentina", "World-renowned wine region in the shadow of the Andes mountains famous for Malbec vineyards and outdoor adventures.", 6800.00),
    ("Ushuaia", "Argentina", "The End of the World southernmost city on Tierra del Fuego, gateway to Beagle Channel and Antarctic cruises.", 11500.00),
    ("Salta", "Argentina", "Charming colonial city in northwest Argentina known as Salta the Beautiful, surrounded by colorful desert gorges.", 5200.00),
    ("El Calafate", "Argentina", "Patagonian gateway town to Los Glaciares National Park and the awe-inspiring Perito Moreno glacier.", 10500.00),

    # Chile (4)
    ("Santiago", "Chile", "Dynamic capital framed by snow-capped Andes mountains, featuring historic Plaza de Armas and vineyard valleys.", 8200.00),
    ("Valparaiso", "Chile", "Bohemian coastal port city celebrated for hillside funicular elevators, vibrant street art, and Pablo Neruda's home.", 6500.00),
    ("San Pedro de Atacama", "Chile", "Desert oasis town gateway to the otherworldly Moon Valley salt flats, geysers, and premier stargazing.", 10000.00),
    ("Puerto Varas", "Chile", "Picturesque lake district town with German heritage overlooking Lake Llanquihue and snow-capped Osorno volcano.", 7800.00),

    # Colombia, Ecuador, Bolivia (5)
    ("Bogota", "Colombia", "High-altitude cultural capital featuring the Gold Museum, Monserrate hilltop sanctuary, and historic La Candelaria.", 4800.00),
    ("Medellin", "Colombia", "City of Eternal Spring transformed by innovative cable cars, Botero sculpture plaza, and lush flower festivals.", 5200.00),
    ("Cartagena", "Colombia", "Fabled Caribbean walled city boasting colorful bougainvillea-draped colonial balconies and sea ramparts.", 6800.00),
    ("Quito", "Ecuador", "Highest constitutional capital in the world featuring South America's best-preserved UNESCO colonial historic center.", 5000.00),
    ("La Paz", "Bolivia", "High-altitude Andean metropolis featuring the world's highest cable car network (Mi Teleferico) and Witches' Market.", 3800.00),

    # =========================================================================
    # 6. MIDDLE EAST & NORTH AFRICA (34 destinations)
    # =========================================================================
    # UAE (4)
    ("Dubai", "United Arab Emirates", "Futuristic desert metropolis featuring Burj Khalifa, Dubai Mall, Palm Jumeirah, and luxury desert safaris.", 18500.00),
    ("Abu Dhabi", "United Arab Emirates", "Sophisticated UAE capital boasting the majestic Sheikh Zayed Grand Mosque and Louvre Abu Dhabi museum.", 16000.00),
    ("Sharjah", "United Arab Emirates", "UNESCO Cultural Capital of the Arab World celebrated for art heritage museums and Islamic architecture.", 9500.00),
    ("Ras Al Khaimah", "United Arab Emirates", "Scenic northern emirate known for rugged Jebel Jais mountain ziplines, terracotta desert dunes, and beaches.", 11000.00),

    # Saudi Arabia (4)
    ("Riyadh", "Saudi Arabia", "Dynamic Saudi capital blending futuristic skyscrapers like Kingdom Centre with historic Diriyah mud-brick city.", 14000.00),
    ("Jeddah", "Saudi Arabia", "Historic coastal Red Sea gateway famous for Al-Balad coral architecture, modern waterfront Corniche, and diving.", 13000.00),
    ("AlUla", "Saudi Arabia", "Ancient living museum featuring the rock-cut Nabataean tombs of Hegra, Elephant Rock, and oasis trails.", 22000.00),
    ("Medina", "Saudi Arabia", "Sacred Islamic holy city home to the Prophet's Mosque (Al-Masjid an-Nabawi) with towering umbrella architecture.", 9500.00),

    # Qatar, Oman, Bahrain, Kuwait (5)
    ("Doha", "Qatar", "Modern Gulf capital featuring the stunning Museum of Islamic Art, traditional Souq Waqif, and futuristic Katara village.", 15500.00),
    ("Muscat", "Oman", "Graceful coastal capital boasting the Sultan Qaboos Grand Mosque, Mutrah Corniche, and rugged mountain backdrops.", 12500.00),
    ("Salalah", "Oman", "Lush subtropical southern oasis famous for monsoon Khareef greenery, frankincense trees, and coconut beaches.", 11000.00),
    ("Manama", "Bahrain", "Island capital blending ancient Bahrain Fort, bustling Bab Al Bahrain souqs, and modern culinary dining.", 12000.00),
    ("Kuwait City", "Kuwait", "Gulf metropolis famous for the iconic Kuwait Towers, Grand Mosque, and modern waterfront promenades.", 13500.00),

    # Turkey (6)
    ("Istanbul", "Turkey", "Historic transcontinental city spanning Europe and Asia, home to Hagia Sophia, Blue Mosque, Grand Bazaar, and Bosphorus.", 9500.00),
    ("Goreme", "Turkey", "Heart of Cappadocia famous for sunrise hot air balloon flights over fairy chimneys and underground rock-cut cities.", 12500.00),
    ("Antalya", "Turkey", "Turquoise Coast resort city featuring the historic Kaleici old town, Roman Hadrian's Gate, and Mediterranean beaches.", 8500.00),
    ("Bodrum", "Turkey", "Charming Aegean coastal haven with whitewashed houses, Castle of St. Peter, and luxury sailing gulets.", 11500.00),
    ("Izmir", "Turkey", "Vibrant Aegean port city with historic Clock Tower, lively Kordon seaside promenade, and gateway to ancient Ephesus.", 7800.00),
    ("Fethiye", "Turkey", "Stunning coastal hub famous for the blue lagoon of Oludeniz, Lycian rock tombs, and paragliding from Babadag.", 8200.00),

    # Jordan & Levant (3)
    ("Amman", "Jordan", "Historic capital built across seven hills featuring the Roman Citadel, Roman Theatre, and bustling Rainbow Street.", 9500.00),
    ("Petra", "Jordan", "Rose-red city carved directly into sandstone cliffs by the Nabataeans, featuring the iconic Treasury and Monastery.", 14000.00),
    ("Aqaba", "Jordan", "Jordan's Red Sea port city renowned for colorful coral reef diving and access to the desert sands of Wadi Rum.", 10500.00),

    # Egypt (6)
    ("Cairo", "Egypt", "Sprawling capital on the Nile featuring the ancient Giza Pyramids, Great Sphinx, Khan el-Khalili bazaar, and Egyptian Museum.", 4800.00),
    ("Luxor", "Egypt", "World's greatest open-air museum featuring Karnak Temple, Luxor Temple, and the tombs of the Valley of the Kings.", 5200.00),
    ("Aswan", "Egypt", "Picturesque Nile city known for Philae Temple island, colorful Nubian villages, and serene felucca sailboat rides.", 4600.00),
    ("Alexandria", "Egypt", "Historic Mediterranean coastal city founded by Alexander the Great, featuring the modern Bibliotheca Alexandrina and Qaitbay citadel.", 4200.00),
    ("Sharm El Sheikh", "Egypt", "Red Sea resort capital renowned for world-class scuba diving at Ras Mohammed National Park and coral reefs.", 7500.00),
    ("Hurghada", "Egypt", "Vibrant Red Sea coastal resort town offering water sports, desert quad biking, and offshore coral island excursions.", 6800.00),

    # Morocco (6)
    ("Marrakech", "Morocco", "The Red City famous for the bustling Jemaa el-Fnaa square, Majorelle Garden, Bahia Palace, and souk spice stalls.", 6500.00),
    ("Casablanca", "Morocco", "Modern Atlantic coastal metropolis home to the colossal Hassan II Mosque with ocean-facing minaret.", 7200.00),
    ("Fes", "Morocco", "Medieval cultural and spiritual heart of Morocco boasting the labyrinthine Fes el-Bali medina and historic Chouara Tannery.", 5200.00),
    ("Chefchaouen", "Morocco", "The Blue Pearl nestled in the Rif mountains, famous for photogenic blue-washed buildings and peaceful mountain air.", 4600.00),
    ("Tangier", "Morocco", "Historic gateway port on the Strait of Gibraltar where the Mediterranean meets the Atlantic, rich in bohemian legacy.", 5800.00),
    ("Essaouira", "Morocco", "Laid-back Atlantic coastal port town enclosed by 18th-century sea ramparts, famous for seafood and windsurfing.", 5000.00),

    # =========================================================================
    # 7. SUB-SAHARAN AFRICA & ISLAND NATIONS (35 destinations)
    # =========================================================================
    # South Africa (6)
    ("Cape Town", "South Africa", "Stunning coastal city set beneath Table Mountain, featuring Cape Point, Boulders Beach penguins, and winelands.", 9500.00),
    ("Johannesburg", "South Africa", "South Africa's vibrant economic hub featuring the Apartheid Museum, Soweto history, and bustling Maboneng arts precinct.", 7500.00),
    ("Durban", "South Africa", "Golden Mile beachfront city on the Indian Ocean known for subtropical climate, Zulu culture, and Durban bunny chow.", 6500.00),
    ("Nelspruit", "South Africa", "Scenic gateway city in Mpumalanga to the premier wildlife safari landscapes of Kruger National Park.", 11500.00),
    ("Port Elizabeth", "South Africa", "Friendly City on the Sunshine Coast known for whale watching, clean beaches, and Addo Elephant National Park.", 7200.00),
    ("Stellenbosch", "South Africa", "Historic Cape Dutch town in the Cape Winelands surrounded by oak trees, vineyards, and mountain peaks.", 9000.00),

    # Kenya (5)
    ("Nairobi", "Kenya", "High-energy East African safari capital featuring the world's only national park within a capital city, and giraffe center.", 7800.00),
    ("Mombasa", "Kenya", "Historic coastal island port featuring the 16th-century Fort Jesus, Old Town spice markets, and white sandy beaches.", 6200.00),
    ("Narok", "Kenya", "Safari base town for the legendary Maasai Mara National Reserve, home to the Great Wildebeest Migration.", 16500.00),
    ("Diani Beach", "Kenya", "Award-winning tropical Indian Ocean beach paradise with powdery white sand, coral reefs, and water sports.", 8200.00),
    ("Nakuru", "Kenya", "Rift Valley city famous for Lake Nakuru National Park, flamingos, baboons, and sanctuary for endangered rhinos.", 7000.00),

    # Tanzania (4)
    ("Zanzibar City", "Tanzania", "Island spice paradise featuring the UNESCO-listed labyrinthine Stone Town, spice tours, and turquoise beaches.", 8500.00),
    ("Dar es Salaam", "Tanzania", "Bustling coastal commercial port city blending Swahili culture, fish markets, and ferry access to Zanzibar.", 5500.00),
    ("Arusha", "Tanzania", "Northern safari capital situated beneath Mount Meru, gateway to Serengeti, Ngorongoro Crater, and Kilimanjaro.", 14500.00),
    ("Seronera", "Tanzania", "Wildlife hub in central Serengeti National Park celebrated for predator sightings, savannah plains, and balloon safaris.", 22000.00),

    # Rwanda & Uganda (4)
    ("Kigali", "Rwanda", "Clean and orderly capital city nestled across lush hills, featuring the Kigali Genocide Memorial and coffee culture.", 6800.00),
    ("Musanze", "Rwanda", "Northern mountain base town for tracking endangered mountain gorillas in Volcanoes National Park.", 24000.00),
    ("Kampala", "Uganda", "Sprawling capital city perched on seven hills, home to Kasubi Tombs, vibrant craft markets, and Lake Victoria views.", 5200.00),
    ("Entebbe", "Uganda", "Tranquil peninsula town on Lake Victoria featuring historic botanical gardens, reptile sanctuary, and international airport.", 5800.00),

    # Ethiopia, Zimbabwe, Zambia, Namibia, Botswana (9)
    ("Addis Ababa", "Ethiopia", "Diplomatic capital of Africa featuring the National Museum with the Lucy fossil, Entoto hills, and coffee ceremonies.", 4600.00),
    ("Lalibela", "Ethiopia", "Spiritual mountain town world-famous for eleven monolithic rock-hewn medieval churches, including Church of St. George.", 5400.00),
    ("Victoria Falls", "Zimbabwe", "Adventure resort town home to the world's largest waterfall curtain, known locally as Mosi-oa-Tunya (The Smoke That Thunders).", 12500.00),
    ("Livingstone", "Zambia", "Zambian riverside base for Victoria Falls adventures, featuring the Devil's Pool and Zambezi river sunset cruises.", 11500.00),
    ("Windhoek", "Namibia", "Orderly desert capital blending German colonial architecture with modern African culture in the Khomas Highland.", 8200.00),
    ("Swakopmund", "Namibia", "Coastal adventure town where desert dunes meet the Atlantic Ocean, famous for sandboarding and quad biking.", 8800.00),
    ("Sossusvlei", "Namibia", "Spectacular desert salt and clay pan surrounded by the monumental red dunes of Dune 45 and ancient dead trees at Deadvlei.", 14000.00),
    ("Maun", "Botswana", "Safari tourism capital and primary jumping-off point for exploring the pristine waterways of the Okavango Delta.", 18500.00),
    ("Kasane", "Botswana", "Four-corners border town on the Chobe River famous for colossal elephant herds in Chobe National Park.", 16000.00),

    # Island Nations & West Africa (7)
    ("Port Louis", "Mauritius", "Mauritian capital city blending Caudan Waterfront, Aapravasi Ghat UNESCO site, and multicultural street food.", 11500.00),
    ("Grand Baie", "Mauritius", "Lively seaside resort village in northern Mauritius famous for turquoise emerald lagoons, yachting, and nightlife.", 13500.00),
    ("Victoria", "Seychelles", "Charming small capital of Seychelles on Mahe island with a silver clock tower, botanical gardens, and granite beaches.", 18500.00),
    ("Antananarivo", "Madagascar", "Hilltop Malagasy capital featuring the historic Rova palace, colorful hillside markets, and French bakery culture.", 4800.00),
    ("Nosy Be", "Madagascar", "Scented island paradise off the northwest coast known for ylang-ylang plantations, coral reefs, and lemurs.", 7800.00),
    ("Accra", "Ghana", "Vibrant West African capital featuring historic Jamestown lighthouse, Makola Market, and rich Pan-African heritage.", 5800.00),
    ("Dakar", "Senegal", "Vibrant Atlantic capital on the Cap-Vert peninsula famous for Goree Island history, surf beaches, and lively music.", 6200.00),

    # =========================================================================
    # 8. OCEANIA (20 destinations)
    # =========================================================================
    # Australia (10)
    ("Sydney", "Australia", "Iconic harbour city renowned for the Sydney Opera House, Sydney Harbour Bridge, Bondi Beach, and coastal walks.", 19500.00),
    ("Melbourne", "Australia", "Cultural and sporting capital celebrated for hidden laneway street art, world-famous specialty coffee, and Yarra River.", 18000.00),
    ("Brisbane", "Australia", "Subtropical riverside city featuring South Bank parklands, Lone Pine Koala Sanctuary, and vibrant outdoor dining.", 16000.00),
    ("Perth", "Australia", "Sunniest Australian state capital featuring expansive Kings Park, Cottesloe Beach, and nearby Rottnest Island quokkas.", 16500.00),
    ("Cairns", "Australia", "Tropical north gateway city to the world-famous Great Barrier Reef coral diving and ancient Daintree Rainforest.", 17500.00),
    ("Gold Coast", "Australia", "Famous coastal playground featuring Surfers Paradise golden beaches, high-rise skyline, theme parks, and hinterlands.", 17000.00),
    ("Adelaide", "Australia", "Cosmopolitan city of churches surrounded by parklands, Barossa Valley wine region, and Glenelg beach tram.", 15500.00),
    ("Hobart", "Australia", "Tasmanian island capital situated beneath Mount Wellington, famous for MONA museum and Salamanca Market.", 16500.00),
    ("Darwin", "Australia", "Tropical Top End capital known for Mindil Beach sunset markets, Crocosaurus Cove, and gateway to Kakadu National Park.", 15500.00),
    ("Alice Springs", "Australia", "Heart of the Red Centre desert outback, rich in Aboriginal art and gateway to Uluru-Kata Tjuta National Park.", 17000.00),

    # New Zealand (7)
    ("Auckland", "New Zealand", "City of Sails featuring the iconic Sky Tower, two natural harbours, volcanic cones, and Waiheke Island vineyards.", 18500.00),
    ("Queenstown", "New Zealand", "Global adventure capital on Lake Wakatipu surrounded by The Remarkables, famous for bungy jumping, skiing, and Milford Sound.", 22000.00),
    ("Christchurch", "New Zealand", "Garden City on the South Island featuring Avon River punting, modern cardboard cathedral, and Botanic Gardens.", 16500.00),
    ("Wellington", "New Zealand", "Windy cultural and film capital boasting the interactive Te Papa national museum, cable car, and craft beer.", 17000.00),
    ("Rotorua", "New Zealand", "Geothermal wonderland famous for bubbling mud pools, natural hot springs, and authentic Maori cultural experiences.", 16500.00),
    ("Wanaka", "New Zealand", "Scenic South Island alpine resort town known for the famous lone willow tree in Lake Wanaka and Roys Peak hike.", 18000.00),
    ("Napier", "New Zealand", "Art Deco capital of the world rebuilt after a 1931 earthquake, featuring Hawke's Bay wineries and seaside promenade.", 15000.00),

    # Fiji & French Polynesia (3)
    ("Nadi", "Fiji", "Main gateway city on Viti Levu island featuring Sri Siva Subramaniya Hindu temple and access to Mamanuca island resorts.", 14000.00),
    ("Suva", "Fiji", "Lively South Pacific capital city featuring the Fiji Museum, Thurston Gardens, and vibrant colonial harbor.", 11500.00),
    ("Papeete", "French Polynesia", "Tropical capital of Tahiti featuring vibrant municipal markets, black sand beaches, and gateway to Bora Bora.", 24000.00),
]


def validate_dataset_in_memory() -> Dict[str, Any]:
    """Validate all records before database interaction."""
    errors = []
    seen_pairs = set()
    seen_descriptions = set()

    # Add existing destinations to seen pairs
    for city, country in EXISTING_DESTINATIONS:
        seen_pairs.add((city.strip().lower(), country.strip().lower()))

    for idx, (city, country, desc, cost) in enumerate(NEW_DESTINATIONS_DATA, 1):
        pair = (city.strip().lower(), country.strip().lower())
        if pair in seen_pairs:
            errors.append(f"Row {idx}: Duplicate city-country combination: '{city}', '{country}'")
        seen_pairs.add(pair)

        if desc.strip() in seen_descriptions:
            errors.append(f"Row {idx}: Duplicate description for '{city}': '{desc[:40]}...'")
        seen_descriptions.add(desc.strip())

        if not city or len(city) < 2 or len(city) > 100:
            errors.append(f"Row {idx}: Invalid city length '{city}' ({len(city)})")

        if not country or len(country) < 2 or len(country) > 100:
            errors.append(f"Row {idx}: Invalid country length '{country}' ({len(country)})")

        if not desc or len(desc) < 15 or len(desc) > 1000:
            errors.append(f"Row {idx}: Invalid description length for '{city}' ({len(desc)})")

        if cost is None or cost <= 0:
            errors.append(f"Row {idx}: Invalid cost for '{city}': {cost}")

    return {
        "valid": len(errors) == 0,
        "new_count": len(NEW_DESTINATIONS_DATA),
        "existing_count": len(EXISTING_DESTINATIONS),
        "total_count": len(NEW_DESTINATIONS_DATA) + len(EXISTING_DESTINATIONS),
        "errors": errors,
    }


def export_master_json(output_path: Path) -> None:
    """Export dataset to machine-readable JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for city, country, desc, cost in NEW_DESTINATIONS_DATA:
        records.append({
            "city": city,
            "country": country,
            "description": desc,
            "average_daily_cost": cost,
            "active": True,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    logger.info(f"Exported master seed dataset to {output_path}")


def seed_destinations(dry_run: bool = False) -> Dict[str, Any]:
    """Seed destinations into PostgreSQL database in a single safe transaction."""
    val = validate_dataset_in_memory()
    if not val["valid"]:
        logger.error(f"In-memory dataset validation failed with {len(val['errors'])} errors:")
        for err in val["errors"][:10]:
            logger.error(f"  {err}")
        return val

    logger.info(f"In-memory dataset validated successfully: {val['new_count']} new destinations prepared (Total: {val['total_count']}).")

    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine could not be initialized.")

    with Session(engine) as session:
        # 1. Verify existing records
        existing_rows = session.execute(
            select(Destination.id, Destination.city, Destination.country, Destination.average_daily_cost, Destination.active)
            .order_by(Destination.id)
        ).all()

        existing_map = {(row.city.strip().lower(), row.country.strip().lower()): row for row in existing_rows}
        logger.info(f"Database currently contains {len(existing_rows)} destination records.")

        # Ensure all 5 standard existing destinations are present
        for city, country in EXISTING_DESTINATIONS:
            key = (city.lower(), country.lower())
            if key not in existing_map:
                logger.warning(f"Existing expected destination '{city}, {country}' was not found in DB.")

        inserted_count = 0
        skipped_count = 0
        dest_objects_to_add = []

        for city, country, desc, cost in NEW_DESTINATIONS_DATA:
            key = (city.strip().lower(), country.strip().lower())
            if key in existing_map:
                skipped_count += 1
                continue

            dest = Destination(
                city=city.strip(),
                country=country.strip(),
                description=desc.strip(),
                average_daily_cost=Decimal(str(cost)),
                active=True,
            )
            dest_objects_to_add.append(dest)

        if dry_run:
            logger.info(f"[DRY RUN] Would insert {len(dest_objects_to_add)} destinations, skipped {skipped_count}.")
            return {
                "success": True,
                "dry_run": True,
                "would_insert": len(dest_objects_to_add),
                "skipped": skipped_count,
                "initial_count": len(existing_rows),
                "projected_total": len(existing_rows) + len(dest_objects_to_add),
            }

        logger.info(f"Inserting {len(dest_objects_to_add)} new destination records into PostgreSQL...")
        session.add_all(dest_objects_to_add)
        session.commit()

        # Re-verify total in database
        final_count = session.execute(select(func.count(Destination.id))).scalar()
        countries_count = session.execute(select(func.count(func.distinct(Destination.country)))).scalar()

        logger.info(f"Seeding completed successfully! Total destinations in DB: {final_count} across {countries_count} countries.")

        # Also write JSON manifest
        json_path = backend_dir.parent / "database" / "seeds" / "destinations_master_d1.json"
        export_master_json(json_path)

        return {
            "success": True,
            "dry_run": False,
            "initial_count": len(existing_rows),
            "inserted_count": len(dest_objects_to_add),
            "skipped_count": skipped_count,
            "final_count": final_count,
            "countries_count": countries_count,
        }


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    result = seed_destinations(dry_run=dry)
    print(json.dumps(result, indent=2, default=str))
