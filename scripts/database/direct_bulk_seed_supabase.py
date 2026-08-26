"""Direct bulk seeder for Restaurants and Transport Options into Supabase."""
import json
import logging
from pathlib import Path
import psycopg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bulk_seed")

project_root = Path(__file__).resolve().parent.parent.parent
seeds_dir = project_root / "database" / "seeds"

DB_URL = "postgresql://postgres:PERRY1102YASMIN@db.nacsaikbracbdsouaybk.supabase.co:5432/postgres"

def seed_restaurants_bulk():
    rests_file = seeds_dir / "restaurants_master_d4.json"
    with open(rests_file, "r", encoding="utf-8") as f:
        restaurants = json.load(f)

    logger.info("Connecting to Supabase to seed %d restaurants...", len(restaurants))
    with psycopg.connect(DB_URL, connect_timeout=15) as conn:
        with conn.cursor() as cur:
            # Check existing keys
            cur.execute("SELECT destination_id, LOWER(name) FROM restaurants;")
            existing = set(cur.fetchall())
            logger.info("Found %d existing restaurant records in Supabase.", len(existing))

            to_insert = [
                (
                    r["destination_id"],
                    r["name"],
                    r.get("cuisine"),
                    r.get("average_cost_per_person"),
                    r.get("rating"),
                )
                for r in restaurants
                if (r["destination_id"], r["name"].strip().lower()) not in existing
            ]
            logger.info("Prepared %d new restaurant records to insert.", len(to_insert))

            if to_insert:
                query = """
                    INSERT INTO restaurants (destination_id, name, cuisine, average_cost_per_person, rating)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (destination_id, name) DO NOTHING;
                """
                # Batch in chunks of 500 for high speed and reliability
                chunk_size = 500
                for i in range(0, len(to_insert), chunk_size):
                    chunk = to_insert[i:i + chunk_size]
                    cur.executemany(query, chunk)
                    conn.commit()
                    logger.info("Inserted %d/%d restaurants...", min(i + chunk_size, len(to_insert)), len(to_insert))

            cur.execute("SELECT COUNT(*) FROM restaurants;")
            total = cur.fetchone()[0]
            logger.info("Successfully seeded restaurants! Total in Supabase: %d", total)


def seed_transports_bulk():
    trans_file = seeds_dir / "transport_master_d5.json"
    with open(trans_file, "r", encoding="utf-8") as f:
        transports = json.load(f)

    logger.info("Connecting to Supabase to seed %d transport options...", len(transports))
    with psycopg.connect(DB_URL, connect_timeout=15) as conn:
        with conn.cursor() as cur:
            # Check existing keys
            cur.execute("SELECT destination_id, LOWER(origin), LOWER(mode), LOWER(COALESCE(provider, '')) FROM transport_options;")
            existing = set(cur.fetchall())
            logger.info("Found %d existing transport records in Supabase.", len(existing))

            to_insert = [
                (
                    t["destination_id"],
                    t["origin"],
                    t["mode"],
                    t.get("provider"),
                    t.get("estimated_cost"),
                    t.get("duration_minutes"),
                )
                for t in transports
                if (
                    t["destination_id"],
                    t["origin"].strip().lower(),
                    t["mode"].strip().lower(),
                    (t.get("provider") or "").strip().lower(),
                ) not in existing
            ]
            logger.info("Prepared %d new transport records to insert.", len(to_insert))

            if to_insert:
                query = """
                    INSERT INTO transport_options (destination_id, origin, mode, provider, estimated_cost, duration_minutes)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                chunk_size = 500
                for i in range(0, len(to_insert), chunk_size):
                    chunk = to_insert[i:i + chunk_size]
                    cur.executemany(query, chunk)
                    conn.commit()
                    logger.info("Inserted %d/%d transport options...", min(i + chunk_size, len(to_insert)), len(to_insert))

            cur.execute("SELECT COUNT(*) FROM transport_options;")
            total = cur.fetchone()[0]
            logger.info("Successfully seeded transport options! Total in Supabase: %d", total)


if __name__ == "__main__":
    seed_restaurants_bulk()
    seed_transports_bulk()
