import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv

backend_env = backend_dir / ".env"
if backend_env.exists():
    load_dotenv(backend_env)

from app.db.session import get_engine
from sqlalchemy import text

engine = get_engine()
if engine is None:
    raise RuntimeError("Failed to create engine. Please check backend/.env configuration.")

with engine.connect() as conn:
    print("==================================================")
    print("LIVE DATABASE AUDIT REPORT")
    print("==================================================")
    
    # 1. Tables & Row Counts
    tables_result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)).fetchall()
    
    table_names = [t[0] for t in tables_result]
    print(f"\nFound {len(table_names)} Base Tables:")
    
    table_counts = {}
    total_records = 0
    for tname in table_names:
        try:
            cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{tname}"')).scalar()
            table_counts[tname] = cnt
            total_records += cnt
            print(f"  • {tname:<25}: {cnt:>6} rows")
        except Exception as e:
            print(f"  • {tname:<25}: Error ({e})")

    print(f"\nTOTAL RECORDS IN DATABASE: {total_records:,} (Threshold Requirement: >= 5,000)")
    if total_records >= 5000:
        print(">> DATASET REQUIREMENT: PASS")
    else:
        print(">> DATASET REQUIREMENT: FAIL")

    # 2. Views
    views_result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.views 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)).fetchall()
    print(f"\nFound {len(views_result)} Views:")
    for (vname,) in views_result:
        print(f"  • View: {vname}")

    # 3. Functions / Stored Procedures
    routines = conn.execute(text("""
        SELECT routine_name, routine_type 
        FROM information_schema.routines 
        WHERE routine_schema = 'public'
        ORDER BY routine_name;
    """)).fetchall()
    print(f"\nFound {len(routines)} Routines / Stored Procedures:")
    for rname, rtype in routines:
        print(f"  • {rtype}: {rname}")

    # 4. Triggers
    triggers = conn.execute(text("""
        SELECT trigger_name, event_manipulation, event_object_table 
        FROM information_schema.triggers 
        WHERE trigger_schema = 'public'
        ORDER BY event_object_table, trigger_name;
    """)).fetchall()
    print(f"\nFound {len(triggers)} Triggers:")
    for tname, tevent, ttable in triggers:
        print(f"  • Trigger: {tname} ON {ttable} ({tevent})")

    # 5. Foreign Key Integrity Check
    print("\nForeign Key Integrity Verification:")
    orphan_checks = [
        ("hotels -> destinations", "SELECT COUNT(*) FROM hotels h LEFT JOIN destinations d ON h.destination_id = d.id WHERE d.id IS NULL"),
        ("attractions -> destinations", "SELECT COUNT(*) FROM attractions a LEFT JOIN destinations d ON a.destination_id = d.id WHERE d.id IS NULL"),
        ("restaurants -> destinations", "SELECT COUNT(*) FROM restaurants r LEFT JOIN destinations d ON r.destination_id = d.id WHERE d.id IS NULL"),
        ("transport_options -> destinations", "SELECT COUNT(*) FROM transport_options t LEFT JOIN destinations d ON t.destination_id = d.id WHERE d.id IS NULL"),
        ("trips -> users", "SELECT COUNT(*) FROM trips t LEFT JOIN users u ON t.user_id = u.id WHERE u.id IS NULL AND t.user_id IS NOT NULL"),
        ("trips -> destinations", "SELECT COUNT(*) FROM trips t LEFT JOIN destinations d ON t.destination_id = d.id WHERE d.id IS NULL"),
        ("itineraries -> trips", "SELECT COUNT(*) FROM itineraries i LEFT JOIN trips t ON i.trip_id = t.id WHERE t.id IS NULL"),
        ("itinerary_items -> itineraries", "SELECT COUNT(*) FROM itinerary_items ii LEFT JOIN itineraries i ON ii.itinerary_id = i.id WHERE i.id IS NULL"),
    ]
    for check_name, q in orphan_checks:
        try:
            orphans = conn.execute(text(q)).scalar()
            status = "CLEAN (0 orphans)" if orphans == 0 else f"WARNING: {orphans} orphaned records"
            print(f"  • {check_name:<40}: {status}")
        except Exception as e:
            print(f"  • {check_name:<40}: Check Skipped ({e})")
