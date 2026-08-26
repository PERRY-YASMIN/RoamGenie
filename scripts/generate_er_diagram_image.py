import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Set up canvas dimensions
WIDTH = 2600
HEIGHT = 1750
BG_COLOR = (248, 250, 252) # Clean slate light background
CARD_BG = (255, 255, 255)
CARD_BORDER = (203, 213, 225)
HEADER_BG = (30, 41, 59) # Dark slate
HEADER_TEXT = (255, 255, 255)
TEXT_COLOR = (15, 23, 42)
PK_COLOR = (185, 28, 28) # Red for PK
FK_COLOR = (3, 105, 161) # Blue for FK
LINE_COLOR = (100, 116, 139)

img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
draw = ImageDraw.Draw(img)

# Try loading standard Windows system fonts, or default
try:
    title_font = ImageFont.truetype("arialbd.ttf", 36)
    subtitle_font = ImageFont.truetype("arial.ttf", 20)
    entity_font = ImageFont.truetype("arialbd.ttf", 18)
    attr_font = ImageFont.truetype("arial.ttf", 14)
    badge_font = ImageFont.truetype("arialbd.ttf", 13)
except:
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    entity_font = ImageFont.load_default()
    attr_font = ImageFont.load_default()
    badge_font = ImageFont.load_default()

# Draw Title Header Banner
draw.rectangle([(40, 30), (WIDTH - 40, 110)], fill=(15, 23, 42))
draw.text((60, 42), "RoamGenie — Relational Database Entity-Relationship (ER) Diagram", fill=(255, 255, 255), font=title_font)
draw.text((60, 82), "Semester 5 DBMS Theory & Project | 22 Normalized Relational Entities (3NF/BCNF)", fill=(148, 163, 184), font=subtitle_font)

