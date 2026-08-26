"""Attraction Master Dataset Validator (Phase D2)
Performs comprehensive referential integrity, quality, distribution, and preservation checks against the live database.
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
logger = logging.getLogger("validate_attractions_d2")

PRESERVED_ATTRACTIONS = [
    (1, 1, "Mysuru Palace"),
    (2, 1, "Chamundi Hill & Temple"),
    (3, 1, "Brindavan Gardens"),
]

PLACEHOLDER_REGEX = re.compile(
    r"\b(test\s+attraction|placeholder|attraction\s*001|fake\s+attraction|sample\s+museum|generic\s+temple)\b",
    re.IGNORECASE,
)


def run_validation() -> Dict[str, Any]:
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine could not be initialized.")

    results = {
        "status": "PASS",
        "checks": {},
        "issues": [],
        "metrics": {},
    }

    with Session(engine) as session:
        # 1. Total count check
        total_attractions = session.execute(select(func.count(Attraction.id))).scalar()
        results["metrics"]["total_attractions"] = total_attractions
        count_ok = 2400 <= total_attractions <= 2650
        results["checks"]["count_within_target"] = {
            "passed": count_ok,
            "count": total_attractions,
            "target": 2500,
        }
        if not count_ok:
            results["issues"].append(f"Total attractions count {total_attractions} outside target range [2400, 2650]")
            results["status"] = "FAIL"

        # 2. Referential integrity (Orphans check)
        orphan_query = text(
            "SELECT COUNT(*) FROM attractions a LEFT JOIN destinations d ON a.destination_id = d.id WHERE d.id IS NULL"
        )
        orphan_count = session.execute(orphan_query).scalar()
        results["checks"]["referential_integrity"] = {
            "passed": orphan_count == 0,
            "orphan_attractions": orphan_count,
        }
        if orphan_count > 0:
            results["issues"].append(f"Found {orphan_count} orphan attractions with no matching destination!")
            results["status"] = "FAIL"

        # 3. Duplicate check (destination_id, name)
        dup_stmt = (
            select(Attraction.destination_id, func.lower(Attraction.name), func.count(Attraction.id))
            .group_by(Attraction.destination_id, func.lower(Attraction.name))
            .having(func.count(Attraction.id) > 1)
        )
        duplicates = session.execute(dup_stmt).all()
        results["checks"]["no_duplicates"] = {
            "passed": len(duplicates) == 0,
            "duplicate_count": len(duplicates),
        }
        if duplicates:
            results["issues"].append(f"Found {len(duplicates)} duplicate (destination_id, name) pairs: {duplicates}")
            results["status"] = "FAIL"

        # 4. Mandatory non-null / empty fields check
        null_stmt = select(Attraction).where(
            (Attraction.destination_id == None)  # noqa: E711
            | (Attraction.name == None)  # noqa: E711
            | (Attraction.name == "")
            | (Attraction.entry_fee == None)  # noqa: E711
        )
        null_rows = session.execute(null_stmt).scalars().all()
        results["checks"]["no_null_mandatory_fields"] = {
            "passed": len(null_rows) == 0,
            "violating_rows": len(null_rows),
        }
        if null_rows:
            results["issues"].append(f"Found {len(null_rows)} rows with NULL mandatory fields")
            results["status"] = "FAIL"

        # 5. Entry fees and ratings validity
        all_attractions = session.execute(select(Attraction).order_by(Attraction.id)).scalars().all()
        invalid_fees = []
        invalid_ratings = []
        free_count = 0
        paid_count = 0
        fees = []
        ratings = []
        categories: Dict[str, int] = {}
        placeholder_hits = []

        for a in all_attractions:
            # Check placeholder
            if PLACEHOLDER_REGEX.search(a.name) or (a.category and PLACEHOLDER_REGEX.search(a.category)):
                placeholder_hits.append((a.id, a.destination_id, a.name))

            # Check fee
            if a.entry_fee is None or a.entry_fee < Decimal("0"):
                invalid_fees.append((a.id, a.name, str(a.entry_fee)))
            else:
                fee_val = float(a.entry_fee)
                fees.append(fee_val)
                if fee_val == 0.0:
                    free_count += 1
                else:
                    paid_count += 1

            # Check rating
            if a.rating is not None:
                if a.rating < Decimal("0") or a.rating > Decimal("5.0"):
                    invalid_ratings.append((a.id, a.name, str(a.rating)))
                else:
                    ratings.append(float(a.rating))

            # Category
            cat = a.category or "uncategorized"
            categories[cat] = categories.get(cat, 0) + 1

        results["checks"]["no_placeholders"] = {
            "passed": len(placeholder_hits) == 0,
            "placeholder_hits": placeholder_hits,
        }
        if placeholder_hits:
            results["issues"].append(f"Found {len(placeholder_hits)} placeholder records: {placeholder_hits}")
            results["status"] = "FAIL"

        results["checks"]["entry_fees_valid"] = {
            "passed": len(invalid_fees) == 0,
            "invalid_fees_count": len(invalid_fees),
            "free_count": free_count,
            "paid_count": paid_count,
            "min_fee": min(fees) if fees else 0,
            "max_fee": max(fees) if fees else 0,
            "avg_fee": round(sum(fees) / len(fees), 2) if fees else 0,
        }
        if invalid_fees:
            results["issues"].append(f"Found {len(invalid_fees)} invalid entry fees: {invalid_fees[:5]}")
            results["status"] = "FAIL"

        results["checks"]["ratings_valid"] = {
            "passed": len(invalid_ratings) == 0,
            "invalid_ratings_count": len(invalid_ratings),
            "min_rating": min(ratings) if ratings else 0,
            "max_rating": max(ratings) if ratings else 0,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
        }
        if invalid_ratings:
            results["issues"].append(f"Found {len(invalid_ratings)} invalid ratings: {invalid_ratings[:5]}")
            results["status"] = "FAIL"

        # 6. Preserved records check
        preserved_check = []
        for att_id, dest_id, name in PRESERVED_ATTRACTIONS:
            att = session.get(Attraction, att_id)
            if att and att.destination_id == dest_id and att.name.lower() == name.lower():
                preserved_check.append({"id": att_id, "name": name, "preserved": True})
            else:
                preserved_check.append({"id": att_id, "name": name, "preserved": False})
                results["issues"].append(f"Preserved attraction ID={att_id} ('{name}') missing or corrupted")
                results["status"] = "FAIL"

        results["checks"]["preserved_original_records"] = {
            "passed": all(p["preserved"] for p in preserved_check),
            "details": preserved_check,
        }

        # 7. Destination coverage analysis
        dest_counts_res = session.execute(
            select(
                Destination.id,
                Destination.city,
                Destination.country,
                func.count(Attraction.id).label("att_count"),
            )
            .outerjoin(Attraction, Destination.id == Attraction.destination_id)
            .group_by(Destination.id, Destination.city, Destination.country)
            .order_by(func.count(Attraction.id).asc())
        ).all()

        zero_coverage = [d for d in dest_counts_res if d.att_count == 0]
        att_counts_per_dest = [d.att_count for d in dest_counts_res]

        results["checks"]["destination_coverage"] = {
            "passed": len(zero_coverage) == 0 and len(dest_counts_res) == 500,
            "total_destinations": len(dest_counts_res),
            "destinations_with_zero_attractions": len(zero_coverage),
            "min_attractions_per_destination": min(att_counts_per_dest) if att_counts_per_dest else 0,
            "max_attractions_per_destination": max(att_counts_per_dest) if att_counts_per_dest else 0,
            "avg_attractions_per_destination": round(sum(att_counts_per_dest) / len(att_counts_per_dest), 2) if att_counts_per_dest else 0,
        }
        if zero_coverage:
            results["issues"].append(f"Found {len(zero_coverage)} destinations with 0 attractions: {[d.city for d in zero_coverage[:5]]}")
            results["status"] = "FAIL"

        # 8. D1 Preservation check
        total_destinations = session.execute(select(func.count(Destination.id))).scalar()
        results["checks"]["d1_destinations_preserved"] = {
            "passed": total_destinations == 500,
            "destinations_count": total_destinations,
        }
        if total_destinations != 500:
            results["issues"].append(f"Destinations count changed from 500 to {total_destinations}")
            results["status"] = "FAIL"

        # 9. Unrelated tables safety check
        table_counts = {}
        for tbl in ["users", "hotels", "restaurants", "transport_options", "trips", "itineraries", "weather_snapshots", "reviews"]:
            cnt = session.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            table_counts[tbl] = cnt
        results["metrics"]["unrelated_table_counts"] = table_counts

        # 10. Metrics compilation
        results["metrics"]["category_distribution"] = dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))
        results["metrics"]["pricing_breakdown"] = {
            "free_count": free_count,
            "paid_count": paid_count,
            "free_percentage": round((free_count / total_attractions) * 100, 1) if total_attractions else 0,
            "paid_percentage": round((paid_count / total_attractions) * 100, 1) if total_attractions else 0,
            "min_fee_inr": min(fees) if fees else 0,
            "max_fee_inr": max(fees) if fees else 0,
            "avg_fee_inr": round(sum(fees) / len(fees), 2) if fees else 0,
        }
        results["metrics"]["rating_distribution"] = {
            "min_rating": min(ratings) if ratings else 0,
            "max_rating": max(ratings) if ratings else 0,
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "rated_count": len(ratings),
        }

    return results


if __name__ == "__main__":
    report = run_validation()
    print(json.dumps(report, indent=2, default=str))
