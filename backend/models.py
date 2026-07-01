"""
models.py — Pydantic schemas for CarSense API.

Separating schemas from the database layer keeps the API contract explicit.
Each model documents what the frontend sends and receives.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------------
# Car schemas
# ---------------------------------------------------------------------------

class CarOut(BaseModel):
    """Full car detail returned by the API."""
    id: int
    make: str
    model: str
    variant: str
    year: int
    segment: str
    body_type: str
    price_lakh_min: float
    price_lakh_max: float
    fuel_type: str
    transmission: str
    engine_cc: Optional[int] = None
    power_bhp: Optional[int] = None
    torque_nm: Optional[int] = None
    mileage_kmpl: Optional[float] = None
    range_km: Optional[int] = None
    seating: int
    boot_space_l: Optional[int] = None
    ground_clearance_mm: Optional[int] = None
    safety_rating: Optional[float] = None
    airbags: Optional[int] = None
    features: list[str] = []
    pros: list[str] = []
    cons: list[str] = []
    best_for: list[str] = []
    image_url: Optional[str] = None


class CarFilters(BaseModel):
    """Query parameters for filtering car listings."""
    segment: Optional[str] = None
    fuel_type: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    body_type: Optional[str] = None
    transmission: Optional[str] = None
    min_safety: Optional[float] = None
    seating: Optional[int] = None


# ---------------------------------------------------------------------------
# Advisor schemas — these power the AI recommendation engine
# ---------------------------------------------------------------------------

class UserNeeds(BaseModel):
    """
    Captures what the buyer cares about. This is the INPUT to the AI advisor.

    Design note: We ask about lifestyle, not specs. A confused buyer doesn't
    know they want "1.5L turbo" — they know they want "something peppy for
    highway overtakes." The AI translates lifestyle to specs.
    """
    budget_min: float = Field(description="Minimum budget in lakhs")
    budget_max: float = Field(description="Maximum budget in lakhs")
    primary_use: str = Field(description="Main use case: daily_commute, highway_touring, family, off_road, city_driving")
    family_size: int = Field(default=2, description="Number of regular occupants")
    priorities: list[str] = Field(
        description="Ranked list of what matters most: safety, mileage, features, comfort, performance, space, resale_value, low_maintenance"
    )
    fuel_preference: Optional[str] = Field(default=None, description="Preferred fuel: petrol, diesel, electric, hybrid, no_preference")
    transmission_preference: Optional[str] = Field(default=None, description="manual, automatic, no_preference")
    must_haves: list[str] = Field(default=[], description="Non-negotiable features: sunroof, adas, 4x4, 7_seats, etc.")
    dealbreakers: list[str] = Field(default=[], description="Things to avoid: no_diesel, no_cvt, etc.")


class DimensionScores(BaseModel):
    """Radar chart scores for a single car on buyer-relevant dimensions."""
    value: int = Field(ge=0, le=100)
    safety: int = Field(ge=0, le=100)
    comfort: int = Field(ge=0, le=100)
    performance: int = Field(ge=0, le=100)
    fuel_efficiency: int = Field(ge=0, le=100)
    features: int = Field(ge=0, le=100)


class CarRecommendation(BaseModel):
    """A single AI-generated recommendation with reasoning."""
    car_id: int
    match_score: int = Field(ge=0, le=100)
    reasoning: str
    pros: list[str]
    cons: list[str]
    scores: DimensionScores


class RecommendationResponse(BaseModel):
    """Full response from the recommendation engine."""
    recommendations: list[CarRecommendation]
    summary: str = Field(description="1-2 sentence overview of recommendations")


class CompareRequest(BaseModel):
    """Request to compare specific cars given user context."""
    car_ids: list[int] = Field(min_length=2, max_length=4)
    user_needs: Optional[UserNeeds] = None


class CompareInsight(BaseModel):
    """AI-generated comparison insight for a single car."""
    car_id: int
    verdict: str
    strengths_vs_others: list[str]
    weaknesses_vs_others: list[str]


class CompareResponse(BaseModel):
    """Full comparison response."""
    insights: list[CompareInsight]
    recommendation: str
    summary: str


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(description="user or assistant")
    content: str


class ChatRequest(BaseModel):
    """Chat request with conversation history and buyer context."""
    message: str
    history: list[ChatMessage] = []
    user_needs: Optional[UserNeeds] = None
    shortlisted_car_ids: list[int] = []


class ChatResponse(BaseModel):
    """Chat response from the AI advisor."""
    reply: str


# ---------------------------------------------------------------------------
# Shortlist
# ---------------------------------------------------------------------------

class ShortlistItem(BaseModel):
    session_id: str
    car_id: int