# Define Entities with layout coordinates
# Format: name, x, y, w, h, [ (name, type, tag) ]
entities = [
    # Top Left: Users Subsystem
    {
        "name": "users", "x": 60, "y": 140, "w": 320, "h": 220,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("email", "VARCHAR(254)", "UK"),
            ("password_hash", "TEXT", ""),
            ("full_name", "VARCHAR(120)", ""),
            ("role", "VARCHAR(20)", "CHK"),
            ("created_at", "TIMESTAMPTZ", ""),
            ("updated_at", "TIMESTAMPTZ", "")
        ]
    },
    {
        "name": "user_preferences", "x": 60, "y": 390, "w": 320, "h": 180,
        "attrs": [
            ("user_id", "BIGINT", "PK,FK"),
            ("hotel_preference", "VARCHAR(40)", ""),
            ("food_preference", "VARCHAR(80)", ""),
            ("transport_preference", "VARCHAR(40)", ""),
            ("travel_style", "VARCHAR(40)", ""),
            ("special_requirements", "TEXT", "")
        ]
    },
    {
        "name": "activity_preferences", "x": 60, "y": 600, "w": 320, "h": 120,
        "attrs": [
            ("user_id", "BIGINT", "PK,FK"),
            ("activity", "VARCHAR(60)", "PK")
        ]
    },
    {
        "name": "saved_trips", "x": 60, "y": 750, "w": 320, "h": 150,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("user_id", "BIGINT", "FK"),
            ("trip_id", "BIGINT", "FK"),
            ("saved_at", "TIMESTAMPTZ", "")
        ]
    },

    # Center: Destinations Catalogue Subsystem
    {
        "name": "destinations", "x": 480, "y": 140, "w": 350, "h": 200,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("city", "VARCHAR(100)", "UK(1/2)"),
            ("country", "VARCHAR(100)", "UK(2/2)"),
            ("description", "TEXT", ""),
            ("average_daily_cost", "NUMERIC(12,2)", "CHK"),
            ("active", "BOOLEAN", "")
        ]
    },
    {
        "name": "hotels", "x": 480, "y": 370, "w": 350, "h": 170,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("destination_id", "BIGINT", "FK"),
            ("name", "VARCHAR(150)", ""),
            ("price_per_night", "NUMERIC(12,2)", "CHK"),
            ("rating", "NUMERIC(2,1)", "CHK")
        ]
    },
    {
        "name": "restaurants", "x": 480, "y": 570, "w": 350, "h": 190,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("destination_id", "BIGINT", "FK"),
            ("name", "VARCHAR(150)", ""),
            ("cuisine", "VARCHAR(80)", ""),
            ("average_cost_per_person", "NUMERIC(12,2)", "CHK"),
            ("rating", "NUMERIC(2,1)", "CHK")
        ]
    },
    {
        "name": "attractions", "x": 480, "y": 790, "w": 350, "h": 190,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("destination_id", "BIGINT", "FK"),
            ("name", "VARCHAR(150)", ""),
            ("category", "VARCHAR(60)", ""),
            ("entry_fee", "NUMERIC(12,2)", "CHK"),
            ("rating", "NUMERIC(2,1)", "CHK")
        ]
    },
    {
        "name": "transport_options", "x": 480, "y": 1010, "w": 350, "h": 200,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("origin", "VARCHAR(100)", ""),
            ("destination_id", "BIGINT", "FK"),
            ("mode", "VARCHAR(40)", ""),
            ("provider", "VARCHAR(100)", ""),
            ("estimated_cost", "NUMERIC(12,2)", "CHK"),
            ("duration_minutes", "INTEGER", "CHK")
        ]
    },

    # Center-Right: Trips & Planning Subsystem
    {
        "name": "trips", "x": 930, "y": 140, "w": 360, "h": 290,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("user_id", "BIGINT", "FK"),
            ("destination_id", "BIGINT", "FK"),
            ("starting_location", "VARCHAR(120)", ""),
            ("start_date", "DATE", ""),
            ("end_date", "DATE", "CHK"),
            ("traveller_count", "INTEGER", "CHK"),
            ("total_budget", "NUMERIC(12,2)", "CHK"),
            ("estimated_total", "NUMERIC(12,2)", "CHK"),
            ("status", "VARCHAR(20)", "CHK"),
            ("created_at", "TIMESTAMPTZ", "")
        ]
    },
    {
        "name": "budget_allocations", "x": 930, "y": 460, "w": 360, "h": 150,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("trip_id", "BIGINT", "FK"),
            ("category", "VARCHAR(40)", "UK(2/2)"),
            ("amount", "NUMERIC(12,2)", "CHK")
        ]
    },
    {
        "name": "expenses", "x": 930, "y": 640, "w": 360, "h": 170,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("trip_id", "BIGINT", "FK"),
            ("category", "VARCHAR(40)", ""),
            ("description", "TEXT", ""),
            ("amount", "NUMERIC(12,2)", "CHK"),
            ("incurred_on", "DATE", "")
        ]
    },
    {
        "name": "trip_members", "x": 930, "y": 840, "w": 360, "h": 150,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("trip_id", "BIGINT", "FK"),
            ("display_name", "VARCHAR(120)", ""),
            ("age_group", "VARCHAR(30)", ""),
            ("special_requirements", "TEXT", "")
        ]
    },
    {
        "name": "packing_items", "x": 930, "y": 1020, "w": 360, "h": 160,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("trip_id", "BIGINT", "FK"),
            ("item", "VARCHAR(120)", "UK(2/2)"),
            ("category", "VARCHAR(40)", ""),
            ("is_packed", "BOOLEAN", "")
        ]
    },

    # Right: Itinerary Subsystem
    {
        "name": "itineraries", "x": 1390, "y": 140, "w": 350, "h": 180,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("trip_id", "BIGINT", "FK"),
            ("version", "INTEGER", "CHK"),
            ("summary", "TEXT", ""),
            ("provider", "VARCHAR(40)", ""),
            ("created_at", "TIMESTAMPTZ", "")
        ]
    },
    {
        "name": "itinerary_days", "x": 1390, "y": 350, "w": 350, "h": 150,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("itinerary_id", "BIGINT", "FK"),
            ("day_number", "INTEGER", "CHK"),
            ("itinerary_date", "DATE", "")
        ]
    },
    {
        "name": "itinerary_items", "x": 1390, "y": 530, "w": 350, "h": 220,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("itinerary_day_id", "BIGINT", "FK"),
            ("item_order", "INTEGER", "CHK"),
            ("start_time", "TIME", ""),
            ("title", "VARCHAR(180)", ""),
            ("category", "VARCHAR(50)", ""),
            ("estimated_cost", "NUMERIC(12,2)", "CHK"),
            ("notes", "TEXT", "")
        ]
    },

    # Far Right: AI & Supporting Subsystems
    {
        "name": "ai_conversations", "x": 1840, "y": 140, "w": 340, "h": 150,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("user_id", "BIGINT", "FK"),
            ("trip_id", "BIGINT", "FK (Null)"),
            ("created_at", "TIMESTAMPTZ", "")
        ]
    },
    {
        "name": "ai_messages", "x": 1840, "y": 320, "w": 340, "h": 170,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("conversation_id", "BIGINT", "FK"),
            ("role", "VARCHAR(20)", "CHK"),
            ("content", "TEXT", ""),
            ("created_at", "TIMESTAMPTZ", "")
        ]
    },
    {
        "name": "weather_snapshots", "x": 1840, "y": 520, "w": 340, "h": 180,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("destination_id", "BIGINT", "FK"),
            ("observed_at", "TIMESTAMPTZ", ""),
            ("summary", "VARCHAR(160)", ""),
            ("temperature_c", "NUMERIC(5,2)", ""),
            ("provider", "VARCHAR(40)", "")
        ]
    },
    {
        "name": "reviews", "x": 1840, "y": 730, "w": 340, "h": 170,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("user_id", "BIGINT", "FK"),
            ("destination_id", "BIGINT", "FK"),
            ("rating", "INTEGER", "CHK"),
            ("comment", "TEXT", "")
        ]
    },
    {
        "name": "trip_audit", "x": 1840, "y": 930, "w": 340, "h": 190,
        "attrs": [
            ("id", "BIGINT", "PK"),
            ("trip_id", "BIGINT", ""),
            ("action", "VARCHAR(10)", ""),
            ("changed_at", "TIMESTAMPTZ", ""),
            ("changed_by", "TEXT", ""),
            ("old_row", "JSONB", ""),
            ("new_row", "JSONB", "")
        ]
    }
]

