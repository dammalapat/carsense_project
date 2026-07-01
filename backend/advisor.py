"""
advisor.py — AI-powered car recommendation engine using Claude.

This is the heart of CarSense. Instead of rule-based filtering, we use Claude
to reason about *why* a car fits a buyer's lifestyle. The AI sees both the
buyer's needs and the car specs, then generates personalized explanations.

Architecture decision: We send structured car data + buyer context to Claude
and ask for JSON output. This is more robust than trying to parse free-text.
The prompts are designed to elicit honest trade-off analysis, not just hype.

Fallback: If no API key is set, we use a deterministic scoring algorithm
so the app remains functional for demo/evaluation purposes.
"""

import json
import os
from typing import Optional

from anthropic import AsyncAnthropic

from models import (
    UserNeeds, CarRecommendation, RecommendationResponse,
    CompareRequest, CompareResponse, CompareInsight,
    ChatRequest, ChatResponse, DimensionScores
)

# Initialize client — will be None if no API key is set
_client: Optional[AsyncAnthropic] = None
MODEL = "claude-sonnet-4-20250514"


def get_client() -> Optional[AsyncAnthropic]:
    global _client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key and _client is None:
        _client = AsyncAnthropic(api_key=api_key)
    return _client


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

RECOMMEND_SYSTEM = """You are CarSense, an expert Indian car market advisor.
You help confused buyers find their perfect car by analyzing their lifestyle
needs against available options. You are honest about trade-offs — you never
oversell a car. You explain in simple terms a non-technical buyer understands.

IMPORTANT: Respond with ONLY valid JSON, no markdown fences, no preamble."""

RECOMMEND_USER = """A car buyer needs help choosing. Here's what they told us:

BUYER PROFILE:
- Budget: ₹{budget_min}L – ₹{budget_max}L
- Primary use: {primary_use}
- Family size: {family_size} people
- Top priorities (ranked): {priorities}
- Fuel preference: {fuel_preference}
- Transmission: {transmission_preference}
- Must-haves: {must_haves}
- Dealbreakers: {dealbreakers}

AVAILABLE CARS IN BUDGET:
{cars_json}

Analyze each car against this buyer's specific needs. Return a JSON object:
{{
  "recommendations": [
    {{
      "car_id": <int>,
      "match_score": <0-100, be honest — 100 is rare>,
      "reasoning": "<2-3 sentences explaining why this car fits THIS buyer's life>",
      "pros": ["<3 pros relevant to this buyer's priorities>"],
      "cons": ["<2 honest cons this buyer should know>"],
      "scores": {{
        "value": <0-100>,
        "safety": <0-100>,
        "comfort": <0-100>,
        "performance": <0-100>,
        "fuel_efficiency": <0-100>,
        "features": <0-100>
      }}
    }}
  ],
  "summary": "<1-2 sentence overview: what the buyer should focus on given their needs>"
}}

Rules:
1. Return top 5 cars, ranked by match_score.
2. match_score should reflect fit for THIS buyer, not general quality.
3. Pros/cons must be specific to the buyer's stated priorities.
4. Be honest. If no car is perfect, say so.
5. Scores should vary meaningfully — not everything is 70-80."""

COMPARE_SYSTEM = """You are CarSense, comparing specific cars for a buyer.
Be direct and opinionated — the buyer wants to make a decision, not read a spec sheet.
Respond with ONLY valid JSON, no markdown fences."""

COMPARE_USER = """Compare these cars for a buyer:

{buyer_context}

CARS TO COMPARE:
{cars_json}

Return JSON:
{{
  "insights": [
    {{
      "car_id": <int>,
      "verdict": "<1 sentence: who should buy this car>",
      "strengths_vs_others": ["<what this car does better than the others in this comparison>"],
      "weaknesses_vs_others": ["<where it falls short compared to others here>"]
    }}
  ],
  "recommendation": "<direct recommendation: which car and why, given this buyer>",
  "summary": "<key trade-off the buyer needs to think about>"
}}"""

CHAT_SYSTEM = """You are CarSense, a friendly car buying advisor for the Indian market.

You have access to the buyer's profile and their shortlisted cars. Answer questions
naturally and helpfully. Key behaviors:
- Be conversational, not robotic
- Give specific, actionable advice
- When asked about a specific car, reference real specs from the data provided
- Be honest about limitations — if you don't know, say so
- Keep responses concise — 2-3 paragraphs max
- Use ₹ for prices, mention lakhs
- Don't hedge excessively — give your opinion when asked"""


# ---------------------------------------------------------------------------
# Recommendation engine
# ---------------------------------------------------------------------------

