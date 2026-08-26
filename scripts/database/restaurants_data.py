"""Master Restaurant Dataset Generator (Phase D4)
Provides a rich, deterministic, geographically authentic catalog of 6,000 restaurants across all 500 destinations.
"""
import hashlib
import random
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

RANDOM_SEED = 20260820

# Known landmark and authentic restaurants for prominent destinations across regions
CURATED_LANDMARK_RESTAURANTS: Dict[Tuple[str, str], List[Tuple[str, str, float, float]]] = {
    ("Mysuru", "India"): [
        ("Mylari Tiffin House", "South Indian", 250.0, 4.8),               # Preserved ID 1
        ("Gufha Cave Dining", "North Indian & Mughlai", 650.0, 4.3),      # Preserved ID 2
        ("Oyster Bay Fine Dining", "Seafood & Coastal", 1400.0, 4.6),
        ("The Tiger Trail - Royal Orchid", "Mughlai & North Indian", 1800.0, 4.7),
        ("Spring at Radisson Blu", "Multi-Cuisine & Buffet", 1600.0, 4.6),
        ("Hotel RRR Restaurant", "Andhra & South Indian", 450.0, 4.7),
        ("Depth 'n Green Artisan Cafe", "Healthy & Continental", 550.0, 4.6),
        ("Om Shanthi Pure Veg", "South Indian Pure Veg", 300.0, 4.4),
        ("Mahesh Prasad Tiffin Room", "Traditional South Indian", 200.0, 4.5),
        ("Malgudi Cafe", "Bakery & Artisan Coffee", 400.0, 4.4),
        ("Vinayaka Mylari Nazarbad", "Heritage Dosas & Tiffin", 180.0, 4.8),
        ("Infinit Sky Rooftop Lounge", "Continental & Pan-Asian", 1500.0, 4.5),
    ],
    ("Kochi", "India"): [
        ("The Rice Boat - Taj Malabar", "Kerala Seafood Fine Dining", 3200.0, 4.9),
        ("Seagull Fort Kochi", "Seafood & Kerala", 850.0, 4.5),
        ("Kashi Art Cafe", "Continental & Bakery", 550.0, 4.7),
        ("History & Terrace Restaurant", "Traditional Kerala Heritage", 2200.0, 4.8),
        ("Dal Roti Fort Kochi", "North Indian & Kathi Rolls", 400.0, 4.6),
        ("Paragon Restaurant Kochi", "Malabar Seafood & Biryani", 650.0, 4.8),
        ("Fusion Bay", "Kerala Seafood & Fusion", 750.0, 4.6),
        ("David Hall Gallery & Cafe", "European Bakery & Pizzas", 600.0, 4.5),
        ("Grand Pavilion Kochi", "Syrian Christian & Kerala", 700.0, 4.5),
        ("Kayees Rahmathulla Hotel", "Iconic Kayees Mutton Biryani", 350.0, 4.7),
        ("Qissa Cafe Fort Kochi", "Artisan Bakery & Coffee", 450.0, 4.5),
        ("Fort House Restaurant", "Waterfront Kerala Seafood", 1200.0, 4.6),
    ],
    ("Jaipur", "India"): [
        ("Suvarna Mahal - Rambagh Palace", "Royal Indian Fine Dining", 6500.0, 4.9),
        ("1135 AD Amer Fort", "Royal Rajasthani Heritage", 3500.0, 4.8),
        ("Laxmi Mishthan Bhandar (LMB)", "Rajasthani Thali & Sweets", 650.0, 4.7),
        ("Handi Restaurant MI Road", "Mughlai & Laal Maas", 950.0, 4.6),
        ("Niros Restaurant", "Mughlai & Continental", 1100.0, 4.5),
        ("Peacock Rooftop Restaurant", "North Indian & Global", 750.0, 4.6),
        ("Baradari Restaurant City Palace", "Contemporary Rajasthani", 2400.0, 4.7),
        ("Rawat Mishthan Bhandar", "Pyaaz Kachori & Street Food", 180.0, 4.8),
        ("Tapri The Tea House Central Park", "Chaat & Gourmet Chai", 450.0, 4.7),
        ("RJ 14 Traditional Dining", "North Indian Pure Veg", 600.0, 4.4),
        ("Spice Court Civil Lines", "Authentic Junglee Maas & Thali", 1200.0, 4.6),
        ("Gulab Ji Chai Wale", "Historic Jaipur Tea & Bun Maska", 120.0, 4.7),
    ],
    ("Udaipur", "India"): [
        ("Sheesh Mahal - The Leela Palace", "Royal Indian Fine Dining", 7500.0, 5.0),
        ("Ambrai Waterfront Restaurant", "Rajasthani & Continental", 1800.0, 4.8),
        ("Upre by 1959 Rooftop", "Rajasthani & Multi-Cuisine", 1600.0, 4.7),
        ("Tribute Restaurant Fatehsagar", "North Indian & Mughlai", 1200.0, 4.6),
        ("Jagat Niwas Rooftop Restaurant", "Mughlai & Mewari", 1400.0, 4.6),
        ("Millets of Mewar", "Healthy Organic & Vegan", 650.0, 4.7),
        ("Natraj Dining Hall & Restaurant", "Unlimited Rajasthani Thali", 350.0, 4.8),
        ("Edelweiss Tea & Bakery Cafe", "European Bakery & Coffee", 450.0, 4.5),
        ("Khamma Ghani Restaurant", "Lakeside North Indian & Bar", 1100.0, 4.6),
        ("Charcoal by Carlsson", "BBQ & Mexican-Indian Fusion", 950.0, 4.5),
        ("Jheel's Ginger Coffee Bar & Bakery", "Lakeside Coffee & Desserts", 400.0, 4.7),
        ("Sai Baba Nashta Centre Chetak", "Poha & Street Breakfast", 100.0, 4.6),
    ],
    ("Goa", "India"): [
        ("The Fisherman's Wharf", "Goan Seafood & Curries", 1400.0, 4.7),
        ("Mum's Kitchen Panaji", "Traditional Goan Saraswat & Catholic", 1200.0, 4.7),
        ("Gunpowder Assagao", "Peninsular Indian & Coastal", 1100.0, 4.8),
        ("Thalassa Greek Taverna Siolim", "Greek & Mediterranean Waterfront", 2200.0, 4.7),
        ("Martin's Corner Betalbatim", "Goan Seafood & Balchão", 1300.0, 4.6),
        ("Burger Factory Anjuna", "Gourmet Burgers & Shakes", 650.0, 4.7),
        ("Vinayak Family Restaurant Assagao", "Goan Fish Thali", 400.0, 4.8),
        ("Artjuna Garden Cafe Anjuna", "Mediterranean & Healthy Bakery", 650.0, 4.6),
        ("Ritz Classic Panaji", "Authentic Fish Curry Rice Thali", 450.0, 4.7),
        ("Pousada by the Beach Calangute", "Beachside Goan Cuisine", 1800.0, 4.6),
        ("Infantaria Bakery & Cafe Calangute", "Goan Bakery & Breakfast", 500.0, 4.5),
        ("Kokni Kanteen Panaji", "Traditional Goan Street & Thali", 350.0, 4.7),
    ],
    ("Paris", "France"): [
        ("Le Gabriel - La Réserve Paris", "French Haute Cuisine", 18500.0, 4.9),
        ("L'Ambroisie - Place des Vosges", "Classic French Fine Dining", 22000.0, 4.9),
        ("Bistrot Paul Bert", "Traditional Parisian Bistro", 4200.0, 4.7),
        ("Bouillon Chartier Montmartre", "Classic French Brasserie", 1800.0, 4.5),
        ("Septime Paris 11th", "Modern Creative French", 7500.0, 4.8),
        ("Le Comptoir du Relais Saint-Germain", "French Gastropub & Bistro", 3800.0, 4.6),
        ("Café de Flore Boulevard Saint-Germain", "Iconic Historic Parisian Cafe", 1800.0, 4.5),
        ("Les Deux Magots Saint-Germain", "Historic French Cafe & Bistro", 1950.0, 4.4),
        ("Du Pain et des Idées", "Artisan French Bakery & Viennoiserie", 650.0, 4.9),
        ("L'As du Fallafel Marais", "Middle Eastern Street Food", 850.0, 4.8),
        ("Chez Janou Provençal Bistro", "Southern French & Mousse au Chocolat", 2800.0, 4.6),
        ("Breizh Café Le Marais", "Breton Crêpes & Artisanal Cider", 1400.0, 4.7),
    ],
    ("Tokyo", "Japan"): [
        ("Sukiyabashi Jiro Ginza", "Edomae Sushi Masterclass", 32000.0, 4.9),
        ("Narisawa Minato", "Innovative Satoyama Cuisine", 26000.0, 4.9),
        ("Kagurazaka Ishikawa", "Traditional Kaiseki", 24000.0, 4.9),
        ("Rokurinsha Tokyo Station", "Rich Tonkotsu Tsukemen Ramen", 850.0, 4.7),
        ("Afuri Ramen Harajuku", "Yuzu Shio Ramen & Craft Beer", 950.0, 4.6),
        ("Tonkatsu Maisen Aoyama", "Heritage Kurobuta Tonkatsu", 1800.0, 4.7),
        ("Ichiran Ramen Shibuya", "Classic Tonkotsu Ramen Booths", 800.0, 4.6),
        ("Tendon Tenya Asakusa", "Crispy Tempura Rice Bowls", 650.0, 4.5),
        ("Gonpachi Nishi-Azabu", "Soba, Yakitori & Izakaya", 3500.0, 4.5),
        ("Torikizoku Shinjuku", "Charcoal Yakitori Skewers", 1200.0, 4.4),
        ("Tsukiji Outer Market Seafood Stalls", "Fresh Sashimi & Street Bites", 1400.0, 4.8),
        ("Harbs Lumine Shinjuku", "Japanese Mille Crêpes & Tea", 950.0, 4.6),
    ],
    ("London", "United Kingdom"): [
        ("Gordon Ramsay Restaurant Chelsea", "Modern French Fine Dining", 18500.0, 4.9),
        ("The Ledbury Notting Hill", "Contemporary British Gastronomy", 16500.0, 4.9),
        ("Dishoom Covent Garden", "Bombay Comfort Dining & Chai", 1800.0, 4.8),
        ("St. JOHN Smithfield", "Traditional British Nose-to-Tail", 3800.0, 4.7),
        ("The Wolseley Piccadilly", "European Grand Cafe & Breakfast", 2800.0, 4.6),
        ("Padella Borough Market", "Handmade Fresh Italian Pasta", 1400.0, 4.8),
        ("Hawksmoor Seven Dials", "British Steaks & Craft Cocktails", 5200.0, 4.7),
        ("Rules Restaurant Covent Garden", "Historic British Game & Pies", 4500.0, 4.6),
        ("Poppies Fish & Chips Spitalfields", "Classic British Fish & Chips", 1200.0, 4.5),
        ("Borough Market Food Stalls", "Artisan Global Street Food", 950.0, 4.8),
        ("Monmouth Coffee Company Covent Garden", "Specialty Coffee & Pastries", 450.0, 4.7),
        ("Bao Soho", "Taiwanese Steamed Buns & Small Plates", 1500.0, 4.6),
    ],
    ("New York City", "United States"): [
        ("Le Bernardin Midtown", "French Seafood Fine Dining", 24000.0, 4.9),
        ("Eleven Madison Park Flatiron", "Plant-based Fine Gastronomy", 28000.0, 4.8),
        ("Gramercy Tavern Flatiron", "American Farm-to-Table", 7500.0, 4.8),
        ("Katz's Delicatessen Lower East Side", "Legendary Pastrami & Rye", 2200.0, 4.7),
        ("Joe's Pizza Greenwich Village", "Classic New York Style Slices", 450.0, 4.8),
        ("Balthazar SoHo", "French Brasserie & Raw Bar", 4800.0, 4.6),
        ("Keens Steakhouse Midtown", "Historic Steaks & Mutton Chops", 8500.0, 4.7),
        ("Momofuku Noodle Bar East Village", "Pork Belly Buns & Ramen", 2400.0, 4.5),
        ("Russ & Daughters Lower East Side", "Appetizing Smoked Fish & Bagels", 1600.0, 4.8),
        ("Peter Luger Steak House Brooklyn", "Dry-Aged Porterhouse Steaks", 9500.0, 4.7),
        ("Levain Bakery Upper West Side", "Decadent Chocolate Chip Walnut Cookies", 550.0, 4.9),
        ("Shake Shack Madison Square Park", "Classic Smash Burgers & Concretes", 950.0, 4.5),
    ],
    ("Rome", "Italy"): [
        ("La Pergola - Rome Cavalieri", "Gourmet Italian Haute Cuisine", 26000.0, 4.9),
        ("Il Pagliaccio Centro Storico", "Creative Italian Fine Dining", 18500.0, 4.8),
        ("Roscioli Salumeria con Cucina", "Artisan Carbonara & Salumi", 3200.0, 4.8),
        ("Da Enzo al 29 Trastevere", "Classic Roman Carbonara & Cacio e Pepe", 1800.0, 4.7),
        ("Trattoria Da Cesare al Casaletto", "Roman Classics & Fritti", 2200.0, 4.8),
        ("Armando al Pantheon", "Historic Roman Trattoria", 2600.0, 4.7),
        ("Bonci Pizzarium Prati", "Gourmet Roman Pizza al Taglio", 850.0, 4.8),
        ("Forno Campo de' Fiori", "Fresh Roman Pizza Bianca & Focaccia", 450.0, 4.7),
        ("Giolitti Gelateria near Pantheon", "Historic Roman Artisan Gelato", 400.0, 4.8),
        ("Taverna dei Fori Imperiali", "Family Roman Cuisine & Pasta", 2400.0, 4.6),
        ("Sant'Eustachio Il Caffè", "Iconic Roman Espresso & Pastries", 350.0, 4.7),
        ("Trapizzino Trastevere", "Roman Street Food Pockets", 550.0, 4.7),
    ],
    ("Dubai", "United Arab Emirates"): [
        ("Atmosphere Burj Khalifa", "Fine Dining on 122nd Floor", 12500.0, 4.8),
        ("Ossiano Atlantis The Palm", "Underwater Seafood Fine Dining", 16000.0, 4.9),
        ("Zuma Dubai DIFC", "Contemporary Japanese Izakaya", 5800.0, 4.8),
        ("Al Nafoorah Jumeirah", "Traditional Lebanese & Levantine", 2600.0, 4.7),
        ("Pierchic Jumeirah Al Qasr", "Over-water Mediterranean Seafood", 6500.0, 4.8),
        ("Arabian Tea House Al Fahidi", "Traditional Emirati Breakfast & Grills", 1100.0, 4.7),
        ("Al Ustad Special Kabab Bur Dubai", "Heritage Iranian Kebabs", 650.0, 4.8),
        ("Ravi Restaurant Satwa", "Iconic Pakistani Street Dining & Karahi", 450.0, 4.7),
        ("Coya Dubai Restaurant Village", "Contemporary Peruvian & Ceviche", 4800.0, 4.7),
        ("Bu Qtair Seafood Shack Jumeirah", "Fresh Catch Fried Fish & Curry", 850.0, 4.6),
        ("Bait Al Mandi Al Barsha", "Traditional Yemeni Mandi & Rice", 750.0, 4.5),
        ("Comptoir 102 Jumeirah", "Organic Plant-based Cafe & Smoothies", 950.0, 4.5),
    ],
    ("Bangkok", "Thailand"): [
        ("Sühring Chong Nonsi", "Modern German Gastronomy", 14000.0, 4.9),
        ("Gaa Thong Lor", "Progressive Indian-Thai Cuisine", 12000.0, 4.8),
        ("Jay Fai Old Town", "Michelin Crab Omelettes & Drunken Noodles", 3500.0, 4.8),
        ("Thipsamai Pad Thai Pratu Phi", "Classic Charcoal Pad Thai", 350.0, 4.7),
        ("Supanniga Eating Room Riverside", "Traditional Eastern Thai Cuisine", 1200.0, 4.7),
        ("Somtum Der Silom", "Authentic Isan Papaya Salad & Grills", 550.0, 4.6),
        ("Raan Jay Fai Riverside", "Seafood Street Cuisine", 2200.0, 4.7),
        ("Nai Mong Hoi Thod Chinatown", "Crispy Oyster Omelettes", 300.0, 4.8),
        ("Roast Cafe Thonglor", "Artisan Brunch & Specialty Coffee", 850.0, 4.6),
        ("Wattana Panich Ekkamai", "Legendary 50-Year Beef Broth Noodles", 250.0, 4.8),
        ("Krua Apsorn Dinso Road", "Royal Thai Home Cooking", 650.0, 4.7),
        ("Mango Tango Siam Square", "Thai Mango Sticky Rice & Desserts", 300.0, 4.5),
    ],
}

