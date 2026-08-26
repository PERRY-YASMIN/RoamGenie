"""Master Transport Dataset Generator (Phase D5)
Provides a rich, deterministic, geographically authentic catalog of 6,000 transport options across all 500 destinations.
"""
import hashlib
import random
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

RANDOM_SEED = 20260820

# 8 Preserved Original Transport Records from initial seed:
# (1, 'Bengaluru', 1, 'train', 'Vande Bharat Express', 550.00, 120)
# (2, 'Bengaluru', 1, 'bus', 'KSRTC Airavat', 450.00, 180)
# (3, 'Chennai', 1, 'train', 'Kaveri Express', 850.00, 480)
# (4, 'Bengaluru', 2, 'flight', 'IndiGo', 3200.00, 65)
# (5, 'Bengaluru', 2, 'train', 'Ernakulam Express', 1100.00, 580)
# (6, 'Delhi', 3, 'train', 'Ajmer Shatabdi', 750.00, 240)
# (7, 'Mumbai', 4, 'flight', 'Air India', 4500.00, 80)
# (8, 'Mumbai', 5, 'train', 'Konkan Kanya Express', 950.00, 660)

# Format of each tuple: (origin, mode, provider, estimated_cost, duration_minutes)
CURATED_LANDMARK_TRANSPORTS: Dict[Tuple[str, str], List[Tuple[str, str, str, float, int]]] = {
    ("Mysuru", "India"): [
        ("Bengaluru", "train", "Vande Bharat Express", 550.0, 120),            # Preserved ID 1
        ("Bengaluru", "bus", "KSRTC Airavat", 450.0, 180),                    # Preserved ID 2
        ("Chennai", "train", "Kaveri Express", 850.0, 480),                   # Preserved ID 3
        ("Bengaluru Airport", "bus", "KSRTC Flybus Non-Stop Express", 800.0, 210),
        ("Bengaluru", "taxi", "Ola / Uber Outstation Intercity Cab", 2800.0, 180),
        ("Mysuru", "bus", "Mysuru City Bus Service (KSRTC Local)", 35.0, 35),
        ("Mysuru", "auto-rickshaw", "Mysuru Heritage City Auto Union", 120.0, 25),
        ("Mysuru", "private-transfer", "Royal Mysore Chauffeur AC Sedan", 2200.0, 480),
        ("Mysuru", "car-rental", "Zoomcar Self-Drive Car Rental", 1800.0, 720),
        ("Mysuru", "bike-rental", "Royal Mysore Heritage Bicycle & e-Bike", 150.0, 360),
        ("Mysuru", "shuttle", "Chamundi Hill Panoramic Tourist Shuttle", 60.0, 30),
        ("Bengaluru", "flight", "Alliance Air Regional Shuttle", 2400.0, 40),
    ],
    ("Kochi", "India"): [
        ("Bengaluru", "flight", "IndiGo", 3200.0, 65),                         # Preserved ID 4
        ("Bengaluru", "train", "Ernakulam Express", 1100.0, 580),              # Preserved ID 5
        ("Kochi", "ferry", "Kochi Water Metro (High-Tech Electric Ferry)", 40.0, 25),
        ("Kochi", "metro", "Kochi Metro Rail (KMRL Aluva-Thripunithura)", 60.0, 40),
        ("Kochi", "ferry", "Fort Kochi - Vypin Heritage Ro-Ro Passenger Ferry", 20.0, 15),
        ("Cochin International Airport", "taxi", "CIAL Prepaid Airport Taxi Service", 1100.0, 60),
        ("Kochi", "auto-rickshaw", "Fort Kochi Coastal Tuk-Tuk Drivers Guild", 150.0, 25),
        ("Trivandrum", "train", "Vande Bharat Express (Southern Railway)", 750.0, 190),
        ("Kochi", "ride-hailing", "Uber Premier Kochi City Transit", 450.0, 40),
        ("Bengaluru", "bus", "Kerala State RTC Swift Deluxe AC Sleeper", 1250.0, 540),
        ("Kochi", "car-rental", "Avis Self-Drive Coastal Car Rental", 2400.0, 720),
        ("Kochi", "private-transfer", "Backwaters Luxury Chauffeur Sedan", 3200.0, 480),
    ],
    ("Jaipur", "India"): [
        ("Delhi", "train", "Ajmer Shatabdi", 750.0, 240),                     # Preserved ID 6
        ("Delhi", "flight", "IndiGo", 2800.0, 55),
        ("Delhi", "train", "Vande Bharat Express (Delhi-Jaipur Superfast)", 950.0, 205),
        ("Delhi", "bus", "RSRTC Volvo Super Luxury AC Bus", 650.0, 300),
        ("Jaipur", "metro", "Jaipur Metro Rail (Mansarovar to Badi Chaupar)", 30.0, 25),
        ("Jaipur", "auto-rickshaw", "Pink City Auto-Rickshaw Union", 140.0, 25),
        ("Jaipur Airport", "taxi", "Sanganer Airport Prepaid Taxi", 600.0, 40),
        ("Jaipur", "private-transfer", "Rajputana Royal Chauffeur Sedan", 2800.0, 480),
        ("Jaipur", "shuttle", "Amer Fort Hill Heritage Jeep Shuttle", 200.0, 20),
        ("Jaipur", "ride-hailing", "Uber Go Jaipur City Transit", 280.0, 30),
        ("Jaipur", "car-rental", "Zoomcar Self-Drive Rental", 1900.0, 720),
        ("Mumbai", "flight", "Air India", 4200.0, 105),
    ],
    ("Udaipur", "India"): [
        ("Mumbai", "flight", "Air India", 4500.0, 80),                        # Preserved ID 7
        ("Delhi", "train", "Mewar Superfast Express", 820.0, 720),
        ("Delhi", "flight", "IndiGo", 3800.0, 75),
        ("Jaipur", "bus", "RSRTC Goldline AC Sleeper Bus", 650.0, 360),
        ("Udaipur", "ferry", "Lake Pichola Heritage Public Ferry Boat", 250.0, 30),
        ("Udaipur", "cable-car", "Mansapurna Karni Mata Scenic Ropeway", 110.0, 15),
        ("Udaipur", "auto-rickshaw", "Lake City Auto-Rickshaw Service", 150.0, 20),
        ("Maharana Pratap Airport", "taxi", "Udaipur Airport Official Prepaid Taxi", 850.0, 45),
        ("Udaipur", "private-transfer", "Mewar Royal Chauffeur SUV", 3400.0, 480),
        ("Udaipur", "ride-hailing", "Uber Premier Udaipur", 350.0, 30),
        ("Udaipur", "bike-rental", "Royal Enfield Lake Circuit Motorcycle Rental", 1100.0, 720),
        ("Ahmedabad", "train", "Asarva Udaipur Express", 350.0, 260),
    ],
    ("Goa", "India"): [
        ("Mumbai", "train", "Konkan Kanya Express", 950.0, 660),              # Preserved ID 8
        ("Mumbai", "flight", "IndiGo", 3400.0, 65),
        ("Bengaluru", "flight", "Air India Express", 3100.0, 70),
        ("Mumbai", "train", "Goa Tejas / Vande Bharat Express", 1650.0, 460),
        ("Goa", "ferry", "Goa River Navigation Ferry (Mandovi & Betim)", 30.0, 20),
        ("Goa", "bike-rental", "Goa Beach Scooter / Activa Daily Rental", 450.0, 720),
        ("Goa", "car-rental", "Self-Drive Mahindra Thar / Open Jeep Rental", 2800.0, 720),
        ("Goa Airport (Dabolim / Mopa)", "taxi", "GoaMiles App / Prepaid Airport Cab", 1400.0, 55),
        ("Goa", "bus", "Kadamba Transport AC Airport Express Bus", 200.0, 75),
        ("Goa", "private-transfer", "Luxury Coastal Chauffeur Innova Crysta", 3800.0, 480),
        ("Goa", "ride-hailing", "GoaMiles Official App Taxi", 650.0, 35),
        ("Goa", "shuttle", "Dudhsagar Falls 4x4 Off-Road Safari Jeep", 600.0, 60),
    ],
    ("Paris", "France"): [
        ("Paris", "metro", "Paris Metro RATP (Subway Network)", 240.0, 25),
        ("Paris CDG Airport", "train", "RER B Airport Express Train to Châtelet", 1050.0, 35),
        ("London", "train", "Eurostar High-Speed Rail (St Pancras - Gare du Nord)", 7500.0, 140),
        ("Lyon", "train", "SNCF TGV INOUI High-Speed Rail", 3800.0, 115),
        ("Paris", "ferry", "Batobus Seine River Passenger Hop-on Ferry", 1600.0, 90),
        ("Paris", "tram", "Tramway d'Île-de-France (RATP Light Rail)", 220.0, 30),
        ("Paris", "cable-car", "Funiculaire de Montmartre (Sacré-Cœur Funicular)", 210.0, 10),
        ("Paris CDG Airport", "bus", "RoissyBus Direct Airport Shuttle", 1450.0, 60),
        ("Paris", "taxi", "G7 Official Parisian Metered Taxi", 2800.0, 30),
        ("Paris", "ride-hailing", "Uber Green Paris Eco Ride-Hailing", 2200.0, 25),
        ("Paris", "bike-rental", "Vélib' Métropole City Bike Share", 450.0, 360),
        ("Paris", "private-transfer", "Parisian Luxury Mercedes Chauffeur", 8500.0, 180),
    ],
    ("Tokyo", "Japan"): [
        ("Tokyo", "train", "JR East Yamanote Line Loop", 180.0, 30),
        ("Tokyo", "metro", "Tokyo Metro Ginza & Marunouchi Lines", 210.0, 25),
        ("Osaka", "train", "Shinkansen Nozomi Bullet Train (JR Central)", 8800.0, 145),
        ("Narita Airport", "train", "JR Narita Express (N'EX)", 2200.0, 60),
        ("Haneda Airport", "train", "Tokyo Monorail Express to Hamamatsucho", 450.0, 20),
        ("Tokyo", "ferry", "Tokyo Water Bus Tokyo Cruise (Asakusa - Odaiba)", 850.0, 45),
        ("Tokyo", "taxi", "Nihon Kotsu Tokyo Metered Taxi", 2600.0, 25),
        ("Narita Airport", "bus", "Airport Limousine Bus Tokyo", 1900.0, 80),
        ("Tokyo", "ride-hailing", "Uber Black Tokyo Premium Transit", 3400.0, 25),
        ("Tokyo", "bike-rental", "Docomo Bike Share Tokyo", 350.0, 180),
        ("Tokyo", "car-rental", "Times CAR RENTAL Self-Drive Japan", 4800.0, 720),
        ("Hakone", "train", "Odakyu Electric Railway Romancecar", 1600.0, 85),
    ],
    ("London", "United Kingdom"): [
        ("London", "metro", "London Underground Tube (TfL Network)", 320.0, 25),
        ("Heathrow Airport", "train", "Heathrow Express 15-Minute Non-Stop", 2400.0, 15),
        ("London", "train", "Elizabeth Line Cross-Rail (TfL)", 950.0, 35),
        ("London", "bus", "TfL Iconic Red Double-Decker City Bus", 180.0, 35),
        ("London", "ferry", "Uber Boat by Thames Clippers River Bus", 980.0, 40),
        ("London", "taxi", "Official London Black Hackney Carriage", 3200.0, 30),
        ("Paris", "train", "Eurostar London-Paris High Speed Rail", 7800.0, 140),
        ("Edinburgh", "train", "LNER Azuma East Coast Main Line", 5200.0, 260),
        ("Gatwick Airport", "train", "Gatwick Express to London Victoria", 1950.0, 30),
        ("London", "bike-rental", "Santander Cycles TfL Bike Share", 350.0, 240),
        ("London", "ride-hailing", "Uber London Ride-Hailing", 2100.0, 25),
        ("London", "private-transfer", "Addison Lee Premium Chauffeur", 5800.0, 120),
    ],
    ("New York City", "United States"): [
        ("New York City", "metro", "MTA New York City Subway 24/7", 250.0, 30),
        ("JFK Airport", "train", "JFK AirTrain & Long Island Rail Road Express", 1350.0, 40),
        ("New York City", "ferry", "NYC Ferry (East River & Rockaway Routes)", 360.0, 35),
        ("New York City", "taxi", "Official NYC Yellow Medallion Cab", 3200.0, 30),
        ("New York City", "ride-hailing", "UberX NYC Ride-Hailing", 2600.0, 25),
        ("Boston", "train", "Amtrak Acela High-Speed Express Rail", 6800.0, 215),
        ("Washington DC", "train", "Amtrak Northeast Regional Train", 4500.0, 200),
        ("Staten Island", "ferry", "Staten Island Ferry (Free Transit)", 30.0, 25),
        ("New York City", "bike-rental", "Citi Bike NYC Bicycle Share", 420.0, 180),
        ("Newark Airport", "bus", "Newark Airport Express Bus to Port Authority", 1600.0, 50),
        ("New York City", "car-rental", "Hertz Manhattan Car Rental", 6200.0, 720),
        ("New York City", "private-transfer", "Carmel Luxury Limousine & Chauffeur", 8800.0, 90),
    ],
    ("Rome", "Italy"): [
        ("Rome", "metro", "Rome Metro Line A & B (ATAC Network)", 180.0, 25),
        ("Fiumicino Airport", "train", "Trenitalia Leonardo Express Direct", 1300.0, 32),
        ("Florence", "train", "Trenitalia Frecciarossa High-Speed Rail", 3200.0, 90),
        ("Milan", "train", "Italo High-Speed Train", 4500.0, 190),
        ("Rome", "tram", "ATAC Rome City Tramway (Lines 2, 3 & 8)", 170.0, 30),
        ("Rome", "taxi", "Radio Taxi 3570 Roma Official Metered", 2400.0, 30),
        ("Rome", "ride-hailing", "Uber Black Roma NCC Chauffeur", 3100.0, 25),
        ("Rome", "bike-rental", "Lime e-Bike & Scooter Share Roma", 380.0, 120),
        ("Fiumicino Airport", "bus", "SITBus Shuttle to Roma Termini", 650.0, 55),
        ("Rome", "car-rental", "Avis Autonoleggio Roma Car Hire", 4200.0, 720),
        ("Rome", "shuttle", "Rome Hop-on Hop-off Panoramic Sightseeing Bus", 2200.0, 120),
        ("Rome", "private-transfer", "Vatican & Heritage Luxury Chauffeur Mercedes", 6500.0, 240),
    ],
    ("Dubai", "United Arab Emirates"): [
        ("Dubai", "metro", "Dubai Metro Red & Green Lines (RTA)", 180.0, 25),
        ("Dubai", "tram", "Dubai Tram (JBR & Dubai Marina)", 120.0, 20),
        ("Dubai", "ferry", "Dubai Creek Traditional Abra Wooden Boat", 50.0, 15),
        ("Dubai", "taxi", "Dubai Taxi Corporation (RTA Hala Metered)", 1400.0, 30),
        ("Dubai", "ride-hailing", "Careem / Uber Dubai Chauffeur", 1900.0, 25),
        ("Dubai", "ferry", "Dubai Ferry Marine Transit (Marina to Canal)", 600.0, 50),
        ("Dubai", "shuttle", "The Palm Monorail to Atlantis Aquaventure", 250.0, 15),
        ("Abu Dhabi", "bus", "RTA Intercity Express Coach E100", 350.0, 90),
        ("Dubai Airport", "taxi", "Dubai Airport Official Taxi Transfer", 1800.0, 35),
        ("Dubai", "car-rental", "Budget Rent a Car Dubai Self-Drive", 3600.0, 720),
        ("Dubai", "private-transfer", "Emirates First & Business Chauffeur-Drive", 7500.0, 120),
        ("Dubai", "shuttle", "Desert Safari 4x4 Land Cruiser Dune Transfer", 2800.0, 180),
    ],
    ("Singapore", "Singapore"): [
        ("Singapore", "metro", "Singapore SMRT & SBS Mass Rapid Transit (MRT)", 160.0, 25),
        ("Changi Airport", "train", "Changi Airport MRT Link to City", 200.0, 30),
        ("Singapore", "bus", "SBS Transit & SMRT Double-Decker Public Bus", 120.0, 35),
        ("Singapore", "ferry", "Singapore River Cruise Electric Bumboat", 1650.0, 40),
        ("Singapore", "cable-car", "Mount Faber & Sentosa Island Cable Car", 2200.0, 25),
        ("Singapore", "taxi", "ComfortDelGro City Cab Metered", 1450.0, 25),
        ("Singapore", "ride-hailing", "GrabCar Singapore Ride-Hailing", 1600.0, 20),
        ("Kuala Lumpur", "bus", "Aeroline Luxury Cross-Border Coach", 2400.0, 330),
        ("Singapore", "bike-rental", "Anywheel Singapore Bike Share", 250.0, 180),
        ("Singapore", "shuttle", "Sentosa Express Monorail Train", 280.0, 15),
        ("Singapore", "car-rental", "BlueSG Electric Car Sharing", 1800.0, 240),
        ("Singapore", "private-transfer", "Singapore VIP Mercedes Chauffeur", 6200.0, 180),
    ],
    ("Sydney", "Australia"): [
        ("Sydney", "train", "Sydney Trains Suburban & Intercity Network", 280.0, 30),
        ("Sydney Airport", "train", "Sydney Airport Link Train to Central Station", 1150.0, 15),
        ("Sydney", "ferry", "Sydney Ferries (Circular Quay to Manly F1)", 480.0, 30),
        ("Sydney", "metro", "Sydney Metro Northwest & City Line", 260.0, 25),
        ("Sydney", "tram", "Sydney Light Rail (CBD & South East L2/L3)", 240.0, 25),
        ("Sydney", "taxi", "13CABS Sydney Metered Taxi", 2400.0, 30),
        ("Sydney", "ride-hailing", "Uber Premier Sydney Ride-Hailing", 2100.0, 25),
        ("Melbourne", "flight", "Qantas Airways Express", 5800.0, 90),
        ("Blue Mountains", "train", "NSW TrainLink Blue Mountains Express", 580.0, 120),
        ("Sydney", "bike-rental", "Beam e-Bike Share Sydney", 350.0, 120),
        ("Sydney", "car-rental", "Hertz Australia Car Rental", 5200.0, 720),
        ("Sydney", "private-transfer", "Harbour City Chauffeur Luxury Sedan", 6800.0, 120),
    ],
    ("Bangkok", "Thailand"): [
        ("Bangkok", "metro", "BTS Skytrain Sukhumvit & Silom Lines", 110.0, 20),
        ("Bangkok", "metro", "MRT Bangkok Underground Blue Line", 100.0, 25),
        ("Suvarnabhumi Airport", "train", "Suvarnabhumi Airport Rail Link Express", 120.0, 28),
        ("Bangkok", "ferry", "Chao Phraya Express Orange Flag Boat", 45.0, 30),
        ("Bangkok", "auto-rickshaw", "Bangkok Iconic Motorized Tuk-Tuk", 180.0, 20),
        ("Bangkok", "taxi", "Bangkok Metered Taxi (Pink & Green-Yellow)", 350.0, 35),
        ("Bangkok", "ride-hailing", "GrabCar Bangkok Ride-Hailing", 420.0, 30),
        ("Pattaya", "bus", "Roong Reuang Intercity Coach", 380.0, 130),
        ("Chiang Mai", "train", "State Railway of Thailand Special Express Sleeper", 1800.0, 680),
        ("Bangkok", "shuttle", "Asiatique The Riverfront Free Shuttle Boat", 40.0, 15),
        ("Bangkok", "bike-rental", "Pun-Pun Bangkok Bike Share", 80.0, 120),
        ("Bangkok", "private-transfer", "Siam Luxury Chauffeur Van / Alphard", 4200.0, 240),
    ],
    ("Cape Town", "South Africa"): [
        ("Cape Town", "bus", "MyCiTi Integrated Rapid Transit Bus", 150.0, 30),
        ("Cape Town", "cable-car", "Table Mountain Aerial Cableway", 2100.0, 15),
        ("Cape Town Airport", "taxi", "Cape Town Airport Official Authorized Cab", 1800.0, 35),
        ("Cape Town", "ride-hailing", "Uber Black Cape Town", 1400.0, 25),
        ("Cape Town", "ferry", "Robben Island Passenger Catamaran Ferry", 2800.0, 45),
        ("Cape Town", "train", "Metrorail Western Cape Southern Line", 120.0, 50),
        ("Johannesburg", "flight", "FlySafair Express", 4800.0, 130),
        ("Cape Town", "shuttle", "City Sightseeing Cape Town Hop-On Hop-Off Bus", 1650.0, 120),
        ("Cape Town", "bike-rental", "Atlantic Seaboard Promenade Bicycle Hire", 450.0, 180),
        ("Cape Town", "car-rental", "Avis South Africa Self-Drive Rental", 3600.0, 720),
        ("Cape Town", "bus", "Intercape Mainliner Intercity Coach", 2200.0, 480),
        ("Cape Town", "private-transfer", "Cape Point & Wine Country Luxury Chauffeur", 6400.0, 480),
    ],
    ("Cairo", "Egypt"): [
        ("Cairo", "metro", "Cairo Metro Network (Lines 1, 2 & 3)", 50.0, 30),
        ("Cairo", "train", "Egyptian National Railways Express Train", 450.0, 150),
        ("Cairo", "ferry", "Nile Water Taxi & Historic River Bus", 80.0, 25),
        ("Cairo", "taxi", "Cairo White Metered City Taxi", 350.0, 30),
        ("Cairo", "ride-hailing", "Uber / Careem Cairo Ride-Hailing", 420.0, 25),
        ("Cairo Airport", "bus", "Cairo Airport Express Transit Coach", 180.0, 60),
        ("Giza", "shuttle", "Giza Pyramids Electric Shuttle Bus", 150.0, 20),
        ("Alexandria", "train", "ENR Spanish Talgo Superfast Air-Conditioned Train", 750.0, 140),
        ("Cairo", "auto-rickshaw", "Cairo Suburban Tuk-Tuk Transit", 60.0, 15),
        ("Cairo", "ferry", "Traditional Nile Felucca Sunset Sailing Boat", 850.0, 60),
        ("Cairo", "car-rental", "Europcar Cairo Self-Drive Rental", 2900.0, 720),
        ("Cairo", "private-transfer", "Pharaonic Heritage Private Chauffeur Sedan", 3600.0, 480),
    ],
}

