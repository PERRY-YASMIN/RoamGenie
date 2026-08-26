"""Attractions for 26 South American destinations in RoamGenie (Phase D2)."""
from typing import Dict, List, Tuple

# Format: (name, category, entry_fee_inr, rating)
SOUTH_AMERICA_ATTRACTIONS: Dict[Tuple[str, str], List[Tuple[str, str, float, float]]] = {
    # Brazil (7)
    ("Rio de Janeiro", "Brazil"): [
        ("Christ the Redeemer (Cristo Redentor) & Corcovado Train", "monument", 1600.00, 5.0),
        ("Sugarloaf Mountain (Pão de Açúcar) Cable Car", "viewpoint", 2200.00, 4.9),
        ("Copacabana & Ipanema Iconic Beaches", "beach", 0.00, 4.8),
        ("Selarón Steps (Escadaria Selarón Mosaic Stairs)", "cultural", 0.00, 4.8),
        ("Tijuca National Park (World's Largest Urban Forest)", "nature", 0.00, 4.8),
    ],
    ("Sao Paulo", "Brazil"): [
        ("Paulista Avenue & MASP Art Museum (Glass Easels)", "museum", 900.00, 4.8),
        ("Ibirapuera Park (Oscar Niemeyer Buildings)", "park", 0.00, 4.8),
        ("Municipal Market of São Paulo (Mercadão)", "market", 0.00, 4.7),
        ("Beco do Batman (Graffiti Street Art Alley)", "cultural", 0.00, 4.7),
        ("Liberdade (World's Largest Japanese District)", "cultural", 0.00, 4.6),
    ],
    ("Salvador", "Brazil"): [
        ("Pelourinho UNESCO Colorful Colonial District", "heritage", 0.00, 4.8),
        ("Lacerda Elevator (Elevador Lacerda Art Deco Lift)", "viewpoint", 10.00, 4.6),
        ("Church of São Francisco (Gold Gilded Interior)", "religious", 150.00, 4.8),
        ("Farol da Barra Lighthouse & Nautical Museum", "fort", 250.00, 4.7),
        ("Mercado Modelo Traditional Bahian Crafts", "market", 0.00, 4.5),
    ],
    ("Paraty", "Brazil"): [
        ("Historic Centre of Paraty UNESCO (Pedestrian Cobblestones)", "heritage", 0.00, 4.9),
        ("Paraty Bay Boat Tour & Tropical Island Snorkeling", "adventure", 1800.00, 4.9),
        ("Cachoeira do Tobogã (Natural Rock Slide Waterfall)", "waterfall", 0.00, 4.7),
        ("Trindade Beach & Natural Ocean Swimming Pool", "beach", 0.00, 4.8),
        ("Cachaça Distillery Historic Tour & Tasting", "cultural", 300.00, 4.6),
    ],
    ("Foz do Iguacu", "Brazil"): [
        ("Iguaçu Falls UNESCO (Devil's Throat Catwalk)", "waterfall", 1400.00, 5.0),
        ("Parque das Aves (Atlantic Rainforest Bird Sanctuary)", "wildlife", 1200.00, 4.9),
        ("Macuco Safari Speedboat Rush Under Iguazu Falls", "adventure", 5500.00, 5.0),
        ("Itaipu Hydroelectric Dam Panoramic Tour", "architecture", 750.00, 4.7),
        ("Marco das Três Fronteiras (3-Country Landmark)", "viewpoint", 600.00, 4.6),
    ],
    ("Manaus", "Brazil"): [
        ("Amazon Rainforest Guided Jungle Safari & Pink Dolphins", "wildlife", 6500.00, 5.0),
        ("Teatro Amazonas Belle Époque Opera House", "palace", 400.00, 4.9),
        ("Meeting of the Waters (Encontro das Águas Boat Tour)", "nature", 2800.00, 4.9),
        ("Adolpho Lisboa Municipal Market on Rio Negro", "market", 0.00, 4.5),
        ("MUSA (Museum of the Amazon Canopy Tower 42m)", "nature", 650.00, 4.8),
    ],
    ("Florianopolis", "Brazil"): [
        ("Praia da Joaquina Sandboarding on Giant Dunes", "adventure", 350.00, 4.8),
        ("Lagoa da Conceição Vibrant Lagoon & Gastronomy", "nature", 0.00, 4.7),
        ("Campeche Island (Ilha do Campeche) Turquoise Waters", "beach", 2500.00, 5.0),
        ("Hercílio Luz Historic Suspension Bridge", "monument", 0.00, 4.7),
        ("Praia Mole Surfing Coast & Beach Bars", "beach", 0.00, 4.6),
    ],

    # Argentina (6)
    ("Buenos Aires", "Argentina"): [
        ("Teatro Colón World-Renowned Opera House", "architecture", 1800.00, 5.0),
        ("La Recoleta Cemetery & Eva Perón's Tomb", "historical", 1200.00, 4.8),
        ("Caminito & Colorful Tenements of La Boca", "cultural", 0.00, 4.7),
        ("Plaza de Mayo & Casa Rosada (Pink Presidential Palace)", "historical", 0.00, 4.7),
        ("San Telmo Sunday Antique Fair & Street Tango", "market", 0.00, 4.8),
    ],
    ("Bariloche", "Argentina"): [
        ("Circuito Chico Scenic Lake Route & Cerro Campanario", "viewpoint", 850.00, 5.0),
        ("Cerro Catedral Ski Resort & Winter Alpine Sports", "adventure", 5500.00, 4.8),
        ("Nahuel Huapi National Park & Victoria Island Boat", "nature", 3500.00, 4.9),
        ("Civic Center (Centro Cívico) Alpine Architecture", "cultural", 0.00, 4.6),
        ("Artisan Chocolate Tasting Trail on Calle Mitre", "cultural", 0.00, 4.9),
    ],
    ("Mendoza", "Argentina"): [
        ("Uco Valley High-Altitude Malbec Wine Tour", "cultural", 6500.00, 5.0),
        ("Aconcagua Provincial Park (Highest Peak in Americas)", "adventure", 1800.00, 5.0),
        ("General San Martín Park & Monument to the Andes", "park", 0.00, 4.7),
        ("Termas de Cacheuta Thermal Spa in Mountain Gorge", "nature", 2500.00, 4.8),
        ("Puente del Inca Natural Sulphur Rock Bridge", "nature", 0.00, 4.6),
    ],
    ("Ushuaia", "Argentina"): [
        ("Beagle Channel Catamaran Cruise & Les Eclaireurs Lighthouse", "nature", 5500.00, 5.0),
        ("Tierra del Fuego National Park End of the World Train", "nature", 2800.00, 4.9),
        ("Martillo Island Walking Among Magellanic Penguins", "wildlife", 12000.00, 5.0),
        ("Laguna Esmeralda Glacial Turquoise Trek", "adventure", 0.00, 4.9),
        ("End of the World Museum (Museo del Fin del Mundo)", "museum", 800.00, 4.5),
    ],
    ("Salta", "Argentina"): [
        ("MAAM (Museum of High Altitude Archaeology & Inca Mummies)", "museum", 900.00, 5.0),
        ("Cerro San Bernardo Cable Car (Teleférico)", "viewpoint", 750.00, 4.7),
        ("Salinas Grandes Salt Flats & Cuesta del Lipán", "nature", 3500.00, 5.0),
        ("Salta Cathedral & 9 de Julio Historical Plaza", "religious", 0.00, 4.8),
        ("Quebrada de Cafayate Red Sandstone Canyons Excursion", "nature", 3000.00, 4.9),
    ],
    ("El Calafate", "Argentina"): [
        ("Perito Moreno Glacier UNESCO Boardwalks & Calving Ice", "nature", 3500.00, 5.0),
        ("Perito Moreno Mini-Trekking on Glacial Ice", "adventure", 18000.00, 5.0),
        ("Upsala & Spegazzini Glaciers Lake Cruise", "nature", 9500.00, 5.0),
        ("Glaciarium Ice Museum & Sub-Zero Ice Bar", "museum", 1400.00, 4.7),
        ("Walichu Caves Prehistoric Hunter-Gatherer Rock Art", "historical", 600.00, 4.5),
    ],

    # Peru (4)
    ("Cusco", "Peru"): [
        ("Machu Picchu UNESCO Ancient Inca Citadel Excursion", "heritage", 4200.00, 5.0),
        ("Sacsayhuamán Megalithic Inca Stone Fortress", "heritage", 1800.00, 4.9),
        ("Plaza de Armas & Cusco Cathedral of the Virgin Mary", "religious", 700.00, 4.8),
        ("Rainbow Mountain (Vinicunca 5200m) Sunrise Trek", "adventure", 2500.00, 4.9),
        ("San Pedro Market Traditional Peruvian Andean Herbs", "market", 0.00, 4.7),
    ],
    ("Lima", "Peru"): [
        ("Larco Museum Pre-Columbian Gold & Ceramic Art", "museum", 850.00, 5.0),
        ("Historic Centre of Lima & Monastery of San Francisco Catacombs", "heritage", 450.00, 4.8),
        ("Miraflores Boardwalk (Malecón) & Parapuerto Gliding", "viewpoint", 0.00, 4.8),
        ("Huaca Pucllana 5th-Century Adobe Pyramid", "historical", 400.00, 4.7),
        ("Barranco Bohemian Art District & Bridge of Sighs", "cultural", 0.00, 4.8),
    ],
    ("Arequipa", "Peru"): [
        ("Santa Catalina Monastery (City within a City)", "religious", 950.00, 5.0),
        ("Colca Canyon (World's Deepest Gorge & Andean Condors)", "nature", 2200.00, 5.0),
        ("Plaza de Armas & Basilica Cathedral of Arequipa", "religious", 0.00, 4.8),
        ("Yanahuara Scenic Mirador & Misti Volcano View", "viewpoint", 0.00, 4.7),
        ("Mundo Alpaca Textile Heritage & Camelid Interaction", "cultural", 0.00, 4.8),
    ],
    ("Puno", "Peru"): [
        ("Lake Titicaca Uros Floating Reed Islands Boat Tour", "cultural", 1200.00, 4.8),
        ("Taquile Island UNESCO Traditional Textile Weavers", "cultural", 1500.00, 4.9),
        ("Sillustani Ancient Pre-Inca Burial Towers (Chullpas)", "historical", 350.00, 4.7),
        ("Puno Cathedral & Plaza de Armas", "religious", 0.00, 4.5),
        ("Amantaní Island Overnight Indigenous Homestay", "cultural", 2500.00, 4.8),
    ],

    # Chile, Colombia, Ecuador & Bolivia (9)
    ("Santiago", "Chile"): [
        ("San Cristóbal Hill (Cerro San Cristóbal) & Funicular", "viewpoint", 550.00, 4.8),
        ("Sky Costanera (Tallest Tower in South America 300m)", "viewpoint", 1600.00, 4.7),
        ("Plaza de Armas & Metropolitan Cathedral of Santiago", "religious", 0.00, 4.7),
        ("Santa Lucía Hill Historic Castle & Gardens", "park", 0.00, 4.7),
        ("La Chascona (Pablo Neruda's Quirky House Museum)", "museum", 750.00, 4.6),
    ],
    ("Valparaiso", "Chile"): [
        ("Cerro Alegre & Cerro Concepción Street Art Staircases", "cultural", 0.00, 4.9),
        ("Historic Ascensores (Heritage Wooden Funiculars)", "monument", 30.00, 4.7),
        ("La Sebastiana (Pablo Neruda Cliffside House)", "museum", 750.00, 4.8),
        ("Plaza Sotomayor & Naval Headquarters Monument", "historical", 0.00, 4.5),
        ("Viña del Mar Flower Clock & Pacific Beaches Excursion", "beach", 0.00, 4.6),
    ],
    ("San Pedro de Atacama", "Chile"): [
        ("Valle de la Luna (Moon Valley Dunes & Salt Canyons)", "nature", 1200.00, 5.0),
        ("El Tatio Geysers (World's 3rd Largest Geyser Field 4320m)", "nature", 1600.00, 4.9),
        ("Piedras Rojas & High Altitude Altiplanic Lagoons", "nature", 2500.00, 5.0),
        ("Atacama Dark Sky Astronomical Stargazing Tour", "viewpoint", 3500.00, 5.0),
        ("Laguna Cejar Floating Salt Lagoon Swimming", "adventure", 1800.00, 4.8),
    ],
    ("Puerto Varas", "Chile"): [
        ("Lake Llanquihue Scenic Promenade & Osorno Volcano View", "viewpoint", 0.00, 4.9),
        ("Osorno Volcano Ski & Chairlift Mountain Excursion", "adventure", 2200.00, 4.9),
        ("Petrohué Waterfalls Turquoise Rapids (Todos los Santos)", "waterfall", 650.00, 4.9),
        ("Sacred Heart of Jesus Church (German Wooden Church)", "architecture", 0.00, 4.6),
        ("Vicente Pérez Rosales National Park Forest Trek", "nature", 650.00, 4.8),
    ],
    ("Bogota", "Colombia"): [
        ("Monserrate Hilltop Sanctuary & Cable Car Panorama", "viewpoint", 600.00, 4.9),
        ("Gold Museum (Museo del Oro Pre-Hispanic Gold)", "museum", 120.00, 5.0),
        ("La Candelaria Historic Colonial Quarter & Graffiti Tour", "cultural", 0.00, 4.8),
        ("Botero Museum (Fernando Botero Volumetric Art)", "museum", 0.00, 4.9),
        ("Zipaquirá Salt Cathedral Underground Marvel Excursion", "religious", 1800.00, 4.9),
    ],
    ("Medellin", "Colombia"): [
        ("Comuna 13 Escalators & Hip-Hop Street Art Tour", "cultural", 0.00, 5.0),
        ("Metrocable Aerial Transit System & Arví Nature Park", "viewpoint", 250.00, 4.9),
        ("Plaza Botero (23 Giant Bronze Statues)", "monument", 0.00, 4.7),
        ("Guatapé & El Peñol 740-Step Giant Rock Excursion", "adventure", 1800.00, 5.0),
        ("Jardín Botánico de Medellín & Orchid House", "garden", 0.00, 4.7),
    ],
    ("Cartagena", "Colombia"): [
        ("Walled Old City of Cartagena (Ciudad Amurallada UNESCO)", "heritage", 0.00, 5.0),
        ("Castillo San Felipe de Barajas Fortress & Tunnels", "fort", 750.00, 4.8),
        ("Getsemaní Bohemian Quarter & Umbrella Street", "cultural", 0.00, 4.8),
        ("Rosario Islands (Islas del Rosario) Catamaran Snorkeling", "beach", 3500.00, 4.9),
        ("Convento de la Popa Hilltop Cloister & City View", "religious", 350.00, 4.7),
    ],
    ("Quito", "Ecuador"): [
        ("Historic Center of Quito UNESCO (San Francisco & La Compañía)", "religious", 350.00, 4.9),
        ("Mitad del Mundo (Middle of the World Monument Equator)", "monument", 450.00, 4.7),
        ("TelefériQo High Altitude Gondola to Pichincha Volcano", "viewpoint", 750.00, 4.8),
        ("El Panecillo Winged Virgin of Quito Monument", "viewpoint", 150.00, 4.6),
        ("Basilica of the National Vow (Gothic Spires Climb)", "architecture", 200.00, 4.8),
    ],
    ("La Paz", "Bolivia"): [
        ("Mi Teleférico Cable Car System (World's Highest Transit)", "viewpoint", 100.00, 5.0),
        ("Witches' Market (Mercado de las Brujas)", "market", 0.00, 4.7),
        ("Valley of the Moon (Valle de la Luna Clay Spires)", "nature", 150.00, 4.6),
        ("Death Road (Yungas Road) World-Famous Mountain Biking", "adventure", 5500.00, 5.0),
        ("Salar de Uyuni Giant Salt Flats Multi-Day Excursion", "nature", 16000.00, 5.0),
    ],
}