# Regional restaurant naming profiles & cuisine templates
RESTAURANT_REGIONAL_PROFILES: Dict[str, Dict[str, Any]] = {
    "India_Heritage": {
        "cuisines": [
            "Royal Rajasthani", "Mughlai & North Indian", "Heritage Thali", "North Indian Pure Veg",
            "Continental & Bakery", "Kadhi & Dal Baati", "Chaat & Street Food", "Rajasthani & Tandoor",
            "Pan-Asian & Fusion", "Artisan Coffee & Cafe", "Multi-Cuisine", "Traditional Sweets"
        ],
        "fine_prefixes": ["The Royal", "Maharaja's", "Heritage", "Sheesh", "Darbar", "Imperial", "Haveli"],
        "fine_suffixes": ["Palace Dining", "Fine Dining Lounge", "Terrace Restaurant", "Grand Banquet", "Royal Kitchen"],
        "casual_prefixes": ["Rasoi", "Swad", "Handi", "Peshawri", "Zaika", "Bhojanalaya", "Flavours of"],
        "casual_suffixes": ["Dining Room", "Restaurant", "Thali House", "Kitchen & Bar", "Rasoi"],
        "cafe_prefixes": ["Tapri", "Heritage", "Chai &", "Malgudi", "The Bean", "Artisan", "Cloud"],
        "cafe_suffixes": ["Tea Lounge", "Bakery Cafe", "Bistro & Coffee", "Roastery", "Bakehouse"],
        "budget_prefixes": ["Shree", "Rawat", "Laxmi", "Old City", "Chaat", "Kachori", "Desi"],
        "budget_suffixes": ["Mishthan Bhandar", "Tiffin Centre", "Dhaba & Tandoor", "Snack Corner", "Nashta House"],
    },
    "India_Coastal": {
        "cuisines": [
            "Coastal Seafood", "Kerala Cuisine", "Goan Fish Curry", "South Indian Tiffin",
            "Continental & Seafood", "Syrian Christian", "Beachside Grills", "Mangalorean Ghee Roast",
            "Healthy Cafe & Bowls", "Chettinad Seafood", "Arabian Sands", "Bakery & Desserts"
        ],
        "fine_prefixes": ["The Rice Boat", "Fisherman's", "Bay View", "Lagoon", "Ocean Pearl", "Palm Grove"],
        "fine_suffixes": ["Waterfront Seafood", "Coastal Fine Dining", "Beach Grill & Bar", "Luxury Cove", "Pavilion"],
        "casual_prefixes": ["Seagull", "Paragon", "Coastline", "Fisherman's Wharf", "Curry Leaf", "Coconut Grove"],
        "casual_suffixes": ["Seafood Restaurant", "Beach Shack & Diner", "Coastal Kitchen", "Fish Curry House"],
        "cafe_prefixes": ["Kashi", "Artjuna", "Qissa", "Driftwood", "Waves", "Ocean Breeze", "Little Earth"],
        "cafe_suffixes": ["Art Cafe", "Bakery & Coffee", "Garden Bistro", "Beach Cafe", "Roaster"],
        "budget_prefixes": ["Vinayak", "Ritz Classic", "Kayees", "Mylari", "Beach Tiffin", "Sea Breeze"],
        "budget_suffixes": ["Fish Thali House", "Tiffin Home", "Biryani Point", "Nashta Corner", "Mess & Meals"],
    },
    "India_Hill": {
        "cuisines": [
            "Himachali & North Indian", "Tibetan & Momos", "Himalayan Trout & Grills", "Continental Cafe",
            "Wood-Fired Pizza", "Pahari Traditional", "Boutique Bakery", "South & North Indian",
            "Gourmet Chai & Snacks", "Cafe & Healthy Bowls", "Multi-Cuisine", "Street Maggi & Chai"
        ],
        "fine_prefixes": ["Wildflower", "Himalayan", "Pine Crest", "The Glen", "Cloud Nine", "Alpine"],
        "fine_suffixes": ["Mountain Dining", "Valley View Restaurant", "Cedar Grill & Bar", "Heritage Hearth"],
        "casual_prefixes": ["Tibur", "Woodshed", "Pine & Cedar", "Mountain Echo", "Valley Flavours", "Snow View"],
        "casual_suffixes": ["Diner & Kitchen", "Family Restaurant", "Trout House", "Mountain Kitchen"],
        "cafe_prefixes": ["Cafe 1947", "Wake & Bake", "Himalayan", "Moonpeak", "Evergreen", "Misty Bean"],
        "cafe_suffixes": ["Bakery & Cafe", "Coffee Roasters", "Tea Garden Cafe", "Alpine Bistro", "Bakehouse"],
        "budget_prefixes": ["Tibetan Kitchen", "Mama's", "Lama's", "Trekkers", "Pahadi", "Old Town"],
        "budget_suffixes": ["Momo Corner", "Dhaba", "Tiffin & Tea Stalls", "Noodle House", "Maggi Point"],
    },
    "India_Standard": {
        "cuisines": [
            "North Indian & Tandoor", "South Indian Tiffin", "Hyderabadi Biryani", "Mughlai",
            "Continental & Italian", "Pan-Asian", "Street Food & Chaat", "Pure Vegetarian Thali",
            "Artisan Coffee & Pastry", "Tandoori Grills", "Multi-Cuisine Buffet", "Desi Sweets"
        ],
        "fine_prefixes": ["The Grand", "Royal", "Saffron", "The Pavilion", "Barbeque", "Spice Route"],
        "fine_suffixes": ["Fine Dining", "Lounge & Bar", "Sky Restaurant", "Grand Kitchen", "Grill"],
        "casual_prefixes": ["Paradise", "Bawarchi", "Saravanaa", "Pind", "Chowk", "Karim's", "Mainland"],
        "casual_suffixes": ["Restaurant & Bar", "Bhojanalaya", "Family Diner", "Kitchen", "Curry Point"],
        "cafe_prefixes": ["Third Wave", "Blue Tokai", "The Coffee", "Chai Point", "Madras Cafe", "Mocha"],
        "cafe_suffixes": ["Roastery & Cafe", "Bakery & Bistro", "Coffee House", "Tea Bar", "Eatery"],
        "budget_prefixes": ["Haldiram's", "Bikanervala", "Annapurna", "Udupi", "Sagar", "Chatoree"],
        "budget_suffixes": ["Tiffin Room", "Sweets & Snacks", "Dhaba", "Bhavan", "Fast Food"],
    },
    "Europe": {
        "cuisines": [
            "Classic French", "Italian Trattoria", "Mediterranean Seafood", "Modern European",
            "Traditional Brasserie", "Spanish Tapas", "Artisan Bakery & Pastry", "Neapolitan Pizza",
            "Gourmet Gastropub", "Farm-to-Table", "Local Alpine / Regional", "Street Food & Bites"
        ],
        "fine_prefixes": ["Le Gabriel", "L'Ambroisie", "Grand Restaurant", "Villa", "La Pergola", "Atelier", "Le Jardin"],
        "fine_suffixes": ["Haute Gastronomie", "Fine Dining", "Gourmet Table", "Dining Room", "Restaurant & Salon"],
        "casual_prefixes": ["Trattoria", "Bistrot", "Brasserie", "Osteria", "La Taverna", "Ristorante", "Chez"],
        "casual_suffixes": ["del Centro", "Paul Bert", "al Mare", "Artisan Kitchen", "Bistro & Wine Bar", "Brasserie"],
        "cafe_prefixes": ["Café", "Pasticceria", "Boulangerie", "Sant'Eustachio", "The Daily", "Artisan"],
        "cafe_suffixes": ["de Flore", "Bakery & Coffee", "Espresso Bar", "Bakehouse", "Patisserie & Tea"],
        "budget_prefixes": ["Bonci", "Trapizzino", "Pizzarium", "L'As", "Old Town", "The Local"],
        "budget_suffixes": ["Pizza al Taglio", "Street Food", "Tapas & Bites", "Bocadillos", "Bites & Beer"],
    },
    "East_Asia": {
        "cuisines": [
            "Edomae Sushi", "Traditional Kaiseki", "Ramen & Tsukemen", "Tonkatsu & Tempura",
            "Yakitori & Izakaya", "Korean BBQ", "Cantonese Dim Sum", "Japanese Curry & Donburi",
            "Artisan Tea House", "Modern Asian Fusion", "Soba & Udon", "Night Market Street Food"
        ],
        "fine_prefixes": ["Sukiyabashi", "Narisawa", "Kagurazaka", "The Silk", "Imperial", "Aman"],
        "fine_suffixes": ["Kaiseki Dining", "Sushi Master", "Gastronomy", "Grand Dining", "Pavilion"],
        "casual_prefixes": ["Maisen", "Gonpachi", "Din Tai", "Rokurinsha", "Torikizoku", "Ippudo", "Gyu-Kaku"],
        "casual_suffixes": ["Izakaya & Grill", "Ramen Bar", "Kitchen & Dumplings", "Noodle House", "Robata"],
        "cafe_prefixes": ["Harbs", "Matcha", "Chado", "Nana's", "Artisan", "Green Tea"],
        "cafe_suffixes": ["Tea Lounge", "Dessert Cafe", "Coffee & Bakery", "Bakehouse", "Patisserie"],
        "budget_prefixes": ["Tenya", "Ichiran", "Afuri", "Matsuya", "Yoshinoya", "Street Stall"],
        "budget_suffixes": ["Ramen Booths", "Tendon & Donburi", "Quick Noodle", "Bites & Skewers", "Snack Bar"],
    },
    "SE_Asia": {
        "cuisines": [
            "Royal Thai", "Vietnamese Pho & Banh Mi", "Indonesian Satay & Nasi", "Penang Street Food",
            "Chilli Crab & Seafood", "Isan Papaya & Grills", "Peranakan Heritage", "Tropical Bakery",
            "Specialty Coffee", "Pad Thai & Noodles", "Night Market Stalls", "Modern Asian"
        ],
        "fine_prefixes": ["Sühring", "Gaa", "Blue Elephant", "The Siam", "Mandarin", "Saigon"],
        "fine_suffixes": ["Fine Dining", "Royal Heritage", "Riverside Dining", "Gastronomic Room"],
        "casual_prefixes": ["Supanniga", "Somtum Der", "Madame Hien", "Bintang", "PappaRich", "Chilli Crab"],
        "casual_suffixes": ["Eating Room", "Kitchen & Bar", "Seafood House", "Heritage Diner"],
        "cafe_prefixes": ["Roast", "The Workshop", "Cong Caphe", "Cafe Amazon", "Artisan", "Lotus"],
        "cafe_suffixes": ["Coffee Roaster", "Bakery Cafe", "Tea House", "Bakehouse", "Garden Cafe"],
        "budget_prefixes": ["Jay Fai", "Thipsamai", "Nai Mong", "Wattana", "Banh Mi", "Street Hawker"],
        "budget_suffixes": ["Pad Thai Stall", "Noodle Broth House", "Street Wok", "Oyster Omelette", "Food Hub"],
    },
    "Americas": {
        "cuisines": [
            "American Contemporary", "Dry-Aged Steakhouse", "Farm-to-Table", "Mexican Gastronomy",
            "Peruvian & Ceviche", "New York Style Pizza", "Smokehouse BBQ", "Gourmet Deli & Bagels",
            "Artisan Bakery & Pastry", "Coastal Seafood Bar", "Craft Burgers & Brews", "Latin Street Tacos"
        ],
        "fine_prefixes": ["Le Bernardin", "Eleven Madison", "The Grill", "Gramercy", "Ocean Prime", "The Capital"],
        "fine_suffixes": ["Tavern & Dining", "Steakhouse & Bar", "Fine Gastronomy", "Grand Dining Room"],
        "casual_prefixes": ["Balthazar", "Keens", "Momofuku", "The Smokehouse", "Blue Ribbon", "Tavern on"],
        "casual_suffixes": ["Brasserie & Raw Bar", "Steakhouse", "Noodle Bar", "Grill & Taproom", "Diner"],
        "cafe_prefixes": ["Levain", "Russ & Daughters", "Blue Bottle", "Stumptown", "Magnolia", "Artisan"],
        "cafe_suffixes": ["Bakery & Coffee", "Bagel & Appetizing", "Cafe & Roastery", "Bakehouse", "Pastry Bar"],
        "budget_prefixes": ["Joe's", "Katz's", "Shake Shack", "Taqueria", "Halal Guys", "Corner"],
        "budget_suffixes": ["Pizza Slices", "Delicatessen", "Burger Shack", "Taco Stand", "Street Cart"],
    },
    "MENA_Africa": {
        "cuisines": [
            "Levantine & Lebanese", "Traditional Emirati", "Moroccan Tagine & Couscous", "Egyptian Grills & Koshari",
            "Authentic Persian Kebabs", "Seafood & Coastal Grills", "Yemeni Mandi", "Turkish Charcoal Grills",
            "Artisan Arabian Tea & Cafe", "Modern African Fusion", "Mezze & Hummus Bar", "Historic Street Grills"
        ],
        "fine_prefixes": ["Atmosphere", "Ossiano", "Al Nafoorah", "Pierchic", "La Mamounia", "The Palace"],
        "fine_suffixes": ["Fine Dining Lounge", "Under-water Dining", "Royal Terrace", "Grand Grill"],
        "casual_prefixes": ["Zuma", "Coya", "Arabian Tea", "Bait Al Mandi", "Al Hallab", "Al Fanar"],
        "casual_suffixes": ["House & Grills", "Restaurant & Lounge", "Heritage Diner", "Mandi House"],
        "cafe_prefixes": ["Comptoir 102", "Al Mashowa", "El Fishawy", "Café Clock", "Artisan", "Saffron"],
        "cafe_suffixes": ["Tea House", "Organic Cafe & Juice", "Historic Cafe", "Bakehouse & Coffee"],
        "budget_prefixes": ["Al Ustad", "Ravi", "Bu Qtair", "Koshari Abou Tarek", "Shawarma", "Falafel"],
        "budget_suffixes": ["Special Kabab", "Pakistani Karahi", "Fish Shack", "Street Food Stalls", "Grill Point"],
    },
    "Oceania": {
        "cuisines": [
            "Modern Australian", "Pacific Rim Seafood", "New Zealand Farm-to-Table", "Wood-Fired Pizzeria",
            "Asian Fusion & Bao", "Contemporary Bistro", "Artisan Bakery & Brunch", "Harbour Steakhouse",
            "Specialty Flat White Coffee", "Gourmet Burgers", "Craft Beer Gastropub", "Fish & Chips by the Bay"
        ],
        "fine_prefixes": ["Quay", "Bennelong", "Tetsuya's", "Aria", "The Boatshed", "Harbour View"],
        "fine_suffixes": ["Restaurant & Lounge", "Fine Dining Room", "Ocean Gastronomy", "Pavilion"],
        "casual_prefixes": ["Chin Chin", "Rockpool", "The Boathouse", "Hurricane's", "Coogee Pavilion", "Merivale"],
        "casual_suffixes": ["Bar & Grill", "Dining Room & Wok", "Seafood Kitchen", "Bistro & Terrace"],
        "cafe_prefixes": ["Single O", "Grounds of Alexandria", "Lune", "Bills", "Black Star", "Artisan"],
        "cafe_suffixes": ["Croissanterie", "Coffee Roasters", "Bakery & Brunch", "Cafe & Pastry", "Eatery"],
        "budget_prefixes": ["Mary's", "Harry's Cafe de Wheels", "Fish Market", "Bondi Burger", "Pacific", "The Pier"],
        "budget_suffixes": ["Pies & Hotdogs", "Fish & Chips", "Burger Bar", "Bao & Bites", "Street Shack"],
    },
}

