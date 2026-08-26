"""Exports SQL seed files for Hotels, Restaurants, and Transport Options for Supabase SQL Editor."""
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
seeds_dir = project_root / "database" / "seeds"

def generate_hotels_sql():
    hotels_file = seeds_dir / "hotels_master_d3.json"
    if not hotels_file.exists():
        return
    with open(hotels_file, "r", encoding="utf-8") as f:
        hotels = json.load(f)
    
    lines = [
        "-- RoamGenie D3 Hotels Dataset Seed (6,000 records)",
        "BEGIN;",
    ]
    for h in hotels:
        name_esc = h["name"].replace("'", "''")
        price = h["price_per_night"]
        rating = f"{h['rating']:.1f}" if h["rating"] is not None else "NULL"
        lines.append(
            f"INSERT INTO hotels (id, destination_id, name, price_per_night, rating) OVERRIDING SYSTEM VALUE "
            f"VALUES ({h['id']}, {h['destination_id']}, '{name_esc}', {price:.2f}, {rating}) "
            f"ON CONFLICT (destination_id, name) DO NOTHING;"
        )
    lines.append("COMMIT;")
    
    out_file = seeds_dir / "003_seed_hotels.sql"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated {out_file.name} ({len(hotels)} records, {out_file.stat().st_size / 1024:.1f} KB)")


def generate_restaurants_sql():
    rests_file = seeds_dir / "restaurants_master_d4.json"
    if not rests_file.exists():
        return
    with open(rests_file, "r", encoding="utf-8") as f:
        restaurants = json.load(f)
    
    lines = [
        "-- RoamGenie D4 Restaurants Dataset Seed (6,000 records)",
        "BEGIN;",
    ]
    for r in restaurants:
        name_esc = r["name"].replace("'", "''")
        cuisine_esc = f"'{r['cuisine'].replace("'", "''")}'" if r.get("cuisine") else "NULL"
        cost = r["average_cost_per_person"]
        cost_str = f"{cost:.2f}" if cost is not None else "NULL"
        rating = f"{r['rating']:.1f}" if r.get("rating") is not None else "NULL"
        lines.append(
            f"INSERT INTO restaurants (id, destination_id, name, cuisine, average_cost_per_person, rating) OVERRIDING SYSTEM VALUE "
            f"VALUES ({r['id']}, {r['destination_id']}, '{name_esc}', {cuisine_esc}, {cost_str}, {rating}) "
            f"ON CONFLICT (destination_id, name) DO NOTHING;"
        )
    lines.append("COMMIT;")
    
    out_file = seeds_dir / "004_seed_restaurants.sql"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated {out_file.name} ({len(restaurants)} records, {out_file.stat().st_size / 1024:.1f} KB)")


def generate_transports_sql():
    trans_file = seeds_dir / "transport_master_d5.json"
    if not trans_file.exists():
        return
    with open(trans_file, "r", encoding="utf-8") as f:
        transports = json.load(f)
    
    lines = [
        "-- RoamGenie D5 Transport Options Dataset Seed (6,000 records)",
        "BEGIN;",
    ]
    for t in transports:
        orig_esc = t["origin"].replace("'", "''")
        mode_esc = t["mode"].replace("'", "''")
        prov_esc = f"'{t['provider'].replace("'", "''")}'" if t.get("provider") else "NULL"
        cost = t["estimated_cost"]
        dur = t["duration_minutes"] if t.get("duration_minutes") is not None else "NULL"
        lines.append(
            f"INSERT INTO transport_options (id, destination_id, origin, mode, provider, estimated_cost, duration_minutes) OVERRIDING SYSTEM VALUE "
            f"VALUES ({t['id']}, {t['destination_id']}, '{orig_esc}', '{mode_esc}', {prov_esc}, {cost:.2f}, {dur}) "
            f"ON CONFLICT DO NOTHING;"
        )
    lines.append("COMMIT;")
    
    out_file = seeds_dir / "005_seed_transports.sql"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated {out_file.name} ({len(transports)} records, {out_file.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    generate_hotels_sql()
    generate_restaurants_sql()
    generate_transports_sql()
