"""Destination Master Dataset Validator (Phase D1)
Performs comprehensive data-quality, integrity, and realism checks against the live database.
"""
import json
import logging
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List

# Set up project path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

backend_env_file = backend_dir / ".env"
if backend_env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(backend_env_file)

from app.db.models.catalogue import Destination
from app.db.session import get_engine
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("validate_destinations_d1")

PRESERVED_RECORDS = [
    (1, "Mysuru", "India"),
    (2, "Kochi", "India"),
    (3, "Jaipur", "India"),
    (4, "Udaipur", "India"),
    (5, "Goa", "India"),
]

PLACEHOLDER_REGEX = re.compile(r"\b(test|placeholder|city\s*001|randomville|unknown\s+destination|fake\s+city|fake\s+country)\b", re.IGNORECASE)


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
        total_destinations = session.execute(select(func.count(Destination.id))).scalar()
        results["metrics"]["total_destinations"] = total_destinations
        total_ok = 490 <= total_destinations <= 510
        results["checks"]["count_within_target"] = {
            "passed": total_ok,
            "count": total_destinations,
            "target": 500,
        }
        if not total_ok:
            results["issues"].append(f"Total count {total_destinations} is outside target range [490, 510]")
            results["status"] = "FAIL"

        # 2. Duplicate check
        dup_stmt = (
            select(func.lower(Destination.city), func.lower(Destination.country), func.count(Destination.id))
            .group_by(func.lower(Destination.city), func.lower(Destination.country))
            .having(func.count(Destination.id) > 1)
        )
        duplicates = session.execute(dup_stmt).all()
        results["checks"]["no_duplicates"] = {
            "passed": len(duplicates) == 0,
            "duplicate_count": len(duplicates),
        }
        if duplicates:
            results["issues"].append(f"Found {len(duplicates)} duplicate (city, country) pairs: {duplicates}")
            results["status"] = "FAIL"

        # 3. NULL / Empty mandatory fields check
        null_stmt = select(Destination).where(
            (Destination.city == None)  # noqa: E711
            | (Destination.city == "")
            | (Destination.country == None)  # noqa: E711
            | (Destination.country == "")
            | (Destination.description == None)  # noqa: E711
            | (Destination.active == None)  # noqa: E711
        )
        null_rows = session.execute(null_stmt).scalars().all()
        results["checks"]["no_null_or_empty_fields"] = {
            "passed": len(null_rows) == 0,
            "violating_rows": len(null_rows),
        }
        if null_rows:
            results["issues"].append(f"Found {len(null_rows)} rows with NULL or empty mandatory fields")
            results["status"] = "FAIL"

        # 4. Placeholder / Fake data check
        all_destinations = session.execute(select(Destination).order_by(Destination.id)).scalars().all()
        placeholder_hits = []
        for d in all_destinations:
            if PLACEHOLDER_REGEX.search(d.city) or PLACEHOLDER_REGEX.search(d.country) or PLACEHOLDER_REGEX.search(d.description):
                placeholder_hits.append((d.id, d.city, d.country))

        results["checks"]["no_placeholders"] = {
            "passed": len(placeholder_hits) == 0,
            "placeholder_hits": placeholder_hits,
        }
        if placeholder_hits:
            results["issues"].append(f"Found {len(placeholder_hits)} potential placeholder records: {placeholder_hits}")
            results["status"] = "FAIL"

        # 5. Cost validity check
        invalid_costs = []
        costs = []
        for d in all_destinations:
            if d.average_daily_cost is None or d.average_daily_cost <= Decimal("0") or d.average_daily_cost > Decimal("100000"):
                invalid_costs.append((d.id, d.city, d.country, str(d.average_daily_cost)))
            else:
                costs.append(float(d.average_daily_cost))

        results["checks"]["costs_valid_and_reasonable"] = {
            "passed": len(invalid_costs) == 0,
            "invalid_cost_count": len(invalid_costs),
            "min_cost": min(costs) if costs else 0,
            "max_cost": max(costs) if costs else 0,
            "avg_cost": round(sum(costs) / len(costs), 2) if costs else 0,
        }
        results["metrics"]["min_daily_cost"] = min(costs) if costs else 0
        results["metrics"]["max_daily_cost"] = max(costs) if costs else 0
        results["metrics"]["avg_daily_cost"] = round(sum(costs) / len(costs), 2) if costs else 0

        if invalid_costs:
            results["issues"].append(f"Found {len(invalid_costs)} invalid/unreasonable costs: {invalid_costs[:5]}")
            results["status"] = "FAIL"

        # 6. Preserved records check
        preserved_check = []
        for orig_id, city, country in PRESERVED_RECORDS:
            dest = session.get(Destination, orig_id)
            if dest and dest.city.lower() == city.lower() and dest.country.lower() == country.lower():
                preserved_check.append({"id": orig_id, "city": city, "country": country, "preserved": True})
            else:
                preserved_check.append({"id": orig_id, "city": city, "country": country, "preserved": False})
                results["issues"].append(f"Preserved destination ID={orig_id} ({city}, {country}) is missing or corrupted")
                results["status"] = "FAIL"

        results["checks"]["preserved_original_records"] = {
            "passed": all(p["preserved"] for p in preserved_check),
            "details": preserved_check,
        }

        # 7. Unrelated tables safety check
        table_counts = {}
        for tbl in ["users", "hotels", "restaurants", "attractions", "transport_options", "trips", "itineraries", "weather_snapshots", "reviews"]:
            cnt = session.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            table_counts[tbl] = cnt
        results["metrics"]["unrelated_table_counts"] = table_counts

        # 8. Country and Regional distribution
        country_counts_res = (
            session.execute(
                select(Destination.country, func.count(Destination.id))
                .group_by(Destination.country)
                .order_by(func.count(Destination.id).desc())
            ).all()
        )
        country_dist = {country: count for country, count in country_counts_res}
        results["metrics"]["unique_countries"] = len(country_dist)
        results["metrics"]["country_distribution_top_10"] = dict(list(country_dist.items())[:10])
        results["metrics"]["country_distribution_all"] = country_dist

        # Regional aggregation
        def categorize_region(country: str) -> str:
            c = country.strip().lower()
            if c == "india":
                return "India"
            elif c in ["japan", "south korea", "china", "hong kong", "macau", "taiwan", "thailand", "vietnam", "indonesia", "malaysia", "singapore", "philippines", "cambodia", "laos", "myanmar", "sri lanka", "maldives", "nepal", "bhutan"]:
                return "Southeast & East Asia / South Asia"
            elif c in ["united kingdom", "ireland", "france", "italy", "spain", "portugal", "germany", "switzerland", "austria", "netherlands", "belgium", "denmark", "sweden", "norway", "finland", "iceland", "czech republic", "hungary", "poland", "slovakia", "romania", "croatia", "slovenia", "estonia", "latvia", "lithuania", "bulgaria", "serbia", "greece"]:
                return "Europe"
            elif c in ["united states", "canada", "mexico", "cuba", "costa rica", "panama", "guatemala", "puerto rico"]:
                return "North & Central America"
            elif c in ["peru", "brazil", "argentina", "chile", "colombia", "ecuador", "bolivia"]:
                return "South America"
            elif c in ["united arab emirates", "saudi arabia", "qatar", "oman", "bahrain", "kuwait", "turkey", "jordan", "israel", "egypt", "morocco"]:
                return "Middle East & North Africa"
            elif c in ["south africa", "kenya", "tanzania", "rwanda", "uganda", "ethiopia", "zimbabwe", "zambia", "namibia", "botswana", "mauritius", "seychelles", "madagascar", "ghana", "senegal"]:
                return "Sub-Saharan Africa & Island Nations"
            elif c in ["australia", "new zealand", "fiji", "french polynesia"]:
                return "Oceania"
            return "Other"

        regional_dist = {}
        for c_name, count in country_dist.items():
            reg = categorize_region(c_name)
            regional_dist[reg] = regional_dist.get(reg, 0) + count
        results["metrics"]["regional_distribution"] = regional_dist

        # 9. Duplicate description check
        desc_counts = (
            session.execute(
                select(Destination.description, func.count(Destination.id))
                .group_by(Destination.description)
                .having(func.count(Destination.id) > 1)
            ).all()
        )
        results["checks"]["no_duplicate_descriptions"] = {
            "passed": len(desc_counts) == 0,
            "duplicate_desc_count": len(desc_counts),
        }
        if desc_counts:
            results["issues"].append(f"Found {len(desc_counts)} duplicate descriptions")
            results["status"] = "FAIL"

    return results


if __name__ == "__main__":
    report = run_validation()
    print(json.dumps(report, indent=2, default=str))
