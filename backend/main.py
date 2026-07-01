"""
main.py — FastAPI application for CarSense.

Single entry point. Routes are defined here rather than split into router files
because the API surface is small (7 endpoints). In a larger app, we'd split.

Run: uvicorn main:app --reload --port 8000
"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from database import get_db, init_db
from models import (
    CarOut, UserNeeds, RecommendationResponse,
    CompareRequest, CompareResponse,
    ChatRequest, ChatResponse,
    ShortlistItem,
)
from advisor import get_recommendations, compare_cars, chat


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed data on startup."""
    await init_db()
    print("CarSense API ready — database initialized")
    yield


app = FastAPI(
    title="CarSense API",
    description="AI-powered car recommendation engine for the Indian market",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — permissive for development, lock down in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_dict(row) -> dict:
    """Convert an aiosqlite Row to a plain dict."""
    return dict(row)


def _row_to_car(row) -> CarOut:
    """Convert a database row to a CarOut schema."""
    d = _row_to_dict(row)
    d["features"] = json.loads(d["features"])
    d["pros"] = json.loads(d["pros"])
    d["cons"] = json.loads(d["cons"])
    d["best_for"] = json.loads(d["best_for"])
    return CarOut(**d)


# ---------------------------------------------------------------------------
# Car endpoints
# ---------------------------------------------------------------------------

@app.get("/api/cars", response_model=list[CarOut])
async def list_cars(
    segment: Optional[str] = None,
    fuel_type: Optional[str] = None,
    body_type: Optional[str] = None,
    transmission: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_safety: Optional[float] = None,
    seating: Optional[int] = None,
    search: Optional[str] = None,
):
    """List cars with optional filters. Supports text search across make/model."""
    db = await get_db()
    try:
        query = "SELECT * FROM cars WHERE 1=1"
        params: list = []

        if segment:
            query += " AND segment = ?"
            params.append(segment)
        if fuel_type:
            query += " AND (fuel_type = ? OR fuel_type = 'Both')"
            params.append(fuel_type)
        if body_type:
            query += " AND body_type = ?"
            params.append(body_type)
        if transmission:
            query += " AND (transmission = ? OR transmission = 'Both')"
            params.append(transmission)
        if min_price is not None:
            query += " AND price_lakh_max >= ?"
            params.append(min_price)
        if max_price is not None:
            query += " AND price_lakh_min <= ?"
            params.append(max_price)
        if min_safety is not None:
            query += " AND safety_rating >= ?"
            params.append(min_safety)
        if seating is not None:
            query += " AND seating >= ?"
            params.append(seating)
        if search:
            query += " AND (LOWER(make || ' ' || model) LIKE ?)"
            params.append(f"%{search.lower()}%")

        query += " ORDER BY price_lakh_min ASC"

        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [_row_to_car(r) for r in rows]
    finally:
        await db.close()


@app.get("/api/cars/{car_id}", response_model=CarOut)
async def get_car(car_id: int):
    """Get a single car by ID."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Car not found")
        return _row_to_car(row)
    finally:
        await db.close()


@app.get("/api/filters")
async def get_filter_options():
    """Return distinct values for each filter dimension — powers the UI dropdowns."""
    db = await get_db()
    try:
        result = {}
        for col in ["segment", "fuel_type", "body_type", "transmission"]:
            cursor = await db.execute(f"SELECT DISTINCT {col} FROM cars ORDER BY {col}")
            rows = await cursor.fetchall()
            result[col] = [r[0] for r in rows]

        cursor = await db.execute(
            "SELECT MIN(price_lakh_min), MAX(price_lakh_max) FROM cars"
        )
        row = await cursor.fetchone()
        result["price_range"] = {"min": row[0], "max": row[1]}

        cursor = await db.execute("SELECT DISTINCT seating FROM cars ORDER BY seating")
        rows = await cursor.fetchall()
        result["seating_options"] = [r[0] for r in rows]

        return result
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# AI Advisor endpoints
# ---------------------------------------------------------------------------

@app.post("/api/advisor/recommend", response_model=RecommendationResponse)
async def recommend(needs: UserNeeds):
    """
    Core endpoint: Takes buyer needs, returns AI-ranked recommendations.

    The AI sees the full car database, applies the buyer's priorities,
    and explains WHY each car is (or isn't) a good fit.
    """
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM cars")
        rows = await cursor.fetchall()
        all_cars = [_row_to_dict(r) for r in rows]
        return await get_recommendations(needs, all_cars)
    finally:
        await db.close()


@app.post("/api/advisor/compare", response_model=CompareResponse)
async def compare(request: CompareRequest):
    """Compare 2-4 specific cars with optional buyer context."""
    db = await get_db()
    try:
        placeholders = ",".join("?" * len(request.car_ids))
        cursor = await db.execute(
            f"SELECT * FROM cars WHERE id IN ({placeholders})", request.car_ids
        )
        rows = await cursor.fetchall()
        cars = [_row_to_dict(r) for r in rows]

        if len(cars) < 2:
            raise HTTPException(status_code=400, detail="Need at least 2 valid car IDs")

        return await compare_cars(cars, request.user_needs)
    finally:
        await db.close()


@app.post("/api/advisor/chat", response_model=ChatResponse)
async def advisor_chat(request: ChatRequest):
    """Conversational follow-up about cars. Context-aware."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM cars")
        rows = await cursor.fetchall()
        all_cars = [_row_to_dict(r) for r in rows]
        return await chat(request, all_cars)
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Shortlist endpoints
# ---------------------------------------------------------------------------

@app.post("/api/shortlist")
async def add_to_shortlist(item: ShortlistItem):
    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO shortlists (session_id, car_id) VALUES (?, ?)",
            (item.session_id, item.car_id),
        )
        await db.commit()
        return {"status": "added"}
    finally:
        await db.close()


@app.delete("/api/shortlist/{session_id}/{car_id}")
async def remove_from_shortlist(session_id: str, car_id: int):
    db = await get_db()
    try:
        await db.execute(
            "DELETE FROM shortlists WHERE session_id = ? AND car_id = ?",
            (session_id, car_id),
        )
        await db.commit()
        return {"status": "removed"}
    finally:
        await db.close()


@app.get("/api/shortlist/{session_id}")
async def get_shortlist(session_id: str):
    db = await get_db()
    try:
        cursor = await db.execute(
            """SELECT c.* FROM cars c
               JOIN shortlists s ON c.id = s.car_id
               WHERE s.session_id = ?""",
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [_row_to_car(r) for r in rows]
    finally:
        await db.close()


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "carsense-api"}


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