async def get_recommendations(
    needs: UserNeeds, cars: list[dict]
) -> RecommendationResponse:
    """Generate AI-powered car recommendations based on buyer needs."""
    client = get_client()

    # Filter cars within budget (with 10% buffer for negotiation)
    budget_cars = [
        c for c in cars
        if c["price_lakh_min"] <= needs.budget_max * 1.1
        and c["price_lakh_max"] >= needs.budget_min * 0.9
    ]

    if not budget_cars:
        return RecommendationResponse(
            recommendations=[],
            summary="No cars found in your budget range. Try adjusting your budget."
        )

    if client:
        return await _ai_recommend(client, needs, budget_cars)
    else:
        return _fallback_recommend(needs, budget_cars)


async def _ai_recommend(
    client: AsyncAnthropic, needs: UserNeeds, cars: list[dict]
) -> RecommendationResponse:
    """Use Claude to generate personalized recommendations."""
    # Prepare car data — strip internal fields, keep what the AI needs
    cars_for_prompt = []
    for c in cars:
        cars_for_prompt.append({
            "id": c["id"], "make": c["make"], "model": c["model"],
            "variant": c["variant"], "segment": c["segment"],
            "price_range": f"₹{c['price_lakh_min']}L – ₹{c['price_lakh_max']}L",
            "fuel": c["fuel_type"], "transmission": c["transmission"],
            "power_bhp": c["power_bhp"], "mileage_kmpl": c["mileage_kmpl"],
            "range_km": c["range_km"], "seating": c["seating"],
            "boot_space_l": c["boot_space_l"],
            "safety_rating": c["safety_rating"], "airbags": c["airbags"],
            "ground_clearance_mm": c["ground_clearance_mm"],
            "features": json.loads(c["features"]) if isinstance(c["features"], str) else c["features"],
            "known_pros": json.loads(c["pros"]) if isinstance(c["pros"], str) else c["pros"],
            "known_cons": json.loads(c["cons"]) if isinstance(c["cons"], str) else c["cons"],
            "best_for": json.loads(c["best_for"]) if isinstance(c["best_for"], str) else c["best_for"],
        })

    user_prompt = RECOMMEND_USER.format(
        budget_min=needs.budget_min,
        budget_max=needs.budget_max,
        primary_use=needs.primary_use,
        family_size=needs.family_size,
        priorities=", ".join(needs.priorities),
        fuel_preference=needs.fuel_preference or "no preference",
        transmission_preference=needs.transmission_preference or "no preference",
        must_haves=", ".join(needs.must_haves) if needs.must_haves else "none",
        dealbreakers=", ".join(needs.dealbreakers) if needs.dealbreakers else "none",
        cars_json=json.dumps(cars_for_prompt, indent=2),
    )

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=2000,
            system=RECOMMEND_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        return RecommendationResponse(**data)
    except Exception as e:
        print(f"AI recommendation failed: {e}, falling back to deterministic scoring")
        return _fallback_recommend(needs, cars)


def _fallback_recommend(needs: UserNeeds, cars: list[dict]) -> RecommendationResponse:
    """Deterministic scoring when no API key is available."""
    scored = []
    for car in cars:
        score = _score_car(car, needs)
        best_for = json.loads(car["best_for"]) if isinstance(car["best_for"], str) else car["best_for"]
        pros = json.loads(car["pros"]) if isinstance(car["pros"], str) else car["pros"]
        cons = json.loads(car["cons"]) if isinstance(car["cons"], str) else car["cons"]

        scored.append(CarRecommendation(
            car_id=car["id"],
            match_score=score,
            reasoning=_generate_reasoning(car, needs, score),
            pros=pros[:3],
            cons=cons[:2],
            scores=_compute_dimension_scores(car, needs),
        ))

    scored.sort(key=lambda r: r.match_score, reverse=True)
    top = scored[:5]

    return RecommendationResponse(
        recommendations=top,
        summary=f"Based on your priorities ({', '.join(needs.priorities[:2])}), "
                f"we found {len(top)} strong matches in your ₹{needs.budget_min}–{needs.budget_max}L range."
    )