# Draw all entity boxes
for ent in entities:
    x, y, w, h = ent["x"], ent["y"], ent["w"], ent["h"]
    # Draw drop shadow
    draw.rectangle([(x + 3, y + 3), (x + w + 3, y + h + 3)], fill=(226, 232, 240))
    # Draw card body
    draw.rectangle([(x, y), (x + w, y + h)], fill=CARD_BG, outline=CARD_BORDER, width=2)
    # Draw header bar
    draw.rectangle([(x, y), (x + w, y + 34)], fill=HEADER_BG)
    draw.text((x + 12, y + 7), ent["name"], fill=HEADER_TEXT, font=entity_font)

    # Draw attributes
    curr_y = y + 42
    for attr_name, attr_type, tag in ent["attrs"]:
        # Attribute name
        draw.text((x + 12, curr_y), attr_name, fill=TEXT_COLOR, font=attr_font)
        # Attribute type
        draw.text((x + 155, curr_y), attr_type, fill=(100, 116, 139), font=attr_font)
        # Key Badge
        if tag:
            badge_color = PK_COLOR if "PK" in tag else (FK_COLOR if "FK" in tag else (16, 185, 129))
            draw.text((x + w - 45, curr_y), tag, fill=badge_color, font=badge_font)
        curr_y += 22

# Save ER Diagram PNG
out_dir = Path("RoamGenie_Milestones_1-5/ER_Diagram")
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / "ER_Diagram.png"
img.save(str(out_path), "PNG", quality=95)
print(f"ER Diagram image generated successfully at: {out_path}")
