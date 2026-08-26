"""Attraction Master Dataset Seeder (Phase D2)
Populates the attractions table with ~2,500 authentic attractions mapped to the 500 destinations in Supabase PostgreSQL.
"""
import argparse
import json
import logging
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

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

# Import curated master attraction catalog
from scripts.database.attractions_data import MASTER_ATTRACTIONS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_attractions_d2")

RANDOM_SEED = 20260820


def validate_dataset_in_memory() -> Dict[str, Any]:
    """Pre-insertion validation of the in-memory master attraction dataset."""
    errors = []
    total_attractions = 0
    categories = set()
    fees = []
    ratings = []

    for (city, country), att_list in MASTER_ATTRACTIONS.items():
        if not city or len(city) > 100:
            errors.append(f"Invalid city: '{city}'")
        if not country or len(country) > 100:
            errors.append(f"Invalid country: '{country}'")
        if len(att_list) < 3:
            errors.append(f"Destination ({city}, {country}) has only {len(att_list)} attractions (minimum 3 required)")

        seen_names: Set[str] = set()
        for item in att_list:
            total_attractions += 1
            name, cat, fee, rating = item
            if not name or len(name) > 150:
                errors.append(f"Invalid attraction name in ({city}, {country}): '{name}'")
            name_lower = name.lower().strip()
            if name_lower in seen_names:
                errors.append(f"Duplicate attraction name in ({city}, {country}): '{name}'")
            seen_names.add(name_lower)

            if cat:
                if len(cat) > 60:
                    errors.append(f"Category too long for '{name}': '{cat}'")
                categories.add(cat)

            if fee is None or fee < 0:
                errors.append(f"Invalid entry fee for '{name}': {fee}")
            else:
                fees.append(fee)

            if rating is not None:
                if rating < 0 or rating > 5.0:
                    errors.append(f"Invalid rating for '{name}': {rating}")
                ratings.append(rating)

    if errors:
        raise ValueError(f"In-memory dataset validation failed with {len(errors)} errors:\n" + "\n".join(errors[:10]))

    logger.info(
        "In-memory dataset validated: %d attractions across %d destinations (%d categories).",
        total_attractions,
        len(MASTER_ATTRACTIONS),
        len(categories),
    )
    return {
        "destinations_count": len(MASTER_ATTRACTIONS),
        "total_attractions": total_attractions,
        "categories_count": len(categories),
        "min_fee": min(fees) if fees else 0,
        "max_fee": max(fees) if fees else 0,
        "min_rating": min(ratings) if ratings else 0,
        "max_rating": max(ratings) if ratings else 0,
    }


def seed_attractions(dry_run: bool = False) -> Dict[str, Any]:
    """Seeds the attractions table in PostgreSQL from live destinations."""
    validate_dataset_in_memory()

    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine could not be initialized. Check DATABASE_URL in backend/.env.")

    with Session(engine) as session:
        # Read live destinations from PostgreSQL
        dest_rows = session.execute(
            select(Destination.id, Destination.city, Destination.country)
        ).all()

        if not dest_rows:
            raise RuntimeError("No destinations found in database! D1 master destinations must exist first.")

        dest_map: Dict[Tuple[str, str], int] = {
            (d.city.strip().lower(), d.country.strip().lower()): d.id
            for d in dest_rows
        }
        logger.info("Found %d destination records in live database.", len(dest_map))

        # Check existing attractions in DB
        existing_att_rows = session.execute(
            select(Attraction.id, Attraction.destination_id, func.lower(Attraction.name))
        ).all()
        existing_keys: Set[Tuple[int, str]] = {
            (r[1], r[2].strip().lower()) for r in existing_att_rows
        }
        logger.info("Database currently contains %d attraction records.", len(existing_keys))

        to_insert: List[Attraction] = []
        skipped_count = 0

        for (city, country), att_list in MASTER_ATTRACTIONS.items():
            dest_key = (city.strip().lower(), country.strip().lower())
            if dest_key not in dest_map:
                raise RuntimeError(f"Destination ({city}, {country}) not found in live database!")

            dest_id = dest_map[dest_key]

            for name, cat, fee, rating in att_list:
                att_key = (dest_id, name.strip().lower())
                if att_key in existing_keys:
                    skipped_count += 1
                    continue

                att_obj = Attraction(
                    destination_id=dest_id,
                    name=name.strip(),
                    category=cat.strip() if cat else None,
                    entry_fee=Decimal(str(fee)),
                    rating=Decimal(str(rating)) if rating is not None else None,
                )
                to_insert.append(att_obj)

        logger.info(
            "Prepared %d new attractions to insert (skipped %d existing).",
            len(to_insert),
            skipped_count,
        )

        if dry_run:
            logger.info("[DRY RUN] Would insert %d attractions, skipped %d.", len(to_insert), skipped_count)
            return {
                "success": True,
                "dry_run": True,
                "would_insert": len(to_insert),
                "skipped": skipped_count,
                "initial_count": len(existing_keys),
                "projected_total": len(existing_keys) + len(to_insert),
            }

        # Execute insertion in transaction
        logger.info("Inserting %d new attraction records into PostgreSQL...", len(to_insert))
        session.add_all(to_insert)
        session.commit()

        # Verify final count
        final_count = session.execute(select(func.count(Attraction.id))).scalar()
        logger.info("Seeding completed successfully! Total attractions in DB: %d.", final_count)

        # Export full attractions dataset to JSON for repository artifacts
        export_path = Path(__file__).resolve().parent.parent.parent / "database" / "seeds" / "attractions_master_d2.json"
        export_master_json(session, export_path)

        return {
            "success": True,
            "dry_run": False,
            "initial_count": len(existing_keys),
            "inserted_count": len(to_insert),
            "skipped_count": skipped_count,
            "final_count": final_count,
        }


def export_master_json(session: Session, export_file: Path) -> None:
    """Exports all attraction records from PostgreSQL to a clean JSON seed file."""
    stmt = (
        select(
            Attraction.id,
            Attraction.destination_id,
            Attraction.name,
            Attraction.category,
            Attraction.entry_fee,
            Attraction.rating,
            Destination.city,
            Destination.country,
        )
        .join(Destination, Attraction.destination_id == Destination.id)
        .order_by(Attraction.id)
    )
    records = session.execute(stmt).all()

    data = [
        {
            "id": r.id,
            "destination_id": r.destination_id,
            "city": r.city,
            "country": r.country,
            "name": r.name,
            "category": r.category,
            "entry_fee": float(r.entry_fee),
            "rating": float(r.rating) if r.rating is not None else None,
        }
        for r in records
    ]

    export_file.parent.mkdir(parents=True, exist_ok=True)
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("Exported master attraction seed dataset to %s", export_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed attractions dataset (Phase D2)")
    parser.add_argument("--dry-run", action="store_true", help="Perform validation without database writes")
    args = parser.parse_args()

    result = seed_attractions(dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