# Regional Hubs mapping for Intercity Routes
REGIONAL_ORIGIN_HUBS: Dict[str, List[str]] = {
    "India": ["Bengaluru", "Delhi", "Mumbai", "Chennai", "Kolkata", "Hyderabad", "Pune", "Kochi", "Ahmedabad", "Jaipur", "Chandigarh", "Lucknow"],
    "Europe": ["London", "Paris", "Rome", "Frankfurt", "Madrid", "Zurich", "Amsterdam", "Milan", "Vienna", "Barcelona", "Munich", "Prague", "Brussels", "Athens"],
    "North_America": ["New York City", "Los Angeles", "Chicago", "Miami", "San Francisco", "Dallas", "Toronto", "Vancouver", "Seattle", "Boston", "Las Vegas", "Montreal"],
    "East_Asia": ["Tokyo", "Osaka", "Seoul", "Beijing", "Shanghai", "Taipei", "Kyoto", "Hong Kong", "Guangzhou"],
    "Southeast_Asia": ["Bangkok", "Singapore", "Kuala Lumpur", "Bali", "Manila", "Jakarta", "Ho Chi Minh City", "Hanoi", "Phuket"],
    "Middle_East": ["Dubai", "Abu Dhabi", "Doha", "Cairo", "Istanbul", "Riyadh", "Jeddah", "Amman", "Muscat"],
    "Latin_America": ["Mexico City", "Buenos Aires", "Rio de Janeiro", "Lima", "Santiago", "Bogotá", "Cancún", "São Paulo", "Medellín"],
    "Africa": ["Cape Town", "Johannesburg", "Nairobi", "Cairo", "Marrakech", "Casablanca", "Addis Ababa", "Kigali"],
    "Oceania": ["Sydney", "Melbourne", "Auckland", "Brisbane", "Perth", "Adelaide", "Christchurch", "Queenstown"],
}

