import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models.catalogue import (
    Attraction,
    Destination,
    Hotel,
    Restaurant,
    TransportOption,
)

logger = logging.getLogger("uvicorn.error")


def get_seed_dir() -> Optional[Path]:
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "database" / "seeds",
        Path(__file__).resolve().parent.parent.parent / "database" / "seeds",
        Path(__file__).resolve().parent.parent / "database" / "seeds",
        Path.cwd() / "database" / "seeds",
        Path.cwd().parent / "database" / "seeds",
    ]
    for c in candidates:
        if c.exists() and (c / "hotels_master_d3.json").exists():
            return c
    return None


def _bulk_insert(db: Session, model: Any, records: List[Dict[str, Any]], conflict_cols: Optional[List[str]] = None) -> int:
    if not records:
        return 0
    dialect = db.bind.dialect.name if db.bind else "postgresql"
    inserted = 0

    chunk_size = 500
    for i in range(0, len(records), chunk_size):
        chunk = records[i : i + chunk_size]
        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(model).values(chunk)
            if conflict_cols:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)
            else:
                stmt = stmt.on_conflict_do_nothing()
            res = db.execute(stmt)
            inserted += res.rowcount if res.rowcount and res.rowcount > 0 else len(chunk)
        elif dialect == "sqlite":
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            stmt = sqlite_insert(model).values(chunk)
            if conflict_cols:
                stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)
            else:
                stmt = stmt.on_conflict_do_nothing()
            res = db.execute(stmt)
            inserted += res.rowcount if res.rowcount and res.rowcount > 0 else len(chunk)
        else:
            db.bulk_insert_mappings(model, chunk)
            inserted += len(chunk)

    db.commit()
    return inserted


def get_catalogue_counts(db: Session) -> Dict[str, int]:
    return {
        "destinations": db.execute(select(func.count(Destination.id))).scalar() or 0,
        "hotels": db.execute(select(func.count(Hotel.id))).scalar() or 0,
        "restaurants": db.execute(select(func.count(Restaurant.id))).scalar() or 0,
        "attractions": db.execute(select(func.count(Attraction.id))).scalar() or 0,
        "transport_options": db.execute(select(func.count(TransportOption.id))).scalar() or 0,
    }


def seed_master_catalogues(db: Session, force: bool = False) -> Dict[str, Any]:
    seed_dir = get_seed_dir()
    if not seed_dir:
        logger.warning("Seed directory not found. Master catalogue seeding skipped.")
        return {"status": "error", "message": "Seed directory not found", "counts": get_catalogue_counts(db)}

    # Destination mapping cache
    dests = db.execute(select(Destination.id, Destination.city, Destination.country)).all()
    dest_map = {(d.city.strip().lower(), d.country.strip().lower()): d.id for d in dests}
    dest_id_set = {d.id for d in dests}

    stats: Dict[str, Any] = {}

    # 1. Hotels
    hotel_count = db.execute(select(func.count(Hotel.id))).scalar() or 0
    if hotel_count < 100 or force:
        h_path = seed_dir / "hotels_master_d3.json"
        if h_path.exists():
            with open(h_path, "r", encoding="utf-8") as f:
                raw_hotels = json.load(f)
            records = []
            for h in raw_hotels:
                d_id = dest_map.get((h.get("city", "").strip().lower(), h.get("country", "").strip().lower()))
                if not d_id and h.get("destination_id") in dest_id_set:
                    d_id = h.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "name": h["name"],
                        "price_per_night": Decimal(str(h["price_per_night"])),
                        "rating": Decimal(str(h["rating"])) if h.get("rating") is not None else None,
                    })
            stats["hotels_seeded"] = _bulk_insert(db, Hotel, records, conflict_cols=["destination_id", "name"])
            logger.info("Seeded %d master hotels.", len(records))

    # 2. Restaurants
    rest_count = db.execute(select(func.count(Restaurant.id))).scalar() or 0
    if rest_count < 100 or force:
        r_path = seed_dir / "restaurants_master_d4.json"
        if r_path.exists():
            with open(r_path, "r", encoding="utf-8") as f:
                raw_rests = json.load(f)
            records = []
            for r in raw_rests:
                d_id = dest_map.get((r.get("city", "").strip().lower(), r.get("country", "").strip().lower()))
                if not d_id and r.get("destination_id") in dest_id_set:
                    d_id = r.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "name": r["name"],
                        "cuisine": r.get("cuisine"),
                        "average_cost_per_person": Decimal(str(r["average_cost_per_person"])) if r.get("average_cost_per_person") is not None else None,
                        "rating": Decimal(str(r["rating"])) if r.get("rating") is not None else None,
                    })
            stats["restaurants_seeded"] = _bulk_insert(db, Restaurant, records, conflict_cols=["destination_id", "name"])
            logger.info("Seeded %d master restaurants.", len(records))

    # 3. Attractions
    attr_count = db.execute(select(func.count(Attraction.id))).scalar() or 0
    if attr_count < 100 or force:
        a_path = seed_dir / "attractions_master_d2.json"
        if a_path.exists():
            with open(a_path, "r", encoding="utf-8") as f:
                raw_attrs = json.load(f)
            records = []
            for a in raw_attrs:
                d_id = dest_map.get((a.get("city", "").strip().lower(), a.get("country", "").strip().lower()))
                if not d_id and a.get("destination_id") in dest_id_set:
                    d_id = a.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "name": a["name"],
                        "category": a.get("category"),
                        "entry_fee": Decimal(str(a.get("entry_fee", 0))),
                        "rating": Decimal(str(a["rating"])) if a.get("rating") is not None else None,
                    })
            stats["attractions_seeded"] = _bulk_insert(db, Attraction, records, conflict_cols=["destination_id", "name"])
            logger.info("Seeded %d master attractions.", len(records))

    # 4. Transport Options
    trans_count = db.execute(select(func.count(TransportOption.id))).scalar() or 0
    if trans_count < 100 or force:
        t_path = seed_dir / "transport_master_d5.json"
        if t_path.exists():
            with open(t_path, "r", encoding="utf-8") as f:
                raw_trans = json.load(f)
            records = []
            for t in raw_trans:
                d_id = dest_map.get((t.get("city", "").strip().lower(), t.get("country", "").strip().lower()))
                if not d_id and t.get("destination_id") in dest_id_set:
                    d_id = t.get("destination_id")
                if d_id:
                    records.append({
                        "destination_id": d_id,
                        "origin": t["origin"],
                        "mode": t["mode"],
                        "provider": t.get("provider"),
                        "estimated_cost": Decimal(str(t["estimated_cost"])),
                        "duration_minutes": int(t["duration_minutes"]) if t.get("duration_minutes") is not None else None,
                    })
            stats["transport_seeded"] = _bulk_insert(db, TransportOption, records)
            logger.info("Seeded %d master transport options.", len(records))

    stats["counts"] = get_catalogue_counts(db)
    stats["status"] = "ok"
    return stats