def determine_restaurant_region(city: str, country: str) -> str:
    """Classifies destination into appropriate culinary region."""
    c_low = country.lower().strip()
    city_low = city.lower().strip()

    if c_low == "india":
        coastal = {
            "kochi", "goa", "mumbai", "chennai", "pondicherry", "varkala", "kovalam", "kumarakom",
            "alleppey", "puri", "daman", "diu", "karwar", "murudeshwar", "gokarna", "mangalore",
            "alibaug", "ratnagiri", "ganpatipule", "kashid", "havelock island", "neil island",
            "port blair", "visakhapatnam", "kanyakumari", "rameswaram", "dhanushkodi", "mahabalipuram"
        }
        hill = {
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
        heritage = {
            "jaipur", "udaipur", "jodhpur", "jaisalmer", "pushkar", "bikaner", "kumbhalgarh",
            "mandu", "hampi", "badami", "belur", "mysuru", "agra", "varanasi", "khajuraho",
            "orchha", "gwalior", "chittorgarh", "ajmer", "alwar", "shekhawati", "bundi",
            "rann of kutch", "bhuj", "patna", "gaya", "bodh gaya", "rajgir", "nalanda",
            "thanjavur", "madurai", "tiruchirappalli", "chettinad", "kanchipuram"
        }
        if city_low in coastal:
            return "India_Coastal"
        elif city_low in hill:
            return "India_Hill"
        elif city_low in heritage:
            return "India_Heritage"
        else:
            return "India_Standard"

    europe = {
        "france", "italy", "germany", "spain", "united kingdom", "greece", "switzerland",
        "austria", "portugal", "netherlands", "belgium", "norway", "sweden", "finland",
        "denmark", "ireland", "croatia", "czech republic", "hungary", "poland", "iceland",
        "turkey", "slovenia", "estonia", "latvia", "lithuania", "malta", "cyprus", "monaco"
    }
    if c_low in europe:
        return "Europe"

    east_asia = {"japan", "south korea", "china", "taiwan", "hong kong", "macau"}
    if c_low in east_asia:
        return "East_Asia"

    se_asia = {"thailand", "vietnam", "indonesia", "malaysia", "philippines", "cambodia", "laos", "myanmar", "singapore"}
    if c_low in se_asia:
        return "SE_Asia"

    americas = {"united states", "canada", "mexico", "costa rica", "panama", "brazil", "argentina", "peru", "chile", "colombia", "ecuador", "jamaica", "bahamas", "cuba", "dominican republic"}
    if c_low in americas:
        return "Americas"

    mena_africa = {
        "united arab emirates", "egypt", "saudi arabia", "qatar", "oman", "jordan", "israel",
        "morocco", "south africa", "kenya", "tanzania", "mauritius", "seychelles", "maldives",
        "namibia", "zimbabwe", "botswana", "madagascar"
    }
    if c_low in mena_africa:
        return "MENA_Africa"

    oceania = {"australia", "new zealand", "fiji", "french polynesia", "vanuatu", "samoa"}
    if c_low in oceania:
        return "Oceania"

    return "Europe"


def generate_restaurant_catalog_for_destinations(
    destinations: List[Tuple[int, str, str, Optional[float]]]
) -> Dict[Tuple[str, str], List[Tuple[str, str, float, float]]]:
    """Generates 12 restaurants per destination for all 500 destinations.
    
    Returns:
        Dict mapping (city, country) to list of (name, cuisine, average_cost_per_person, rating).
    """
    catalog: Dict[Tuple[str, str], List[Tuple[str, str, float, float]]] = {}

    for dest_id, city, country, avg_daily_cost in destinations:
        dest_key = (city, country)

        # Use curated landmark list if present
        if dest_key in CURATED_LANDMARK_RESTAURANTS:
            catalog[dest_key] = list(CURATED_LANDMARK_RESTAURANTS[dest_key])
            continue

        region_key = determine_restaurant_region(city, country)
        profile = RESTAURANT_REGIONAL_PROFILES[region_key]

        hash_seed = int(hashlib.sha256(f"rest_{city}_{country}_{RANDOM_SEED}".encode("utf-8")).hexdigest()[:8], 16)
        rng = random.Random(hash_seed)

        daily_cost = float(avg_daily_cost) if avg_daily_cost and avg_daily_cost > 0 else 5000.0
        used_names: Set[str] = set()

        def make_unique(cand: str) -> str:
            clean = cand.strip()
            if clean not in used_names:
                used_names.add(clean)
                return clean
            alt = f"{clean} {city}"
            if alt not in used_names:
                used_names.add(alt)
                return alt
            alt2 = f"{clean} Kitchen"
            used_names.add(alt2)
            return alt2

        rest_list: List[Tuple[str, str, float, float]] = []

        # 1. Fine Dining / Royal / Haute Gastronomy (Tier 1)
        f_p1 = rng.choice(profile["fine_prefixes"])
        f_s1 = rng.choice(profile["fine_suffixes"])
        name_1 = make_unique(f"{f_p1} {city} {f_s1}")
        cui_1 = profile["cuisines"][0]
        cost_1 = round(daily_cost * rng.uniform(0.45, 0.85) / 25.0) * 25.0
        rate_1 = round(rng.uniform(4.7, 4.9), 1)
        rest_list.append((name_1, cui_1, max(cost_1, 1500.0), rate_1))

        # 2. Upscale Heritage / Panoramic View / Seafood Fine Dining (Tier 2)
        f_p2 = rng.choice([p for p in profile["fine_prefixes"] if p != f_p1] or profile["fine_prefixes"])
        name_2 = make_unique(f"{city} Panorama {f_p2}")
        cui_2 = profile["cuisines"][1] if len(profile["cuisines"]) > 1 else profile["cuisines"][0]
        cost_2 = round(daily_cost * rng.uniform(0.35, 0.65) / 25.0) * 25.0
        rate_2 = round(rng.uniform(4.5, 4.8), 1)
        rest_list.append((name_2, cui_2, max(cost_2, 1200.0), rate_2))

        # 3. Regional Specialty Diner (Tier 3)
        c_p1 = rng.choice(profile["casual_prefixes"])
        c_s1 = rng.choice(profile["casual_suffixes"])
        name_3 = make_unique(f"{c_p1} {city} {c_s1}")
        cui_3 = profile["cuisines"][2] if len(profile["cuisines"]) > 2 else profile["cuisines"][0]
        cost_3 = round(daily_cost * rng.uniform(0.20, 0.38) / 10.0) * 10.0
        rate_3 = round(rng.uniform(4.4, 4.7), 1)
        rest_list.append((name_3, cui_3, max(cost_3, 650.0), rate_3))

        # 4. Contemporary Bistro / Multi-Cuisine (Tier 4)
        c_p2 = rng.choice([p for p in profile["casual_prefixes"] if p != c_p1] or profile["casual_prefixes"])
        name_4 = make_unique(f"{c_p2} Kitchen & Grill {city}")
        cui_4 = profile["cuisines"][3] if len(profile["cuisines"]) > 3 else profile["cuisines"][0]
        cost_4 = round(daily_cost * rng.uniform(0.18, 0.32) / 10.0) * 10.0
        rate_4 = round(rng.uniform(4.3, 4.6), 1)
        rest_list.append((name_4, cui_4, max(cost_4, 550.0), rate_4))

        # 5. Local Grill / Seafood / Farm Specialty (Tier 5)
        name_5 = make_unique(f"The {city} Grill & Harvest")
        cui_5 = profile["cuisines"][4] if len(profile["cuisines"]) > 4 else profile["cuisines"][0]
        cost_5 = round(daily_cost * rng.uniform(0.16, 0.30) / 10.0) * 10.0
        rate_5 = round(rng.uniform(4.3, 4.6), 1)
        rest_list.append((name_5, cui_5, max(cost_5, 500.0), rate_5))

        # 6. Family Diner / Traditional Feast / Thali (Tier 6)
        name_6 = make_unique(f"{city} Heritage Flavours")
        cui_6 = profile["cuisines"][5] if len(profile["cuisines"]) > 5 else profile["cuisines"][0]
        cost_6 = round(daily_cost * rng.uniform(0.12, 0.24) / 10.0) * 10.0
        rate_6 = round(rng.uniform(4.2, 4.5), 1)
        rest_list.append((name_6, cui_6, max(cost_6, 400.0), rate_6))

        # 7. Artisan Bakery & Coffeehouse (Tier 7)
        cf_p1 = rng.choice(profile["cafe_prefixes"])
        cf_s1 = rng.choice(profile["cafe_suffixes"])
        name_7 = make_unique(f"{cf_p1} {city} {cf_s1}")
        cui_7 = profile["cuisines"][6] if len(profile["cuisines"]) > 6 else "Bakery & Coffee"
        cost_7 = round(daily_cost * rng.uniform(0.08, 0.16) / 10.0) * 10.0
        rate_7 = round(rng.uniform(4.3, 4.7), 1)
        rest_list.append((name_7, cui_7, max(cost_7, 300.0), rate_7))

        # 8. Organic / Vegan / Health Bistro (Tier 8)
        name_8 = make_unique(f"Green Leaf Bistro {city}")
        cui_8 = profile["cuisines"][7] if len(profile["cuisines"]) > 7 else "Healthy & Organic"
        cost_8 = round(daily_cost * rng.uniform(0.09, 0.18) / 10.0) * 10.0
        rate_8 = round(rng.uniform(4.3, 4.6), 1)
        rest_list.append((name_8, cui_8, max(cost_8, 350.0), rate_8))

        # 9. Cultural Tea House & Lounge (Tier 9)
        name_9 = make_unique(f"{city} Corner Tea & Bakes")
        cui_9 = profile["cuisines"][8] if len(profile["cuisines"]) > 8 else "Tea House & Snacks"
        cost_9 = round(daily_cost * rng.uniform(0.06, 0.14) / 10.0) * 10.0
        rate_9 = round(rng.uniform(4.2, 4.5), 1)
        rest_list.append((name_9, cui_9, max(cost_9, 250.0), rate_9))

        # 10. Famous Street Food / Night Market Hub (Tier 10)
        b_p1 = rng.choice(profile["budget_prefixes"])
        b_s1 = rng.choice(profile["budget_suffixes"])
        name_10 = make_unique(f"{b_p1} {city} {b_s1}")
        cui_10 = profile["cuisines"][9] if len(profile["cuisines"]) > 9 else "Street Food"
        cost_10 = round(daily_cost * rng.uniform(0.04, 0.09) / 10.0) * 10.0
        rate_10 = round(rng.uniform(4.3, 4.8), 1)
        rest_list.append((name_10, cui_10, max(cost_10, 150.0), rate_10))

        # 11. Traditional Tiffin / Local Eatery (Tier 11)
        b_p2 = rng.choice([p for p in profile["budget_prefixes"] if p != b_p1] or profile["budget_prefixes"])
        name_11 = make_unique(f"{b_p2} Fast Food {city}")
        cui_11 = profile["cuisines"][10] if len(profile["cuisines"]) > 10 else "Local Eatery"
        cost_11 = round(daily_cost * rng.uniform(0.03, 0.08) / 10.0) * 10.0
        rate_11 = round(rng.uniform(4.2, 4.6), 1)
        rest_list.append((name_11, cui_11, max(cost_11, 120.0), rate_11))

        # 12. Quick Bites / Snacks & Desserts (Tier 12)
        name_12 = make_unique(f"{city} Express Tiffin & Sweets")
        cui_12 = profile["cuisines"][11] if len(profile["cuisines"]) > 11 else "Snacks & Sweets"
        cost_12 = round(daily_cost * rng.uniform(0.03, 0.07) / 10.0) * 10.0
        rate_12 = round(rng.uniform(4.1, 4.5), 1)
        rest_list.append((name_12, cui_12, max(cost_12, 100.0), rate_12))

        catalog[dest_key] = rest_list

    return catalog