# Regional Airline, Railway, Transit Operators, and Brand Data
REGIONAL_OPERATORS: Dict[str, Dict[str, List[str]]] = {
    "India": {
        "airlines": ["IndiGo", "Air India", "Air India Express", "SpiceJet", "Akasa Air", "Alliance Air"],
        "railways": ["Vande Bharat Express", "Shatabdi Express", "Rajdhani Superfast", "Jan Shatabdi Express", "Garib Rath Express", "Intercity Superfast Express"],
        "bus_operators": ["KSRTC Airavat Club Class", "MSRTC Shivneri Volvo", "RSRTC Volvo Super Luxury", "APSRTC Garuda Plus", "Zingbus Electric Intercity", "IntrCity SmartBus"],
        "local_transit": ["City Metro Rail", "City Rapid Transit Bus (BRTS)", "Municipal Public City Bus", "City Electric Bus Fleet"],
        "taxi_services": ["Prepaid Airport Taxi Union", "City Metered Taxi Cab", "Regional Outstation Taxi", "FastTrack Cabs"],
        "ride_hailing": ["Uber Go", "Ola Prime", "Rapido Auto & Cab", "Uber Premier", "Ola Electric"],
        "auto_services": ["City Auto-Rickshaw Union", "Smart Prepaid Auto Stand", "E-Rickshaw Feeder Service", "City Tuk-Tuk Transit"],
        "car_rentals": ["Zoomcar Self-Drive Rental", "Revv Self-Drive Car", "MyChoize Car Rental", "Avis India Car Hire"],
        "bike_rentals": ["Royal Enfield Mountain Motorcycle Hire", "Bounce City Scooter Rental", "City Bicycle & e-Bike Share", "Wheelstreet Bike Rental"],
        "transfers": ["Royal Heritage Chauffeur Sedan", "Executive AC Innova Crysta Transfer", "Premium Luxury Chauffeur Service"],
        "coastal_ferries": ["Coastal Catamaran Ferry", "State Inland Waterways Ferry", "Harbour Passenger Boat", "Scenic Lagoon Cruise Shuttle"],
        "mountain_transit": ["Himalayan Scenic Ropeway", "Mountain Funicular & Cable Car", "4x4 Hill Station Jeep Shuttle", "Alpine Toy Train Heritage Railway"],
    },
    "Europe": {
        "airlines": ["Lufthansa", "British Airways", "Air France", "EasyJet", "Ryanair", "KLM Royal Dutch", "Swiss International", "Iberia", "ITA Airways"],
        "railways": ["SNCF TGV INOUI", "Deutsche Bahn ICE", "Eurostar High-Speed Rail", "Trenitalia Frecciarossa", "Renfe AVE", "ÖBB Nightjet", "SBB Swiss Federal Rail"],
        "bus_operators": ["FlixBus Europe Express", "RegioJet Coach", "National Express", "BlaBlaCar Bus", "Eurolines Intercity"],
        "local_transit": ["City Underground Metro", "City Light Rail & Tramway", "Municipal Electric City Bus", "S-Bahn Suburban Express Rail"],
        "taxi_services": ["Official City Metered Taxi", "Radio Taxi Cooperative", "Airport Official Taxi Service", "City Centre Cab Rank"],
        "ride_hailing": ["Uber Green Europe", "Bolt Ride-Hailing", "FreeNow Taxi & Cab", "Uber Black Executive"],
        "car_rentals": ["Sixt Rent a Car", "Europcar Mobility", "Hertz Europe Car Hire", "Avis Car Rental", "Enterprise Rent-A-Car"],
        "bike_rentals": ["City e-Bike & Bicycle Share", "Nextbike Public Bike Share", "Donkey Republic Bike Hire", "Lime e-Scooter & e-Bike"],
        "transfers": ["VIP Executive Mercedes Chauffeur", "Blacklane Luxury Chauffeur Transfer", "Grand Tour Private Sedan"],
        "coastal_ferries": ["High-Speed Passenger Hydrofoil", "Inter-Island Ferry Line", "Coastal Catamaran Express", "Historic Canal Water Bus"],
        "mountain_transit": ["Alpine Panoramic Cable Car", "Glacier Express Scenic Funicular", "Mountain Aerial Tramway", "Alpine Rack & Pinion Railway"],
    },
    "North_America": {
        "airlines": ["Delta Air Lines", "United Airlines", "American Airlines", "Southwest Airlines", "Air Canada", "JetBlue Airways", "Alaska Airlines"],
        "railways": ["Amtrak Acela High-Speed", "Amtrak Northeast Regional", "Amtrak Coast Starlight", "VIA Rail Canada", "Brightline Florida High-Speed"],
        "bus_operators": ["Greyhound Lines", "Megabus Express", "FlixBus North America", "RedCoach Luxury Coach", "Coach USA Airport Express"],
        "local_transit": ["MTA Subway / Metro Transit", "City Light Rail Express", "Metropolitan Transit Bus (MTA / CTA)", "Regional Commuter Rail"],
        "taxi_services": ["Official City Medallion Taxi", "Airport Authorized Yellow Cab", "Metro City Taxi Service", "Checker Cab Company"],
        "ride_hailing": ["UberX Ride-Hailing", "Lyft Standard & XL", "Uber Comfort", "Lyft Black Luxury"],
        "car_rentals": ["Enterprise Rent-A-Car", "Hertz Car Rental", "Avis Rent A Car", "National Car Rental", "Alamo Rent A Car"],
        "bike_rentals": ["Citi Bike / Divvy Bike Share", "Lime e-Bike & Scooter Share", "Bird Electric Scooter Fleet", "City Cycle Share"],
        "transfers": ["Carmel Luxury Chauffeur SUV", "Empire Luxury Sedan & Limousine", "Executive Suburban Black Car"],
        "coastal_ferries": ["State Passenger Ferry System", "Harbour Water Taxi Express", "Scenic Island Catamaran", "Bay Area Fast Ferry"],
        "mountain_transit": ["Rocky Mountain Aerial Tramway", "Alpine Scenic Gondola Lift", "4x4 Mountain Explorer Shuttle", "Scenic Mountain Railway"],
    },
    "East_Asia": {
        "airlines": ["ANA All Nippon Airways", "Japan Airlines (JAL)", "Korean Air", "Asiana Airlines", "China Eastern", "Cathay Pacific", "EVA Air"],
        "railways": ["JR Shinkansen Bullet Train", "KTX Korea High-Speed Rail", "China High-Speed Railway (CRH)", "Taiwan High Speed Rail (THSR)", "Odakyu Limited Express"],
        "bus_operators": ["WILLER EXPRESS Highway Bus", "Keio Highway Bus", "Airport Limousine Bus", "Kumho Express Bus", "Trans-Island Express Coach"],
        "local_transit": ["Tokyo / Seoul Subway Metro", "City Monorail Express", "Municipal Transit Electric Bus", "Automated Light Transit (AGT)"],
        "taxi_services": ["Nihon Kotsu Metered Taxi", "Kakao T Official Taxi", "MK Taxi Luxury Service", "City Green Metered Cab"],
        "ride_hailing": ["Uber East Asia", "Kakao Taxi Black", "DiDi Express", "Grab Asia"],
        "car_rentals": ["Times CAR RENTAL", "Toyota Rent a Car", "Nippon Rent-A-Car", "Lotte Rent-a-Car Korea"],
        "bike_rentals": ["Docomo / T-Bike Share", "Seoul Ttareungyi Public Bike", "YouBike City Share", "HelloCycling Japan"],
        "transfers": ["Imperial Chauffeur Toyota Alphard", "VIP Luxury Executive Sedan", "Grand Hospitality Airport Chauffeur"],
        "coastal_ferries": ["Tokyo Water Bus Cruise", "JR Miyajima Passenger Ferry", "High-Speed Hydrofoil Ferry", "Harbour Island Jetfoil"],
        "mountain_transit": ["Hakone Ropeway Gondola Lift", "Mount Fuji Scenic Cable Car", "Namsan Cable Car Seoul", "Alpine Panoramic Ropeway"],
    },
    "Southeast_Asia": {
        "airlines": ["Singapore Airlines", "Thai Airways", "AirAsia", "Garuda Indonesia", "Vietnam Airlines", "Scoot", "Malaysia Airlines", "Cebu Pacific"],
        "railways": ["KTM ETS High-Speed Rail", "State Railway of Thailand Express", "Vietnam Railways North-South Reunification Express", "Whoosh Indonesia High Speed Rail"],
        "bus_operators": ["Aeroline Luxury Coach", "Sombat Tour VIP Bus", "Futa Bus Lines Vietnam", "TransNasional Intercity", "Giant Ibis Transport"],
        "local_transit": ["Mass Rapid Transit (MRT / BTS)", "City Rapid Monorail", "Public AC Transit Bus Fleet", "TransJakarta Bus Rapid Transit"],
        "taxi_services": ["ComfortDelGro Metered Taxi", "Bluebird Taxi Indonesia", "Mai Linh Taxi Vietnam", "City Metered Cab Guild"],
        "ride_hailing": ["GrabCar Express", "Gojek Ride-Hailing", "Maxim Southeast Asia", "GrabCar Premium"],
        "auto_services": ["Heritage Motorized Tuk-Tuk", "Traditional Songthaew Shuttle", "Jeepney Urban Transit", "Bajaj City Trike"],
        "car_rentals": ["Avis Southeast Asia", "Hertz Asia Car Hire", "Drive.SG Rental", "Local Self-Drive Car Hire"],
        "bike_rentals": ["Scooter / Moped Daily Rental", "City Bicycle Rental & Tour", "e-Scooter Urban Share", "Honda Wave Motorcycle Hire"],
        "transfers": ["VIP Private Chauffeur Luxury Van", "Luxury Airport Sedan Transfer", "Private Island / Beach Resort Chauffeur"],
        "coastal_ferries": ["Speedboat Island Express", "High-Speed Passenger Catamaran", "Traditional Longtail Boat Shuttle", "Inter-Island Ro-Ro Ferry"],
        "mountain_transit": ["Awana SkyWay Cable Car", "Ba Na Hills Sun World Cable Car", "Scenic Hill Station Funicular", "4x4 Highland Safari Jeep"],
    },
    "Middle_East": {
        "airlines": ["Emirates", "Qatar Airways", "Etihad Airways", "Flydubai", "Saudia", "Turkish Airlines", "Gulf Air", "EgyptAir", "Royal Jordanian"],
        "railways": ["Haramain High-Speed Rail", "Etihad Rail Network", "Turkish State Railways (TCDD) High-Speed", "Israel Railways Express"],
        "bus_operators": ["RTA Intercity Express Bus", "SAPTCO VIP Intercity Coach", "Kamil Koç Express Coach", "Metro Istanbul Bus Line"],
        "local_transit": ["City Underground Metro", "Modern City Tramway", "Public RTA City Bus Fleet", "Automated People Mover"],
        "taxi_services": ["Dubai Taxi Corporation (Hala)", "Careem Metered Taxi", "Airport Official Yellow Cab", "Turquoise City Taxi"],
        "ride_hailing": ["Careem Chauffeur", "Uber Middle East", "Bolt Ride-Hailing", "Uber Black VIP"],
        "auto_services": ["Traditional Tuk-Tuk Feeder", "City Rickshaw Transit", "Historic Tourist Carriage", "Old Quarter Trike"],
        "car_rentals": ["Budget Rent a Car", "Hertz Middle East", "Sixt Luxury Car Hire", "Thrifty Car Rental"],
        "bike_rentals": ["Careem BIKE Urban Share", "City Promenade Bicycle Rental", "e-Scooter App Hire", "Cycling Track Bike Hire"],
        "transfers": ["VIP Luxury Mercedes-Maybach Chauffeur", "GMC Yukon Luxury SUV Transfer", "Executive Airport Chauffeur Drive"],
        "coastal_ferries": ["Traditional Wooden Abra Boat", "Dubai Ferry Marine Transport", "Bosphorus Passenger Ferry", "Red Sea Express Catamaran"],
        "mountain_transit": ["Taif Scenic Teleférico Cable Car", "Olympos Teleferik Cable Car", "Jabal Sawda Mountain Cableway", "Desert 4x4 Dune Chauffeur"],
    },
    "Latin_America": {
        "airlines": ["LATAM Airlines", "Avianca", "Aeroméxico", "Copa Airlines", "Gol Transportes Aéreos", "Azul Brazilian Airlines", "Sky Airline"],
        "railways": ["Inca Rail / PeruRail Scenic Train", "Tren Maya Express", "Metrotren Nos Chile", "Tren a las Nubes High Altitude Rail"],
        "bus_operators": ["ADO Primera Clase Bus", "Cruz del Sur Luxury Coach", "Pluma Internacional", "Andesmar Bus Cama", "Pullman Bus Chile"],
        "local_transit": ["Metrô / Subway Transit System", "Metrobús Rapid Transit (BRT)", "City Electric Trolleybus", "TransMilenio Express"],
        "taxi_services": ["Radio Taxi Seguro", "Sitio Authorized Taxi", "Airport Official Prepaid Taxi", "City Yellow & White Cab"],
        "ride_hailing": ["Uber Latin America", "Cabify Executive", "Didi Express LatAm", "99 App Taxi"],
        "auto_services": ["Mototaxi Urban Transit", "Tuk-Tuk Local Feeder", "Colectivo Shared Minibus", "Combi Urban Transit"],
        "car_rentals": ["Localiza Rent a Car", "Hertz Latin America", "Avis Car Rental", "Movida Rent a Car"],
        "bike_rentals": ["Ecobici / Bike Santiago Share", "Tembici City Bike Share", "Mountain Bike Adventure Rental", "Beachfront Cruiser Hire"],
        "transfers": ["Executive Armored Chauffeur SUV", "Private Heritage Van Transfer", "Luxury Airport Sedan Chauffeur"],
        "coastal_ferries": ["Passenger Catamaran to Islands", "Coastal Water Taxi Boat", "Amazon River Passenger Ferry", "Lake Titicaca Motorboat Shuttle"],
        "mountain_transit": ["Mi Teleférico Cable Car System", "Metrocable Medellin", "Sugarloaf Mountain Cable Car (Bondinho)", "Andes Funicular Railway"],
    },
    "Africa": {
        "airlines": ["South African Airways", "Ethiopian Airlines", "Kenya Airways", "Royal Air Maroc", "FlySafair", "Airlink", "EgyptAir"],
        "railways": ["Gautrain High-Speed Commuter Rail", "Madaraka Express SGR Kenya", "ONCF Al Boraq High Speed Rail Morocco", "Rovos Rail Heritage Express"],
        "bus_operators": ["Intercape Mainliner Bus", "Easy Coach Kenya", "CTM Morocco Express", "Greyhound South Africa", "Modern Coast Express"],
        "local_transit": ["MyCiTi / Gautrain Feeder Bus", "Rea Vaya Bus Rapid Transit", "Casablanca Tramway", "Nairobi Commuter Rail"],
        "taxi_services": ["Authorized Metered City Taxi", "Prepaid Airport Cab Service", "Minibus Taxi (Matatu / Danfo)", "City Petit Taxi"],
        "ride_hailing": ["Uber Africa", "Bolt Ride-Hailing", "Little Cab Kenya", "Yango Ride Service"],
        "auto_services": ["Tuk-Tuk / Keke Napep Trike", "Boda-Boda Motorcycle Taxi", "City Motorized Rickshaw", "Bajaj Auto Transit"],
        "car_rentals": ["Avis South Africa", "Europcar Africa", "Hertz Southern Africa", "First Car Rental"],
        "bike_rentals": ["City Beachfront Bike Hire", "Safari Mountain Bike Rental", "Urban Cycle Share", "e-Bike Coastal Explorer"],
        "transfers": ["Private Safari 4x4 Land Cruiser Chauffeur", "Luxury Mercedes VIP Transfer", "Garden Route Private Touring Sedan"],
        "coastal_ferries": ["Zanzibar High-Speed Passenger Catamaran", "Robben Island Passenger Ferry", "Coastal Dhow Sailing Boat", "River Lagoon Shuttle"],
        "mountain_transit": ["Table Mountain Aerial Cableway", "Atlas Mountain Scenic Cable Car", "Rift Valley 4x4 Mountain Jeep", "Highlands Safari Rover"],
    },
    "Oceania": {
        "airlines": ["Qantas Airways", "Air New Zealand", "Virgin Australia", "Jetstar Airways", "Fiji Airways", "Rex Regional Express"],
        "railways": ["NSW TrainLink Intercity Rail", "V/Line Victoria Regional Rail", "TranzAlpine Scenic Railway NZ", "Queensland Rail Coastal Express", "Northern Explorer Train"],
        "bus_operators": ["Premier Motor Service Coach", "InterCity New Zealand Coach", "Firefly Express Coach", "Murrays Coaches Australia"],
        "local_transit": ["Sydney Trains / Metro Network", "Melbourne Iconic Tram Network", "Auckland AT Metro Train & Bus", "Brisbane Translink Busway & Rail"],
        "taxi_services": ["13CABS Australia", "Silver Top Taxis Melbourne", "Green Cabs New Zealand", "Airport Official Taxi Rank"],
        "ride_hailing": ["Uber Oceania", "Didi Australia", "Ola Australia", "Uber Premier Black"],
        "car_rentals": ["Hertz Australia & NZ", "Avis Car Rental", "Thrifty Car & Van Rental", "Europcar Oceania", "Apex Car Rentals"],
        "bike_rentals": ["Beam e-Bike & e-Scooter Share", "Neuron Mobility e-Scooters", "City Promenade Cycle Hire", "Mountain Trail Bike Rental"],
        "transfers": ["Harbour Luxury Chauffeur Mercedes", "Private Wine Country Touring Sedan", "Luxury Outback 4WD Chauffeur"],
        "coastal_ferries": ["Sydney Ferries (Manly & Taronga)", "Fullers360 Auckland Island Ferry", "Interislander Cook Strait Ferry", "Great Barrier Reef Fast Catamaran"],
        "mountain_transit": ["Skyline Queenstown Gondola", "Scenic World Blue Mountains Cableway", "Southern Alps Ski Resort Gondola", "Mount Kosciuszko Chairlift & Shuttle"],
    },
}


