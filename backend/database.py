"""
database.py — SQLite setup, schema creation, and seed data for CarSense.

Design decision: SQLite is the right choice for a take-home — zero external
dependencies, sub-millisecond reads, and the dataset fits comfortably in memory.
A production system would swap this for PostgreSQL without changing the query layer.
"""

import aiosqlite
import json
import os

DB_PATH = os.getenv("DB_PATH", "carsense.db")

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS cars (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    make            TEXT NOT NULL,
    model           TEXT NOT NULL,
    variant         TEXT NOT NULL,
    year            INTEGER NOT NULL,
    segment         TEXT NOT NULL,
    body_type       TEXT NOT NULL,
    price_lakh_min  REAL NOT NULL,
    price_lakh_max  REAL NOT NULL,
    fuel_type       TEXT NOT NULL,
    transmission    TEXT NOT NULL,
    engine_cc       INTEGER,
    power_bhp       INTEGER,
    torque_nm       INTEGER,
    mileage_kmpl    REAL,
    range_km        INTEGER,
    seating         INTEGER NOT NULL,
    boot_space_l    INTEGER,
    ground_clearance_mm INTEGER,
    safety_rating   REAL,
    airbags         INTEGER,
    features        TEXT NOT NULL,  -- JSON array
    pros            TEXT NOT NULL,  -- JSON array
    cons            TEXT NOT NULL,  -- JSON array
    image_url       TEXT,
    best_for        TEXT NOT NULL   -- JSON array of use-case tags
);

CREATE TABLE IF NOT EXISTS shortlists (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    car_id      INTEGER NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (car_id) REFERENCES cars(id)
);

CREATE INDEX IF NOT EXISTS idx_cars_segment ON cars(segment);
CREATE INDEX IF NOT EXISTS idx_cars_fuel ON cars(fuel_type);
CREATE INDEX IF NOT EXISTS idx_cars_price ON cars(price_lakh_min, price_lakh_max);
CREATE INDEX IF NOT EXISTS idx_shortlists_session ON shortlists(session_id);
"""

# ---------------------------------------------------------------------------
# Connection helper
# ---------------------------------------------------------------------------

async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Create tables and seed data if the database is empty."""
    db = await get_db()
    try:
        await db.executescript(SCHEMA)
        cursor = await db.execute("SELECT COUNT(*) FROM cars")
        row = await cursor.fetchone()
        if row[0] == 0:
            await _seed(db)
        await db.commit()
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Seed data — 30 cars across Indian market segments
# ---------------------------------------------------------------------------

