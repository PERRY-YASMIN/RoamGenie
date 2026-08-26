"""Post-Insert Live Database Verification Script (Phase D2)
Queries the live Supabase PostgreSQL database to strictly verify all 14 post-insert criteria.
"""
import json
import logging
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

# Set up project path
project_root = Path(__file__).resolve().parent.parent.parent
backend_dir = project_root / "backend"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

backend_env_file = backend_dir / ".env"
if backend_env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(backend_env_file)

from app.db.models.catalogue import Attraction, Destination
from app.db.session import get_engine
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("post_insert_verification_d2")

PRESERVED_ATTRACTIONS = [
    (1, 1, "Mysuru Palace"),
    (2, 1, "Chamundi Hill & Temple"),
    (3, 1, "Brindavan Gardens"),
]

ORIGINAL_5_DESTINATIONS = [
    (1, "Mysuru", "India"),
    (2, "Kochi", "India"),
    (3, "Jaipur", "India"),
    (4, "Udaipur", "India"),
    (5, "Goa", "India"),
]

ALL_PROJECT_TABLES = [
    "destinations",
    "attractions",
    "hotels",
    "restaurants",
    "transport_options",
    "users",
    "user_preferences",
    "activity_preferences",
    "trips",
    "trip_members",
    "itineraries",
    "itinerary_days",
    "itinerary_items",
    "expenses",
    "packing_items",
    "saved_trips",
    "reviews",
    "weather_snapshots",
    "ai_conversations",
    "ai_messages",
    "trip_audit",
]

PLACEHOLDER_REGEX = re.compile(
    r"\b(test\s+attraction|placeholder|attraction\s*001|fake\s+attraction|sample\s+museum|generic\s+temple)\b",
    re.IGNORECASE,
)