def get_destination_region(country: str, city: str) -> str:
    """Classifies a destination into a geographic region."""
    c = country.strip().lower()
    if c == "india":
        return "India"
    
    europe_countries = {
        "france", "united kingdom", "italy", "germany", "spain", "switzerland", "austria",
        "netherlands", "belgium", "portugal", "greece", "czech republic", "czechia", "hungary",
        "poland", "sweden", "norway", "denmark", "finland", "ireland", "croatia", "iceland",
        "scotland", "monaco", "vatican city", "san marino", "malta", "cyprus", "romania", "bulgaria"
    }
    if c in europe_countries:
        return "Europe"

    na_countries = {"united states", "usa", "canada", "mexico", "puerto rico", "cuba", "bahamas", "jamaica", "dominican republic", "costa rica", "panama"}
    if c in na_countries:
        return "North_America"

    east_asia_countries = {"japan", "south korea", "korea", "china", "taiwan", "hong kong", "macau", "mongolia"}
    if c in east_asia_countries:
        return "East_Asia"

    se_asia_countries = {"thailand", "singapore", "malaysia", "indonesia", "vietnam", "philippines", "cambodia", "laos", "myanmar"}
    if c in se_asia_countries:
        return "Southeast_Asia"

    me_countries = {"united arab emirates", "uae", "saudi arabia", "qatar", "egypt", "turkey", "jordan", "oman", "kuwait", "bahrain", "israel", "morocco"}
    if c in me_countries:
        return "Middle_East"

    latam_countries = {"brazil", "argentina", "peru", "chile", "colombia", "ecuador", "bolivia", "uruguay", "paraguay", "guatemala"}
    if c in latam_countries:
        return "Latin_America"

    africa_countries = {"south africa", "kenya", "tanzania", "ethiopia", "rwanda", "zimbabwe", "botswana", "namibia", "mauritius", "seychelles", "uganda", "ghana", "nigeria"}
    if c in africa_countries:
        return "Africa"

    oceania_countries = {"australia", "new zealand", "fiji", "french polynesia", "samoa", "papua new guinea"}
    if c in oceania_countries:
        return "Oceania"

    return "Europe"  # Default fallback