def _score_car(car: dict, needs: UserNeeds) -> int:
    """Rule-based scoring: 0–100 based on how well the car fits the buyer."""
    score = 50  # baseline
    best_for = json.loads(car["best_for"]) if isinstance(car["best_for"], str) else car["best_for"]

    # Budget fit (±10 points)
    mid_budget = (needs.budget_min + needs.budget_max) / 2
    mid_price = (car["price_lakh_min"] + car["price_lakh_max"]) / 2
    if needs.budget_min <= mid_price <= needs.budget_max:
        score += 10
    elif mid_price > needs.budget_max * 1.05:
        score -= 10

    # Use-case alignment (up to +15)
    use_map = {
        "daily_commute": ["daily_commute", "city_driving", "fuel_efficiency"],
        "highway_touring": ["highway_touring", "long_drives", "comfort"],
        "family": ["family", "7_seater", "space", "safety_first"],
        "off_road": ["off_road", "rough_roads"],
        "city_driving": ["city_driving", "parking_ease", "first_car"],
        "enthusiast": ["enthusiast", "performance"],
    }
    relevant_tags = use_map.get(needs.primary_use, [needs.primary_use])
    overlap = len(set(relevant_tags) & set(best_for))
    score += min(overlap * 5, 15)

    # Priority alignment (up to +15)
    for i, priority in enumerate(needs.priorities[:3]):
        weight = 3 - i  # first priority worth more
        if priority == "safety" and car.get("safety_rating", 0) and car["safety_rating"] >= 4:
            score += weight * 3
        elif priority == "mileage" and car.get("mileage_kmpl", 0) and car["mileage_kmpl"] > 18:
            score += weight * 3
        elif priority == "performance" and car.get("power_bhp", 0) and car["power_bhp"] > 120:
            score += weight * 3
        elif priority == "space" and car.get("seating", 5) >= needs.family_size + 1:
            score += weight * 3
        elif priority == "features" and "features" in car.get("best_for", []):
            score += weight * 2

    # Fuel preference (+5 / -10)
    if needs.fuel_preference and needs.fuel_preference != "no_preference":
        if needs.fuel_preference.lower() in car["fuel_type"].lower():
            score += 5
        elif car["fuel_type"].lower() == "both":
            score += 3
        else:
            score -= 10

    # Seating needs
    if needs.family_size > 5 and car["seating"] < 7:
        score -= 15
    elif needs.family_size <= 2 and car["seating"] >= 7:
        score -= 5  # paying for seats you don't need

    # Safety bonus
    if car.get("safety_rating") and car["safety_rating"] >= 5:
        score += 5

    return max(0, min(100, score))


def _compute_dimension_scores(car: dict, needs: UserNeeds) -> DimensionScores:
    """Compute radar chart dimension scores for a car."""
    # Value: inverse of price relative to features
    price = (car["price_lakh_min"] + car["price_lakh_max"]) / 2
    features_list = json.loads(car["features"]) if isinstance(car["features"], str) else car["features"]
    value = min(100, int(60 + len(features_list) * 3 - price * 1.5))

    safety = min(100, int((car.get("safety_rating", 3) / 5) * 80 + (car.get("airbags", 2) / 7) * 20))
    comfort = min(100, int(50 + (car.get("boot_space_l", 300) / 600) * 30 + len(features_list) * 2))
    performance = min(100, int((car.get("power_bhp", 80) / 200) * 80 + 10))

    if car["fuel_type"] == "Electric":
        fuel_eff = min(100, int((car.get("range_km", 300) / 500) * 90))
    else:
        fuel_eff = min(100, int((car.get("mileage_kmpl", 15) / 25) * 90))

    features_score = min(100, int(len(features_list) * 12))

    return DimensionScores(
        value=max(10, value),
        safety=max(10, safety),
        comfort=max(10, comfort),
        performance=max(10, performance),
        fuel_efficiency=max(10, fuel_eff),
        features=max(10, features_score),
    )


def _generate_reasoning(car: dict, needs: UserNeeds, score: int) -> str:
    """Generate a human-readable reason for the recommendation."""
    name = f"{car['make']} {car['model']}"
    use = needs.primary_use.replace("_", " ")
    priority = needs.priorities[0] if needs.priorities else "overall value"

    if score >= 75:
        return (f"The {name} is a strong match for your {use} needs. "
                f"It scores well on {priority}, which you ranked highest.")
    elif score >= 55:
        return (f"The {name} is a solid option worth considering. "
                f"While not perfect on every front, it balances {priority} with your budget.")
    else:
        return (f"The {name} is a stretch for your needs but included for completeness. "
                f"Consider it only if other priorities shift.")


# ---------------------------------------------------------------------------
# Comparison engine
# ---------------------------------------------------------------------------

async def compare_cars(
    cars: list[dict], user_needs: Optional[UserNeeds] = None
) -> CompareResponse:
    """Generate AI-powered comparison insights."""
    client = get_client()

    if client:
        return await _ai_compare(client, cars, user_needs)
    else:
        return _fallback_compare(cars, user_needs)


