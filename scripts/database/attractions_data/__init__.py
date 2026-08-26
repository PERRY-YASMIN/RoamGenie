"""Attractions Master Dataset Provider for RoamGenie Phase D2.
Aggregates authentic attractions mapped across all 500 destinations.
"""
from typing import Dict, List, Tuple

from scripts.database.attractions_data.africa import AFRICA_ATTRACTIONS
from scripts.database.attractions_data.asia import ASIA_ATTRACTIONS
from scripts.database.attractions_data.europe import EUROPE_ATTRACTIONS
from scripts.database.attractions_data.india import INDIA_ATTRACTIONS
from scripts.database.attractions_data.middle_east import MIDDLE_EAST_ATTRACTIONS
from scripts.database.attractions_data.north_america import NORTH_AMERICA_ATTRACTIONS
from scripts.database.attractions_data.oceania import OCEANIA_ATTRACTIONS
from scripts.database.attractions_data.south_america import SOUTH_AMERICA_ATTRACTIONS

# Master dictionary: (city, country) -> List[(name, category, entry_fee_inr, rating)]
MASTER_ATTRACTIONS: Dict[Tuple[str, str], List[Tuple[str, str, float, float]]] = {}

for sub_dict in [
    INDIA_ATTRACTIONS,
    EUROPE_ATTRACTIONS,
    ASIA_ATTRACTIONS,
    NORTH_AMERICA_ATTRACTIONS,
    AFRICA_ATTRACTIONS,
    MIDDLE_EAST_ATTRACTIONS,
    SOUTH_AMERICA_ATTRACTIONS,
    OCEANIA_ATTRACTIONS,
]:
    for key, items in sub_dict.items():
        MASTER_ATTRACTIONS[key] = items