def detect_environmental_features(city: str, country: str, description: str) -> Dict[str, bool]:
    """Detects coastal, island, mountain, alpine, and metro features from destination attributes."""
    text_corpus = f"{city} {country} {description}".lower()
    
    coastal_keywords = [
        "beach", "coast", "coastal", "island", "sea", "ocean", "bay", "harbour", "harbor",
        "port", "lake", "lagoon", "waterfront", "backwaters", "marina", "reef", "gulf",
        "canal", "ferry", "snorkeling", "scuba", "yacht", "palawan", "bali", "phuket",
        "goa", "kochi", "venice", "santorini", "mykonos", "maldives", "mauritius", "fiji",
        "amalfi", "capri", "dubrovnik", "cancun", "honolulu", "sydney", "nice", "ibiza"
    ]
    
    mountain_keywords = [
        "mountain", "himalaya", "himalayan", "alps", "alpine", "hill", "peak", "valley",
        "trek", "trekking", "ski", "skiing", "snow", "altitude", "pass", "elevation",
        "cordillera", "andes", "rockies", "glacier", "manali", "shimla", "leh", "gulmarg",
        "pahalgam", "munnar", "ooty", "coorg", "zermatt", "interlaken", "grindelwald",
        "banff", "aspen", "cusco", "queenstown", "innsbruck", "salzburg", "hallstatt", "darjeeling"
    ]
    
    metro_keywords = [
        "capital", "metropolis", "financial", "skyscrapers", "skyline", "cosmopolitan",
        "subway", "metro", "bustling", "technology hub", "megacity", "urban", "commercial"
    ]

    is_coastal = any(kw in text_corpus for kw in coastal_keywords)
    is_mountain = any(kw in text_corpus for kw in mountain_keywords)
    is_metro = any(kw in text_corpus for kw in metro_keywords)

    return {
        "is_coastal": is_coastal,
        "is_mountain": is_mountain,
        "is_metro": is_metro,
    }