async def _ai_compare(
    client: AsyncAnthropic, cars: list[dict], user_needs: Optional[UserNeeds]
) -> CompareResponse:
    """Use Claude for detailed comparison."""
    buyer_context = "No specific buyer profile provided — give general comparison."
    if user_needs:
        buyer_context = (
            f"Budget: ₹{user_needs.budget_min}–{user_needs.budget_max}L, "
            f"Use: {user_needs.primary_use}, "
            f"Priorities: {', '.join(user_needs.priorities[:3])}"
        )

    cars_for_prompt = []
    for c in cars:
        cars_for_prompt.append({
            "id": c["id"], "name": f"{c['make']} {c['model']} {c['variant']}",
            "price_range": f"₹{c['price_lakh_min']}L – ₹{c['price_lakh_max']}L",
            "fuel": c["fuel_type"], "power_bhp": c["power_bhp"],
            "mileage_kmpl": c["mileage_kmpl"], "safety_rating": c["safety_rating"],
            "airbags": c["airbags"], "seating": c["seating"],
            "boot_space_l": c["boot_space_l"],
            "features": json.loads(c["features"]) if isinstance(c["features"], str) else c["features"],
            "pros": json.loads(c["pros"]) if isinstance(c["pros"], str) else c["pros"],
            "cons": json.loads(c["cons"]) if isinstance(c["cons"], str) else c["cons"],
        })

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=COMPARE_SYSTEM,
            messages=[{"role": "user", "content": COMPARE_USER.format(
                buyer_context=buyer_context,
                cars_json=json.dumps(cars_for_prompt, indent=2),
            )}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        data = json.loads(raw)
        return CompareResponse(**data)
    except Exception as e:
        print(f"AI comparison failed: {e}")
        return _fallback_compare(cars, user_needs)


def _fallback_compare(cars: list[dict], user_needs: Optional[UserNeeds]) -> CompareResponse:
    """Deterministic comparison fallback."""
    insights = []
    for car in cars:
        pros = json.loads(car["pros"]) if isinstance(car["pros"], str) else car["pros"]
        cons = json.loads(car["cons"]) if isinstance(car["cons"], str) else car["cons"]
        insights.append(CompareInsight(
            car_id=car["id"],
            verdict=f"The {car['make']} {car['model']} is best for buyers who prioritize {pros[0].lower() if pros else 'overall balance'}.",
            strengths_vs_others=pros[:2],
            weaknesses_vs_others=cons[:2],
        ))

    names = [f"{c['make']} {c['model']}" for c in cars]
    return CompareResponse(
        insights=insights,
        recommendation=f"Among {', '.join(names)}, each has distinct strengths. Consider test-driving your top 2.",
        summary="These cars target similar buyers but differ in key areas. Your priorities should guide the choice.",
    )


# ---------------------------------------------------------------------------
# Chat engine
# ---------------------------------------------------------------------------

async def chat(
    request: ChatRequest, all_cars: list[dict]
) -> ChatResponse:
    """AI-powered contextual chat about cars."""
    client = get_client()

    if not client:
        return ChatResponse(
            reply="AI chat requires an API key. Set ANTHROPIC_API_KEY to enable "
                  "intelligent conversations. In the meantime, check the car cards "
                  "for detailed specs and recommendations!"
        )

    # Build context from shortlisted cars
    shortlisted = [c for c in all_cars if c["id"] in request.shortlisted_car_ids]
    car_context = ""
    if shortlisted:
        car_context = "\n\nBUYER'S SHORTLISTED CARS:\n"
        for c in shortlisted:
            features = json.loads(c["features"]) if isinstance(c["features"], str) else c["features"]
            car_context += (
                f"- {c['make']} {c['model']} ({c['variant']}): "
                f"₹{c['price_lakh_min']}–{c['price_lakh_max']}L, "
                f"{c['fuel_type']}, {c['power_bhp']}bhp, "
                f"{c.get('mileage_kmpl', 'N/A')}kmpl, "
                f"Safety: {c.get('safety_rating', 'N/A')}★, "
                f"Features: {', '.join(features[:5])}\n"
            )

    buyer_context = ""
    if request.user_needs:
        n = request.user_needs
        buyer_context = (
            f"\n\nBUYER PROFILE: Budget ₹{n.budget_min}–{n.budget_max}L, "
            f"Use: {n.primary_use}, Family: {n.family_size}, "
            f"Priorities: {', '.join(n.priorities[:3])}"
        )

    system = CHAT_SYSTEM + car_context + buyer_context

    messages = [{"role": m.role, "content": m.content} for m in request.history]
    messages.append({"role": "user", "content": request.message})

    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=600,
            system=system,
            messages=messages,
        )
        return ChatResponse(reply=response.content[0].text)
    except Exception as e:
        return ChatResponse(reply=f"Sorry, I hit a snag: {str(e)}. Try again?")