SEED_CARS = [
    # ── Hatchbacks ──────────────────────────────────────────────────────────
    {
        "make": "Maruti Suzuki", "model": "Swift", "variant": "ZXi+ AMT",
        "year": 2024, "segment": "Hatchback", "body_type": "Hatchback",
        "price_lakh_min": 5.99, "price_lakh_max": 9.49,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1197, "power_bhp": 82, "torque_nm": 113,
        "mileage_kmpl": 22.56, "range_km": None, "seating": 5,
        "boot_space_l": 268, "ground_clearance_mm": 163,
        "safety_rating": 4.0, "airbags": 6,
        "features": ["Touchscreen Infotainment", "Cruise Control", "Auto Headlamps", "Rear Camera", "Wireless Charging"],
        "pros": ["Best-in-class fuel efficiency", "Strong resale value", "Wide service network"],
        "cons": ["Compact rear seat", "Basic interior plastics", "Average NVH"],
        "best_for": ["daily_commute", "first_car", "fuel_efficiency", "city_driving"],
        "image_url": None
    },
    {
        "make": "Hyundai", "model": "i20", "variant": "Asta (O) 1.0 Turbo DCT",
        "year": 2024, "segment": "Premium Hatchback", "body_type": "Hatchback",
        "price_lakh_min": 7.04, "price_lakh_max": 11.45,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 998, "power_bhp": 120, "torque_nm": 172,
        "mileage_kmpl": 20.25, "range_km": None, "seating": 5,
        "boot_space_l": 311, "ground_clearance_mm": 170,
        "safety_rating": 3.0, "airbags": 6,
        "features": ["10.25-inch Touchscreen", "Bose Sound System", "Sunroof", "BlueLink Connected", "Air Purifier"],
        "pros": ["Premium cabin feel", "Turbo engine is peppy", "Feature-loaded"],
        "cons": ["Expensive top variants", "Turbo DCT jerky in traffic", "Firm ride"],
        "best_for": ["enthusiast", "feature_rich", "premium_feel", "city_driving"],
        "image_url": None
    },
    {
        "make": "Tata", "model": "Altroz", "variant": "XZ+ Dark",
        "year": 2024, "segment": "Premium Hatchback", "body_type": "Hatchback",
        "price_lakh_min": 6.60, "price_lakh_max": 10.50,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 1199, "power_bhp": 86, "torque_nm": 113,
        "mileage_kmpl": 22.07, "range_km": None, "seating": 5,
        "boot_space_l": 345, "ground_clearance_mm": 165,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["7-inch Touchscreen", "iRA Connected", "Projector Headlamps", "90-degree Door Opening"],
        "pros": ["5-star GNCAP safety", "Spacious boot", "Diesel option available"],
        "cons": ["No automatic in diesel", "Infotainment lags", "Needs more power"],
        "best_for": ["safety_first", "daily_commute", "family", "fuel_efficiency"],
        "image_url": None
    },
    {
        "make": "Maruti Suzuki", "model": "Baleno", "variant": "Alpha AMT",
        "year": 2024, "segment": "Premium Hatchback", "body_type": "Hatchback",
        "price_lakh_min": 6.61, "price_lakh_max": 9.88,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1197, "power_bhp": 90, "torque_nm": 113,
        "mileage_kmpl": 22.35, "range_km": None, "seating": 5,
        "boot_space_l": 318, "ground_clearance_mm": 170,
        "safety_rating": 3.0, "airbags": 6,
        "features": ["9-inch SmartPlay Pro+", "Head-Up Display", "360-degree Camera", "Suzuki Connect"],
        "pros": ["Spacious cabin", "Excellent mileage", "Low maintenance cost"],
        "cons": ["AMT not smooth", "Body roll in corners", "Average build quality"],
        "best_for": ["daily_commute", "first_car", "fuel_efficiency", "family"],
        "image_url": None
    },
    # ── Compact SUVs ────────────────────────────────────────────────────────
    {
        "make": "Tata", "model": "Nexon", "variant": "XZA+ (O) Diesel",
        "year": 2024, "segment": "Compact SUV", "body_type": "SUV",
        "price_lakh_min": 8.10, "price_lakh_max": 15.50,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 1497, "power_bhp": 115, "torque_nm": 260,
        "mileage_kmpl": 23.22, "range_km": None, "seating": 5,
        "boot_space_l": 382, "ground_clearance_mm": 209,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["10.25-inch Touchscreen", "Ventilated Seats", "Sunroof", "Air Purifier", "Connected Car Tech"],
        "pros": ["5-star safety rating", "High ground clearance", "Diesel is very efficient"],
        "cons": ["Compact rear seat for 3", "Boot lip is high", "Turbo lag below 2000rpm"],
        "best_for": ["safety_first", "daily_commute", "rough_roads", "first_car"],
        "image_url": None
    },
    {
        "make": "Hyundai", "model": "Venue", "variant": "SX(O) 1.0 Turbo DCT",
        "year": 2024, "segment": "Compact SUV", "body_type": "SUV",
        "price_lakh_min": 7.94, "price_lakh_max": 13.48,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 998, "power_bhp": 120, "torque_nm": 172,
        "mileage_kmpl": 18.15, "range_km": None, "seating": 5,
        "boot_space_l": 350, "ground_clearance_mm": 195,
        "safety_rating": 3.0, "airbags": 6,
        "features": ["8-inch Touchscreen", "BlueLink Connected", "Wireless CarPlay", "Rear Camera", "TPMS"],
        "pros": ["Compact city-friendly size", "Punchy turbo engine", "Good feature list"],
        "cons": ["Tight rear seat", "No diesel option now", "Average safety rating"],
        "best_for": ["city_driving", "first_car", "solo_commute", "parking_ease"],
        "image_url": None
    },
    {
        "make": "Kia", "model": "Sonet", "variant": "HTX+ 1.0 Turbo iMT",
        "year": 2024, "segment": "Compact SUV", "body_type": "SUV",
        "price_lakh_min": 7.99, "price_lakh_max": 15.69,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 998, "power_bhp": 120, "torque_nm": 172,
        "mileage_kmpl": 18.20, "range_km": None, "seating": 5,
        "boot_space_l": 392, "ground_clearance_mm": 211,
        "safety_rating": 3.0, "airbags": 6,
        "features": ["10.25-inch Touchscreen", "Bose Sound", "Ventilated Seats", "Sunroof", "UVO Connected"],
        "pros": ["Loaded with features", "Multiple powertrain options", "Bold design"],
        "cons": ["Pricey top variants", "Firm ride quality", "Rear seat is snug"],
        "best_for": ["feature_rich", "enthusiast", "daily_commute", "rough_roads"],
        "image_url": None
    },
    {
        "make": "Maruti Suzuki", "model": "Brezza", "variant": "ZXi+ AT",
        "year": 2024, "segment": "Compact SUV", "body_type": "SUV",
        "price_lakh_min": 8.34, "price_lakh_max": 14.14,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1462, "power_bhp": 103, "torque_nm": 137,
        "mileage_kmpl": 20.15, "range_km": None, "seating": 5,
        "boot_space_l": 328, "ground_clearance_mm": 198,
        "safety_rating": 4.0, "airbags": 6,
        "features": ["9-inch SmartPlay Pro+", "Sunroof", "360-degree Camera", "Head-Up Display", "Suzuki Connect"],
        "pros": ["Proven reliability", "Excellent resale value", "Smooth automatic"],
        "cons": ["Needs more power", "No diesel option", "Average NVH"],
        "best_for": ["daily_commute", "family", "resale_value", "city_driving"],
        "image_url": None
    },
    # ── Mid-size Sedans ─────────────────────────────────────────────────────
    {
        "make": "Honda", "model": "City", "variant": "ZX CVT",
        "year": 2024, "segment": "Mid-size Sedan", "body_type": "Sedan",
        "price_lakh_min": 11.82, "price_lakh_max": 16.35,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1498, "power_bhp": 121, "torque_nm": 145,
        "mileage_kmpl": 18.4, "range_km": None, "seating": 5,
        "boot_space_l": 506, "ground_clearance_mm": 165,
        "safety_rating": 4.0, "airbags": 6,
        "features": ["8-inch Touchscreen", "LaneWatch Camera", "Honda Connect", "LED Headlamps", "Rear AC Vents"],
        "pros": ["Legendary reliability", "Spacious rear seat", "Massive boot space"],
        "cons": ["Dated infotainment", "CVT feels rubber-bandy", "Premium pricing"],
        "best_for": ["highway_touring", "family", "comfort", "resale_value"],
        "image_url": None
    },
    {
        "make": "Hyundai", "model": "Verna", "variant": "SX(O) 1.5 Turbo DCT",
        "year": 2024, "segment": "Mid-size Sedan", "body_type": "Sedan",
        "price_lakh_min": 11.00, "price_lakh_max": 17.42,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1482, "power_bhp": 160, "torque_nm": 253,
        "mileage_kmpl": 20.6, "range_km": None, "seating": 5,
        "boot_space_l": 480, "ground_clearance_mm": 170,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["10.25-inch Touchscreen", "ADAS Level 2", "Ventilated Seats", "Bose Sound", "Digital Cluster"],
        "pros": ["Most powerful in segment", "ADAS safety features", "Premium interiors"],
        "cons": ["Turbo DCT hesitant at low speeds", "No diesel anymore", "Expensive top-end"],
        "best_for": ["enthusiast", "highway_touring", "safety_first", "premium_feel"],
        "image_url": None
    },
    {
        "make": "Skoda", "model": "Slavia", "variant": "Style 1.5 TSI DSG",
        "year": 2024, "segment": "Mid-size Sedan", "body_type": "Sedan",
        "price_lakh_min": 11.39, "price_lakh_max": 18.49,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1498, "power_bhp": 150, "torque_nm": 250,
        "mileage_kmpl": 18.72, "range_km": None, "seating": 5,
        "boot_space_l": 521, "ground_clearance_mm": 179,
        "safety_rating": 4.0, "airbags": 6,
        "features": ["10-inch Touchscreen", "Ventilated Seats", "Sunroof", "Wireless CarPlay", "Cruise Control"],
        "pros": ["Best-in-class handling", "Huge boot", "Solid build quality"],
        "cons": ["DSG needs careful driving", "After-sales not as wide", "Infotainment can lag"],
        "best_for": ["enthusiast", "highway_touring", "long_drives", "comfort"],
        "image_url": None
    },
    # ── Mid-size SUVs ───────────────────────────────────────────────────────
    {
        "make": "Hyundai", "model": "Creta", "variant": "SX(O) 1.5 Turbo DCT",
        "year": 2024, "segment": "Mid-size SUV", "body_type": "SUV",
        "price_lakh_min": 11.00, "price_lakh_max": 20.15,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 1482, "power_bhp": 160, "torque_nm": 253,
        "mileage_kmpl": 17.0, "range_km": None, "seating": 5,
        "boot_space_l": 433, "ground_clearance_mm": 190,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["10.25-inch Dual Screens", "ADAS Level 2", "Panoramic Sunroof", "Bose Sound", "Ventilated Seats"],
        "pros": ["Segment leader for a reason", "ADAS suite", "Strong resale"],
        "cons": ["3-cylinder turbo is divisive", "Road noise at speed", "Stiff ride on bad roads"],
        "best_for": ["family", "safety_first", "feature_rich", "daily_commute"],
        "image_url": None
    },
    {
        "make": "Kia", "model": "Seltos", "variant": "HTX+ 1.5 Turbo DCT",
        "year": 2024, "segment": "Mid-size SUV", "body_type": "SUV",
        "price_lakh_min": 10.90, "price_lakh_max": 19.65,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 1482, "power_bhp": 160, "torque_nm": 253,
        "mileage_kmpl": 16.8, "range_km": None, "seating": 5,
        "boot_space_l": 433, "ground_clearance_mm": 190,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["10.25-inch Touchscreen", "ADAS Level 2", "Bose Sound", "Panoramic Sunroof", "360 Camera"],
        "pros": ["Sharp design", "ADAS standard", "Great infotainment"],
        "cons": ["DCT can be jerky", "Firm low-speed ride", "No diesel AT in base"],
        "best_for": ["family", "safety_first", "feature_rich", "highway_touring"],
        "image_url": None
    },
    {
        "make": "Tata", "model": "Harrier", "variant": "XZA+ Dark AT",
        "year": 2024, "segment": "Mid-size SUV", "body_type": "SUV",
        "price_lakh_min": 15.49, "price_lakh_max": 26.44,
        "fuel_type": "Diesel", "transmission": "Both",
        "engine_cc": 1956, "power_bhp": 170, "torque_nm": 350,
        "mileage_kmpl": 16.35, "range_km": None, "seating": 5,
        "boot_space_l": 425, "ground_clearance_mm": 198,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["12.3-inch Touchscreen", "ADAS", "Panoramic Sunroof", "JBL Sound", "Ventilated Seats"],
        "pros": ["Commanding road presence", "5-star safety", "Strong diesel engine"],
        "cons": ["Only diesel engine", "Heavier than rivals", "Tata service quality varies"],
        "best_for": ["highway_touring", "presence", "safety_first", "long_drives"],
        "image_url": None
    },
    {
        "make": "MG", "model": "Hector", "variant": "Sharp Pro CVT",
        "year": 2024, "segment": "Mid-size SUV", "body_type": "SUV",
        "price_lakh_min": 14.00, "price_lakh_max": 22.00,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 1451, "power_bhp": 143, "torque_nm": 250,
        "mileage_kmpl": 14.8, "range_km": None, "seating": 5,
        "boot_space_l": 587, "ground_clearance_mm": 192,
        "safety_rating": 4.0, "airbags": 6,
        "features": ["14-inch Touchscreen", "Panoramic Sunroof", "ADAS", "i-Smart Connected", "Infinity Sound"],
        "pros": ["Massive cabin space", "Huge boot", "Loaded with tech"],
        "cons": ["CVT saps performance", "Heavy to drive", "Resale value concerns"],
        "best_for": ["family", "space", "feature_rich", "tech_lovers"],
        "image_url": None
    },
    {
        "make": "Mahindra", "model": "XUV700", "variant": "AX7 L Diesel AT",
        "year": 2024, "segment": "Mid-size SUV", "body_type": "SUV",
        "price_lakh_min": 13.99, "price_lakh_max": 26.99,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 2184, "power_bhp": 185, "torque_nm": 420,
        "mileage_kmpl": 16.0, "range_km": None, "seating": 7,
        "boot_space_l": 451, "ground_clearance_mm": 200,
        "safety_rating": 5.0, "airbags": 7,
        "features": ["10.25-inch Dual Screens", "ADAS", "Panoramic Sunroof", "Sony Sound", "Flush Door Handles"],
        "pros": ["Incredible value for money", "7 airbags standard", "Powerful engines"],
        "cons": ["Long waiting periods", "3rd row is tight", "Build quality inconsistent"],
        "best_for": ["family", "safety_first", "value", "highway_touring", "7_seater"],
        "image_url": None
    },
    # ── Premium SUVs ────────────────────────────────────────────────────────
    {
        "make": "Toyota", "model": "Fortuner", "variant": "Legender 2.8 4x4 AT",
        "year": 2024, "segment": "Full-size SUV", "body_type": "SUV",
        "price_lakh_min": 33.43, "price_lakh_max": 51.44,
        "fuel_type": "Diesel", "transmission": "Automatic",
        "engine_cc": 2755, "power_bhp": 204, "torque_nm": 500,
        "mileage_kmpl": 10.0, "range_km": None, "seating": 7,
        "boot_space_l": 296, "ground_clearance_mm": 221,
        "safety_rating": 5.0, "airbags": 7,
        "features": ["Touchscreen Infotainment", "Cooled Seats", "Wireless Charging", "4x4 with Diff Lock", "Cruise Control"],
        "pros": ["Bulletproof reliability", "True 4x4 capability", "Massive resale value"],
        "cons": ["Expensive to buy and run", "Thirsty engine", "Dated interior design"],
        "best_for": ["off_road", "presence", "7_seater", "reliability", "towing"],
        "image_url": None
    },
    {
        "make": "Tata", "model": "Safari", "variant": "XZA+ Gold AT",
        "year": 2024, "segment": "Mid-size SUV", "body_type": "SUV",
        "price_lakh_min": 16.19, "price_lakh_max": 27.34,
        "fuel_type": "Diesel", "transmission": "Both",
        "engine_cc": 1956, "power_bhp": 170, "torque_nm": 350,
        "mileage_kmpl": 14.5, "range_km": None, "seating": 7,
        "boot_space_l": 340, "ground_clearance_mm": 198,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["12.3-inch Touchscreen", "ADAS", "Panoramic Sunroof", "Boss Mode", "JBL Sound"],
        "pros": ["Iconic nameplate", "Good 3rd row space", "5-star safety"],
        "cons": ["Diesel only", "Not a true off-roader", "2nd row captain seats reduce capacity"],
        "best_for": ["family", "7_seater", "highway_touring", "presence"],
        "image_url": None
    },
    {
        "make": "Hyundai", "model": "Tucson", "variant": "Signature AWD AT",
        "year": 2024, "segment": "Premium SUV", "body_type": "SUV",
        "price_lakh_min": 29.02, "price_lakh_max": 35.94,
        "fuel_type": "Both", "transmission": "Automatic",
        "engine_cc": 1999, "power_bhp": 187, "torque_nm": 416,
        "mileage_kmpl": 14.6, "range_km": None, "seating": 5,
        "boot_space_l": 539, "ground_clearance_mm": 192,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["10.25-inch Dual Screens", "ADAS Level 2", "Panoramic Sunroof", "Bose Sound", "360 Camera"],
        "pros": ["Striking design", "AWD option", "Premium cabin"],
        "cons": ["Expensive", "No 7-seat option", "Rear visibility limited"],
        "best_for": ["premium_feel", "highway_touring", "design_conscious", "comfort"],
        "image_url": None
    },
    {
        "make": "Jeep", "model": "Compass", "variant": "Model S 4x4 Diesel AT",
        "year": 2024, "segment": "Premium SUV", "body_type": "SUV",
        "price_lakh_min": 18.99, "price_lakh_max": 29.49,
        "fuel_type": "Both", "transmission": "Both",
        "engine_cc": 1956, "power_bhp": 170, "torque_nm": 350,
        "mileage_kmpl": 15.4, "range_km": None, "seating": 5,
        "boot_space_l": 438, "ground_clearance_mm": 178,
        "safety_rating": 4.0, "airbags": 6,
        "features": ["10.1-inch Touchscreen", "Panoramic Sunroof", "Wireless CarPlay", "LED Headlamps", "4x4"],
        "pros": ["Genuine off-road DNA", "Solid highway stability", "Unique brand appeal"],
        "cons": ["After-sales network limited", "Interior feels dated", "Resale value dropping"],
        "best_for": ["off_road", "highway_touring", "brand_value", "enthusiast"],
        "image_url": None
    },
    # ── Electric Vehicles ───────────────────────────────────────────────────
    {
        "make": "Tata", "model": "Nexon EV", "variant": "Empowered+ LR",
        "year": 2024, "segment": "Compact SUV", "body_type": "SUV",
        "price_lakh_min": 14.79, "price_lakh_max": 19.94,
        "fuel_type": "Electric", "transmission": "Automatic",
        "engine_cc": None, "power_bhp": 143, "torque_nm": 215,
        "mileage_kmpl": None, "range_km": 465, "seating": 5,
        "boot_space_l": 350, "ground_clearance_mm": 209,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["12.3-inch Touchscreen", "Connected Car Tech", "V2L Capability", "Sunroof", "Auto Climate"],
        "pros": ["465km real-world range", "Low running cost", "Instant torque"],
        "cons": ["Charging infra still growing", "Higher upfront cost", "Battery warranty concerns"],
        "best_for": ["eco_friendly", "city_driving", "low_running_cost", "tech_lovers"],
        "image_url": None
    },
    {
        "make": "MG", "model": "ZS EV", "variant": "Exclusive Pro",
        "year": 2024, "segment": "Mid-size SUV", "body_type": "SUV",
        "price_lakh_min": 18.98, "price_lakh_max": 25.20,
        "fuel_type": "Electric", "transmission": "Automatic",
        "engine_cc": None, "power_bhp": 176, "torque_nm": 280,
        "mileage_kmpl": None, "range_km": 461, "seating": 5,
        "boot_space_l": 470, "ground_clearance_mm": 177,
        "safety_rating": 4.0, "airbags": 6,
        "features": ["10.1-inch Touchscreen", "Panoramic Sunroof", "i-Smart Connected", "ADAS", "PM2.5 Filter"],
        "pros": ["Spacious for an EV", "Good range", "ADAS features"],
        "cons": ["Limited service network", "No fast-charging standard", "Resale uncertain"],
        "best_for": ["eco_friendly", "family", "tech_lovers", "premium_feel"],
        "image_url": None
    },
    {
        "make": "Tata", "model": "Tiago EV", "variant": "XZ+ Tech LUX LR",
        "year": 2024, "segment": "Hatchback", "body_type": "Hatchback",
        "price_lakh_min": 8.69, "price_lakh_max": 11.79,
        "fuel_type": "Electric", "transmission": "Automatic",
        "engine_cc": None, "power_bhp": 75, "torque_nm": 114,
        "mileage_kmpl": None, "range_km": 315, "seating": 5,
        "boot_space_l": 240, "ground_clearance_mm": 165,
        "safety_rating": 4.0, "airbags": 4,
        "features": ["7-inch Touchscreen", "Connected Car Tech", "Regenerative Braking", "Cruise Control"],
        "pros": ["Most affordable EV", "Zero running cost for commuters", "Zippy in city"],
        "cons": ["Limited range", "Not for highways", "Basic interiors"],
        "best_for": ["eco_friendly", "city_driving", "first_car", "low_running_cost"],
        "image_url": None
    },
    {
        "make": "Mahindra", "model": "XUV400 EV", "variant": "EL Pro LR",
        "year": 2024, "segment": "Compact SUV", "body_type": "SUV",
        "price_lakh_min": 15.49, "price_lakh_max": 19.19,
        "fuel_type": "Electric", "transmission": "Automatic",
        "engine_cc": None, "power_bhp": 150, "torque_nm": 310,
        "mileage_kmpl": None, "range_km": 456, "seating": 5,
        "boot_space_l": 378, "ground_clearance_mm": 180,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["10.25-inch Touchscreen", "Connected Car Tech", "Sunroof", "Fast Charging Support"],
        "pros": ["5-star safety", "Good range", "Peppy performance"],
        "cons": ["Interior feels basic", "No rear AC vents", "Charging network sparse"],
        "best_for": ["eco_friendly", "safety_first", "city_driving", "daily_commute"],
        "image_url": None
    },
    # ── Budget Cars ─────────────────────────────────────────────────────────
    {
        "make": "Maruti Suzuki", "model": "Alto K10", "variant": "VXi+ AGS",
        "year": 2024, "segment": "Entry Hatchback", "body_type": "Hatchback",
        "price_lakh_min": 3.99, "price_lakh_max": 5.96,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 998, "power_bhp": 67, "torque_nm": 89,
        "mileage_kmpl": 24.39, "range_km": None, "seating": 5,
        "boot_space_l": 214, "ground_clearance_mm": 160,
        "safety_rating": 2.0, "airbags": 2,
        "features": ["7-inch SmartPlay Studio", "Dual Airbags", "Rear Parking Sensors"],
        "pros": ["Cheapest automatic car", "Outstanding fuel efficiency", "Easy to drive"],
        "cons": ["Low safety rating", "Very basic feel", "Tiny boot"],
        "best_for": ["budget", "first_car", "city_driving", "fuel_efficiency"],
        "image_url": None
    },
    {
        "make": "Renault", "model": "Kwid", "variant": "Climber AMT",
        "year": 2024, "segment": "Entry Hatchback", "body_type": "Hatchback",
        "price_lakh_min": 4.70, "price_lakh_max": 6.45,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 999, "power_bhp": 68, "torque_nm": 91,
        "mileage_kmpl": 22.0, "range_km": None, "seating": 5,
        "boot_space_l": 279, "ground_clearance_mm": 184,
        "safety_rating": 2.0, "airbags": 2,
        "features": ["8-inch Touchscreen", "Wireless CarPlay", "LED DRLs", "Rear Camera"],
        "pros": ["SUV-like stance", "Bigger boot than rivals", "Good ground clearance"],
        "cons": ["Low safety rating", "Build quality concerns", "Thrashy engine"],
        "best_for": ["budget", "first_car", "rough_roads", "city_driving"],
        "image_url": None
    },
    {
        "make": "Tata", "model": "Punch", "variant": "Creative+ AMT",
        "year": 2024, "segment": "Micro SUV", "body_type": "SUV",
        "price_lakh_min": 6.13, "price_lakh_max": 10.20,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1199, "power_bhp": 86, "torque_nm": 113,
        "mileage_kmpl": 18.8, "range_km": None, "seating": 5,
        "boot_space_l": 366, "ground_clearance_mm": 187,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["7-inch Touchscreen", "iRA Connected", "Roof Rails", "Projector Headlamps"],
        "pros": ["5-star safety at this price!", "Great ground clearance", "Fun to drive"],
        "cons": ["Needs more power", "Harsh ride on bumps", "AMT is slow-shifting"],
        "best_for": ["safety_first", "first_car", "rough_roads", "budget", "city_driving"],
        "image_url": None
    },
    # ── MPVs ────────────────────────────────────────────────────────────────
    {
        "make": "Maruti Suzuki", "model": "Ertiga", "variant": "ZXi+ AT",
        "year": 2024, "segment": "MPV", "body_type": "MPV",
        "price_lakh_min": 8.69, "price_lakh_max": 13.04,
        "fuel_type": "Petrol", "transmission": "Both",
        "engine_cc": 1462, "power_bhp": 103, "torque_nm": 137,
        "mileage_kmpl": 20.30, "range_km": None, "seating": 7,
        "boot_space_l": 209, "ground_clearance_mm": 185,
        "safety_rating": 3.0, "airbags": 6,
        "features": ["7-inch SmartPlay Pro", "Cruise Control", "Rear AC Vents", "Suzuki Connect"],
        "pros": ["Best value 7-seater", "Excellent fuel economy", "Low maintenance"],
        "cons": ["3rd row for kids only", "Body roll in corners", "Basic interior"],
        "best_for": ["family", "7_seater", "budget", "fuel_efficiency", "value"],
        "image_url": None
    },
    {
        "make": "Toyota", "model": "Innova Hycross", "variant": "VX HEV AT",
        "year": 2024, "segment": "Premium MPV", "body_type": "MPV",
        "price_lakh_min": 19.77, "price_lakh_max": 30.98,
        "fuel_type": "Hybrid", "transmission": "Automatic",
        "engine_cc": 1987, "power_bhp": 186, "torque_nm": 188,
        "mileage_kmpl": 21.1, "range_km": None, "seating": 7,
        "boot_space_l": 240, "ground_clearance_mm": 185,
        "safety_rating": 5.0, "airbags": 6,
        "features": ["10.1-inch Touchscreen", "Ottoman Seats", "Panoramic Sunroof", "Wireless Charging", "JBL Sound"],
        "pros": ["Hybrid fuel efficiency", "Legendary reliability", "Ottoman 2nd row seats"],
        "cons": ["Very expensive", "Long waiting", "3rd row cramped"],
        "best_for": ["family", "7_seater", "comfort", "reliability", "highway_touring"],
        "image_url": None
    },
]


async def _seed(db: aiosqlite.Connection):
    """Insert seed cars into the database."""
    for car in SEED_CARS:
        await db.execute(
            """INSERT INTO cars (
                make, model, variant, year, segment, body_type,
                price_lakh_min, price_lakh_max, fuel_type, transmission,
                engine_cc, power_bhp, torque_nm, mileage_kmpl, range_km,
                seating, boot_space_l, ground_clearance_mm,
                safety_rating, airbags, features, pros, cons, image_url, best_for
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                car["make"], car["model"], car["variant"], car["year"],
                car["segment"], car["body_type"],
                car["price_lakh_min"], car["price_lakh_max"],
                car["fuel_type"], car["transmission"],
                car["engine_cc"], car["power_bhp"], car["torque_nm"],
                car["mileage_kmpl"], car["range_km"],
                car["seating"], car["boot_space_l"], car["ground_clearance_mm"],
                car["safety_rating"], car["airbags"],
                json.dumps(car["features"]),
                json.dumps(car["pros"]),
                json.dumps(car["cons"]),
                car["image_url"],
                json.dumps(car["best_for"]),
            ),
        )
    print(f"Seeded {len(SEED_CARS)} cars into the database.")