def generate_transport_catalog_for_destinations(
    destinations: List[Tuple[int, str, str, Optional[float]]]
) -> Dict[Tuple[str, str], List[Tuple[str, str, str, float, int]]]:
    """
    Generates a deterministic catalog of exactly 12 transport options for every destination.
    Preserves existing baseline records.
    Returns: Dict[(city, country), List[(origin, mode, provider, estimated_cost, duration_minutes)]]
    """
    catalog: Dict[Tuple[str, str], List[Tuple[str, str, str, float, int]]] = {}

    for dest_id, city, country, avg_daily_cost in destinations:
        dest_key = (city, country)
        
        # If curated destination exists, load curated list and ensure exactly 12
        if dest_key in CURATED_LANDMARK_TRANSPORTS:
            curated_list = list(CURATED_LANDMARK_TRANSPORTS[dest_key])
            if len(curated_list) == 12:
                catalog[dest_key] = curated_list
                continue
            elif len(curated_list) > 12:
                catalog[dest_key] = curated_list[:12]
                continue
            # If fewer than 12, start with curated and supplement below
            transport_list = list(curated_list)
        else:
            transport_list = []

        # Deterministic RNG seeding based on destination attributes
        seed_str = f"roamgenie_transport_{dest_id}_{city}_{country}_{RANDOM_SEED}"
        seed_hash = int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(seed_hash)

        region = get_destination_region(country, city)
        operators = REGIONAL_OPERATORS.get(region, REGIONAL_OPERATORS["Europe"])
        origin_hubs = REGIONAL_ORIGIN_HUBS.get(region, REGIONAL_ORIGIN_HUBS["Europe"])
        
        features = detect_environmental_features(city, country, "")
        is_coastal = features["is_coastal"]
        is_mountain = features["is_mountain"]
        is_metro = features["is_metro"]

        cost_benchmark = avg_daily_cost if avg_daily_cost and avg_daily_cost > 0 else 4500.0
        # Cost multiplier scale
        mult = cost_benchmark / 4500.0
        if mult < 0.6:
            mult = 0.6
        elif mult > 3.0:
            mult = 3.0

        # Filter origin hubs so origin is not the same as city
        candidate_origins = [h for h in origin_hubs if h.lower() != city.lower()]
        if not candidate_origins:
            candidate_origins = ["Regional Gateway", "International Hub", "Capital City"]

        # Track existing entries to avoid duplicates in (origin, mode, provider)
        seen_triplets = {(t[0].lower(), t[1].lower(), t[2].lower()) for t in transport_list}

        def add_transport_option(origin: str, mode: str, provider: str, cost: float, duration: int) -> bool:
            triplet = (origin.strip().lower(), mode.strip().lower(), provider.strip().lower())
            if triplet in seen_triplets:
                return False
            seen_triplets.add(triplet)
            # Round cost to clean 10s or 50s
            clean_cost = round(cost / 10.0) * 10.0
            if clean_cost < 20.0:
                clean_cost = 20.0
            transport_list.append((origin.strip(), mode.strip(), provider.strip(), clean_cost, int(duration)))
            return True

        # Generate standard 12 slots if needed:
        # Slot 1: Intercity Flight from Hub 1
        origin_1 = candidate_origins[0 % len(candidate_origins)]
        airline_1 = operators["airlines"][rng.randint(0, len(operators["airlines"]) - 1)]
        flight_cost = 3200.0 * mult * (0.85 + 0.3 * rng.random())
        flight_dur = rng.randint(55, 120)
        add_transport_option(origin_1, "flight", f"{airline_1} Direct Flight", flight_cost, flight_dur)

        # Slot 2: High-Speed / Express Rail from Hub 2
        origin_2 = candidate_origins[1 % len(candidate_origins)]
        rail_1 = operators["railways"][rng.randint(0, len(operators["railways"]) - 1)]
        rail_cost = 850.0 * mult * (0.8 + 0.35 * rng.random())
        rail_dur = rng.randint(150, 420)
        add_transport_option(origin_2, "train", f"{rail_1} ({origin_2} - {city})", rail_cost, rail_dur)

        # Slot 3: Intercity Bus / Coach from Hub 3
        origin_3 = candidate_origins[2 % len(candidate_origins)]
        bus_1 = operators["bus_operators"][rng.randint(0, len(operators["bus_operators"]) - 1)]
        bus_cost = 450.0 * mult * (0.8 + 0.3 * rng.random())
        bus_dur = rng.randint(210, 540)
        add_transport_option(origin_3, "bus", f"{bus_1} Intercity Service", bus_cost, bus_dur)

        # Slot 4: Local Public Transit (Metro / Light Rail / City Bus)
        local_mode = "metro" if (is_metro or region in ("East_Asia", "Europe")) else "bus"
        local_op = operators["local_transit"][rng.randint(0, len(operators["local_transit"]) - 1)]
        local_cost = max(30.0, 50.0 * mult * (0.7 + 0.4 * rng.random()))
        local_dur = rng.randint(20, 40)
        add_transport_option(city, local_mode, f"{city} {local_op}", local_cost, local_dur)

        # Slot 5: Local Metered Taxi / Cab
        taxi_op = operators["taxi_services"][rng.randint(0, len(operators["taxi_services"]) - 1)]
        taxi_cost = 550.0 * mult * (0.85 + 0.3 * rng.random())
        taxi_dur = rng.randint(20, 45)
        add_transport_option(city, "taxi", f"{city} {taxi_op}", taxi_cost, taxi_dur)

        # Slot 6: Ride-Hailing App
        ride_op = operators["ride_hailing"][rng.randint(0, len(operators["ride_hailing"]) - 1)]
        ride_cost = 480.0 * mult * (0.85 + 0.3 * rng.random())
        ride_dur = rng.randint(15, 35)
        add_transport_option(city, "ride-hailing", f"{ride_op} {city}", ride_cost, ride_dur)

        # Slot 7: Destination-specific authentic / geographic transit
        if is_coastal:
            ferry_op = operators.get("coastal_ferries", ["Coastal Passenger Ferry"])[rng.randint(0, len(operators.get("coastal_ferries", [])) - 1)]
            ferry_cost = 250.0 * mult * (0.8 + 0.4 * rng.random())
            ferry_dur = rng.randint(20, 60)
            add_transport_option(city, "ferry", f"{city} {ferry_op}", ferry_cost, ferry_dur)
        elif is_mountain:
            mount_op = operators.get("mountain_transit", ["Alpine Cable Car"])[rng.randint(0, len(operators.get("mountain_transit", [])) - 1)]
            mount_cost = 450.0 * mult * (0.85 + 0.4 * rng.random())
            mount_dur = rng.randint(15, 45)
            mount_mode = "cable-car" if "Cable" in mount_op or "Ropeway" in mount_op or "Gondola" in mount_op or "Funicular" in mount_op else "shuttle"
            add_transport_option(city, mount_mode, f"{city} {mount_op}", mount_cost, mount_dur)
        elif region in ("India", "Southeast_Asia", "Middle_East", "Africa", "Latin_America"):
            auto_op = operators.get("auto_services", ["City Auto-Rickshaw Union"])[rng.randint(0, len(operators.get("auto_services", [])) - 1)]
            auto_cost = max(40.0, 120.0 * mult * (0.75 + 0.35 * rng.random()))
            auto_dur = rng.randint(15, 30)
            auto_mode = "auto-rickshaw" if region in ("India", "Southeast_Asia") else "shuttle"
            add_transport_option(city, auto_mode, f"{city} {auto_op}", auto_cost, auto_dur)
        else:
            tram_cost = 180.0 * mult * (0.8 + 0.3 * rng.random())
            tram_dur = rng.randint(20, 35)
            add_transport_option(city, "tram", f"{city} Heritage & City Center Tramway", tram_cost, tram_dur)

        # Slot 8: Self-Drive Car Rental
        rental_op = operators["car_rentals"][rng.randint(0, len(operators["car_rentals"]) - 1)]
        rental_cost = 2200.0 * mult * (0.85 + 0.3 * rng.random())
        rental_dur = 720  # Daily rental (12 hours)
        add_transport_option(city, "car-rental", f"{rental_op} (Daily Hire)", rental_cost, rental_dur)

        # Slot 9: Active Mobility / Bike / Scooter Rental
        bike_op = operators["bike_rentals"][rng.randint(0, len(operators["bike_rentals"]) - 1)]
        bike_cost = 280.0 * mult * (0.8 + 0.3 * rng.random())
        bike_dur = rng.randint(120, 480)
        bike_mode = "bike-rental"
        add_transport_option(city, bike_mode, f"{city} {bike_op}", bike_cost, bike_dur)

        # Slot 10: Private Chauffeur / Luxury Transfer
        trans_op = operators["transfers"][rng.randint(0, len(operators["transfers"]) - 1)]
        trans_cost = 4500.0 * mult * (0.9 + 0.35 * rng.random())
        trans_dur = rng.randint(180, 480)
        add_transport_option(city, "private-transfer", f"{trans_op} in {city}", trans_cost, trans_dur)

        # Slot 11: Airport Express / Regional Shuttle Link
        airport_origin = f"{city} Airport Terminal"
        shuttle_cost = 350.0 * mult * (0.8 + 0.3 * rng.random())
        shuttle_dur = rng.randint(30, 65)
        add_transport_option(airport_origin, "shuttle", f"{city} Official Express Airport Shuttle", shuttle_cost, shuttle_dur)

        # Slot 12: Secondary Intercity Connection (Train or Flight or Regional Express)
        origin_4 = candidate_origins[3 % len(candidate_origins)]
        if rng.random() > 0.5:
            sec_rail = operators["railways"][(rng.randint(0, len(operators["railways"]) - 1) + 1) % len(operators["railways"])]
            sec_cost = 780.0 * mult * (0.8 + 0.3 * rng.random())
            sec_dur = rng.randint(180, 500)
            add_transport_option(origin_4, "train", f"{sec_rail} ({origin_4} - {city})", sec_cost, sec_dur)
        else:
            sec_air = operators["airlines"][(rng.randint(0, len(operators["airlines"]) - 1) + 1) % len(operators["airlines"])]
            sec_cost = 3600.0 * mult * (0.85 + 0.3 * rng.random())
            sec_dur = rng.randint(60, 110)
            add_transport_option(origin_4, "flight", f"{sec_air} Express Flight", sec_cost, sec_dur)

        # Safety: Ensure exactly 12 options
        extra_idx = 0
        while len(transport_list) < 12:
            extra_idx += 1
            hub = candidate_origins[(extra_idx + 4) % len(candidate_origins)]
            add_transport_option(
                hub,
                "bus",
                f"Regional Express Bus Line {extra_idx} to {city}",
                round(350.0 * mult * (0.8 + 0.1 * extra_idx), -1),
                180 + 30 * extra_idx,
            )

        catalog[dest_key] = transport_list[:12]

    return catalog