def run_post_insert_verification() -> Dict[str, Any]:
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine could not be initialized.")

    report = {
        "status": "PASS",
        "verifications": {},
        "failures": [],
        "table_counts": {},
        "summary_metrics": {},
    }

    with Session(engine) as session:
        # Table counts across ALL 21 tables in the schema
        for tbl in ALL_PROJECT_TABLES:
            try:
                cnt = session.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
                report["table_counts"][tbl] = cnt
            except Exception as e:
                report["table_counts"][tbl] = f"Error: {e}"

        # 1. Final attraction count
        total_attractions = session.execute(select(func.count(Attraction.id))).scalar()
        report["verifications"]["1_final_attraction_count"] = {
            "passed": total_attractions == 2517,
            "actual": total_attractions,
            "expected": 2517,
        }
        if total_attractions != 2517:
            report["failures"].append(f"Expected 2,517 attractions, found {total_attractions}")

        # 2. Existing 3 attractions are still present
        preserved_results = []
        for att_id, dest_id, name in PRESERVED_ATTRACTIONS:
            att = session.get(Attraction, att_id)
            if att and att.destination_id == dest_id and att.name.lower() == name.lower():
                preserved_results.append({"id": att_id, "name": name, "status": "preserved"})
            else:
                preserved_results.append({"id": att_id, "name": name, "status": "missing_or_modified"})
        all_preserved = all(r["status"] == "preserved" for r in preserved_results)
        report["verifications"]["2_existing_3_attractions_preserved"] = {
            "passed": all_preserved,
            "details": preserved_results,
        }
        if not all_preserved:
            report["failures"].append("Existing 3 attractions were modified or deleted")

        # 3. All 500 destinations still exist and original 5 intact
        dest_count = session.execute(select(func.count(Destination.id))).scalar()
        orig_5_results = []
        for d_id, city, country in ORIGINAL_5_DESTINATIONS:
            d = session.get(Destination, d_id)
            if d and d.city.lower() == city.lower() and d.country.lower() == country.lower():
                orig_5_results.append({"id": d_id, "city": city, "country": country, "status": "preserved"})
            else:
                orig_5_results.append({"id": d_id, "city": city, "country": country, "status": "missing_or_modified"})
        orig_5_intact = all(r["status"] == "preserved" for r in orig_5_results)
        report["verifications"]["3_all_500_destinations_exist"] = {
            "passed": dest_count == 500 and orig_5_intact,
            "destinations_count": dest_count,
            "original_5_intact": orig_5_intact,
            "original_5_details": orig_5_results,
        }
        if dest_count != 500 or not orig_5_intact:
            report["failures"].append(f"Destination check failed: count={dest_count}, orig_5_intact={orig_5_intact}")

        # 4 & 5. Every attraction has valid destination_id / Zero orphan attractions
        orphan_count = session.execute(
            text("SELECT COUNT(*) FROM attractions a LEFT JOIN destinations d ON a.destination_id = d.id WHERE d.id IS NULL")
        ).scalar()
        report["verifications"]["4_5_zero_orphan_attractions"] = {
            "passed": orphan_count == 0,
            "orphan_count": orphan_count,
        }
        if orphan_count != 0:
            report["failures"].append(f"Found {orphan_count} orphan attractions")

        # 6. Zero duplicate (destination_id, name) pairs
        dup_query = session.execute(
            select(Attraction.destination_id, func.lower(Attraction.name), func.count(Attraction.id))
            .group_by(Attraction.destination_id, func.lower(Attraction.name))
            .having(func.count(Attraction.id) > 1)
        ).all()
        report["verifications"]["6_zero_duplicate_pairs"] = {
            "passed": len(dup_query) == 0,
            "duplicate_count": len(dup_query),
            "duplicates": dup_query,
        }
        if len(dup_query) != 0:
            report["failures"].append(f"Found {len(dup_query)} duplicate attractions")

        # 7 & 8. Zero invalid entry fees and ratings
        all_atts = session.execute(select(Attraction)).scalars().all()
        invalid_fees = [a for a in all_atts if a.entry_fee is None or a.entry_fee < Decimal("0")]
        invalid_ratings = [a for a in all_atts if a.rating is not None and (a.rating < Decimal("0") or a.rating > Decimal("5.0"))]
        report["verifications"]["7_zero_invalid_entry_fees"] = {
            "passed": len(invalid_fees) == 0,
            "invalid_count": len(invalid_fees),
        }
        report["verifications"]["8_zero_invalid_ratings"] = {
            "passed": len(invalid_ratings) == 0,
            "invalid_count": len(invalid_ratings),
        }
        if invalid_fees:
            report["failures"].append(f"Found {len(invalid_fees)} invalid entry fees")
        if invalid_ratings:
            report["failures"].append(f"Found {len(invalid_ratings)} invalid ratings")

        # 9. Zero empty mandatory fields
        null_mandatory = [a for a in all_atts if not a.name or not a.name.strip() or a.destination_id is None or a.entry_fee is None]
        report["verifications"]["9_zero_empty_mandatory_fields"] = {
            "passed": len(null_mandatory) == 0,
            "empty_or_null_count": len(null_mandatory),
        }
        if null_mandatory:
            report["failures"].append(f"Found {len(null_mandatory)} rows with empty mandatory fields")

        # 10. Zero placeholder / test records
        placeholder_hits = [a for a in all_atts if PLACEHOLDER_REGEX.search(a.name) or (a.category and PLACEHOLDER_REGEX.search(a.category))]
        report["verifications"]["10_zero_placeholder_records"] = {
            "passed": len(placeholder_hits) == 0,
            "placeholder_hits": len(placeholder_hits),
        }
        if placeholder_hits:
            report["failures"].append(f"Found {len(placeholder_hits)} placeholder records")

        # 11 & 12. Destination coverage and min/max/avg attraction count
        dest_stats = session.execute(
            select(
                Destination.id,
                Destination.city,
                Destination.country,
                func.count(Attraction.id).label("att_count")
            )
            .outerjoin(Attraction, Destination.id == Attraction.destination_id)
            .group_by(Destination.id, Destination.city, Destination.country)
        ).all()
        zero_cov = [d for d in dest_stats if d.att_count == 0]
        counts = [d.att_count for d in dest_stats]
        covered_count = len(dest_stats) - len(zero_cov)
        min_c = min(counts) if counts else 0
        max_c = max(counts) if counts else 0
        avg_c = round(sum(counts) / len(counts), 2) if counts else 0
        report["verifications"]["11_12_destination_coverage_and_distribution"] = {
            "passed": len(zero_cov) == 0 and covered_count == 500,
            "destinations_covered": f"{covered_count}/500",
            "zero_coverage_destinations": len(zero_cov),
            "min_per_destination": min_c,
            "max_per_destination": max_c,
            "avg_per_destination": avg_c,
        }
        if zero_cov:
            report["failures"].append(f"Found {len(zero_cov)} destinations with 0 attractions")

        # 13. No unexpected modifications to unrelated tables
        # Baseline expectations from pre-insert:
        # destinations=500, users=3, user_preferences=2, activity_preferences=4, hotels=2, restaurants=2, transport_options=2,
        # trips=1, trip_members=2, itineraries=1, itinerary_days=1, itinerary_items=3, expenses=1, packing_items=1,
        # saved_trips=1, reviews=1, weather_snapshots=1, ai_conversations=0, ai_messages=0, trip_audit=0
        expected_unrelated_counts = {
            "destinations": 500,
            "users": 3,
            "user_preferences": 2,
            "activity_preferences": 4,
            "hotels": 2,
            "restaurants": 2,
            "transport_options": 2,
            "trips": 1,
            "trip_members": 2,
            "itineraries": 1,
            "itinerary_days": 1,
            "itinerary_items": 3,
            "expenses": 1,
            "packing_items": 1,
            "saved_trips": 1,
            "reviews": 1,
            "weather_snapshots": 1,
            "ai_conversations": 0,
            "ai_messages": 0,
            "trip_audit": 0,
        }
        unrelated_mods = []
        for tbl, exp_cnt in expected_unrelated_counts.items():
            act_cnt = report["table_counts"].get(tbl)
            if act_cnt != exp_cnt:
                unrelated_mods.append(f"Table '{tbl}' count mismatch: expected {exp_cnt}, actual {act_cnt}")
        report["verifications"]["13_unrelated_tables_isolated"] = {
            "passed": len(unrelated_mods) == 0,
            "violations": unrelated_mods,
        }
        if unrelated_mods:
            report["failures"].append(f"Unrelated table modifications detected: {unrelated_mods}")

        # Summary Metrics
        fees = [float(a.entry_fee) for a in all_atts if a.entry_fee is not None]
        ratings = [float(a.rating) for a in all_atts if a.rating is not None]
        free_count = sum(1 for f in fees if f == 0.0)
        paid_count = len(fees) - free_count
        categories = {}
        for a in all_atts:
            cat = a.category or "uncategorized"
            categories[cat] = categories.get(cat, 0) + 1

        report["summary_metrics"] = {
            "total_attractions": total_attractions,
            "new_attractions_inserted": total_attractions - len(PRESERVED_ATTRACTIONS),
            "preserved_attractions": len(PRESERVED_ATTRACTIONS),
            "total_destinations": dest_count,
            "free_count": free_count,
            "paid_count": paid_count,
            "free_pct": round((free_count / total_attractions) * 100, 2),
            "paid_pct": round((paid_count / total_attractions) * 100, 2),
            "min_fee_inr": min(fees) if fees else 0,
            "max_fee_inr": max(fees) if fees else 0,
            "avg_fee_inr": round(sum(fees) / len(fees), 2) if fees else 0,
            "min_rating": min(ratings) if ratings else 0,
            "max_rating": max(ratings) if ratings else 0,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "categories_breakdown": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)),
        }

    if report["failures"]:
        report["status"] = "FAIL"

    return report


if __name__ == "__main__":
    rep = run_post_insert_verification()
    print(json.dumps(rep, indent=2, default=str))
