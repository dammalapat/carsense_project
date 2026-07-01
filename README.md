# CarSense — AI-Powered Car Buying Advisor

> **Take-home assignment for Software Engineer — AI-Native, CarDekho Group**

CarSense helps a confused car buyer go from *"I have no idea what to buy"* to *"I'm confident about my shortlist"* in under 3 minutes. Instead of drowning buyers in filter dropdowns and spec sheets, it asks about their **life** — then uses AI to explain which cars fit, and why.

**Live URL**: https://car-sense-pranav.netlify.app/ 
**Screen Recording**: [insert Loom/YouTube link]

---

## What I Built and Why

### The product insight

Car buying is overwhelming because of **information overload**, not information scarcity. Every car site gives you 40 filter parameters and 200 results. That doesn't help a confused buyer — it paralyzes them.

The core design decision: **ask about lifestyle, not specifications.** A buyer doesn't know they want a 1.5L turbo — they know they need "something peppy for highway overtakes." CarSense translates lifestyle to specs using AI, and crucially, *explains the reasoning* so the buyer builds confidence rather than just trusting a black-box score.

### What it does (end-to-end flow)

1. **Needs Discovery Wizard** — 5-step guided questionnaire: Budget → Usage → Priorities → Preferences → Must-haves. Each step is a single focused question with tappable options. No typing required.

2. **AI-Ranked Recommendations** — Claude analyzes the buyer's needs against 30 cars from the Indian market and returns personalized recommendations with:
   - Match score (0–100) reflecting fit for *this specific buyer*
   - AI-generated reasoning explaining *why* each car fits their life
   - Radar chart visualizing scores across 6 dimensions (Value, Safety, Comfort, Performance, Fuel Efficiency, Features)
   - Pros/cons tailored to the buyer's stated priorities

3. **AI-Powered Comparison** — Select 2–4 cars for side-by-side comparison. The AI generates:
   - Direct recommendation (opinionated, not wishy-washy)
   - Per-car verdicts: who should buy this car
   - Strengths/weaknesses relative to the other cars in the comparison (not just general pros/cons)

4. **Contextual Chat** — Follow-up questions answered by Claude with full context of the buyer's needs and shortlisted cars. Ask "Is diesel still worth it?" or "Which has better resale?" and get answers grounded in the specific cars being considered.

### What I deliberately cut

- **User accounts / auth** — Zero value for a "help me decide" flow. Session-based shortlisting is sufficient.
- **Car images** — Would require either scraping (legal risk) or placeholder images (low value). Text + data is cleaner.
- **Advanced filtering page** — This is the "old way" the brief is pushing against. The wizard IS the filter.
- **Price prediction / EMI calculator** — Useful but not core to the "confused → confident" mission.
- **Admin panel / CMS** — Seed data in code is simpler and sufficient for an MVP.
- **Review aggregation** — Would need real data. Simulated reviews add no signal.

---

## Tech Stack and Why

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Backend** | Python + FastAPI | Best ecosystem for AI integration (Anthropic SDK is Python-first). Async support matches the I/O-bound nature of LLM calls. |
| **AI** | Claude (claude-sonnet-4-20250514) | Strong structured output, excellent reasoning about trade-offs, good at following complex prompts. |
| **Database** | SQLite (aiosqlite) | Zero external dependencies. 30 cars fit in memory. A take-home shouldn't need PostgreSQL. Swappable later. |
| **Frontend** | React 18 + TypeScript + Vite | Industry standard. TypeScript catches schema mismatches between frontend types and backend models. Vite for fast dev. |
| **Styling** | Tailwind CSS | Rapid UI development without CSS file proliferation. Utility classes are readable and maintainable. |
| **Deployment** | Docker Compose | One-command local setup (`docker compose up`). Frontend deployable to Netlify, backend to Railway. |

### Why NOT Next.js?

I considered it for the SSR benefits, but the tradeoffs didn't favor it here: (1) the app is a single flow, not SEO-dependent, (2) API routes would need rewriting for separate backend deployment, (3) FastAPI's async + Pydantic gives better API ergonomics than Next API routes.

---

## AI Tools Usage — What I Delegated vs. Did Manually

### Delegated to AI (Claude Code)
- **Boilerplate generation** — Project scaffolding, config files, Dockerfile templates
- **Seed data expansion** — I specified ~5 cars with full specs, then asked Claude to generate the remaining 25 following the same pattern with accurate Indian market data
- **CSS utility classes** — Tailwind class combinations for component styling
- **Type mirroring** — Generating TypeScript interfaces from Pydantic models

### Done manually (AI-assisted but human-directed)
- **Product scoping** — The "lifestyle-first, not spec-first" approach was my design decision
- **AI prompt engineering** — The recommendation/comparison prompts went through 3 iterations. Key insight: telling Claude to "be honest about trade-offs" and "score should reflect fit for THIS buyer" dramatically improved output quality
- **Architecture decisions** — Separation of advisor.py from main.py, fallback scoring algorithm, the wizard step design
- **Data model design** — The `best_for` tags, dimension scoring system, and how user priorities map to car attributes
- **Component structure** — Which UI pieces needed to be separate components vs. inline

### Where AI helped most
- Speed on the "wide" work — generating 30 car entries with accurate specs would have taken 45+ minutes manually
- CSS — Tailwind combinations that look professional without pixel-pushing

### Where AI got in the way
- **Over-engineering** — First pass had Redux, React Query, and separate router modules. I stripped it down to simple state lifting.
- **Generic prompts** — Early Claude prompts returned corporate-sounding recommendations ("The Hyundai Creta offers a compelling value proposition..."). Had to iterate toward more natural, opinionated language.
- **Hallucinated specs** — Some car specifications needed manual verification. I kept the seed data I could verify.

---

## If I Had Another 4 Hours

1. **Real-time search** — Full-text search across the car catalog with instant results. The backend already supports it; needs a frontend search UI.

2. **Ownership cost calculator** — Monthly EMI + insurance + fuel cost based on the buyer's commute distance. This is high-value and differentiating.

3. **Test drive scheduler** — Integration with a booking flow. Even a mock version would demonstrate product thinking.

4. **Collaborative shortlisting** — Share your shortlist via a link. Many car purchases are joint decisions (couples, families).

5. **Feedback loop** — "Was this recommendation helpful?" on each card. Could fine-tune the scoring algorithm over time.

6. **More comprehensive car data** — 100+ cars, real images, actual user review summaries. Would make the AI recommendations significantly more useful.

---

## Project Structure

```
carsense/
├── backend/
│   ├── main.py            # FastAPI app, all route handlers
│   ├── database.py         # SQLite schema, connection, 30-car seed data
│   ├── models.py           # Pydantic request/response schemas
│   ├── advisor.py          # AI engine: recommendations, comparison, chat
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Root component, phase-based routing
│   │   ├── api.ts           # Typed API client
│   │   ├── types.ts         # TypeScript interfaces + constants
│   │   └── components/
│   │       ├── Header.tsx       # Navigation header
│   │       ├── Landing.tsx      # Hero page + value proposition
│   │       ├── Wizard.tsx       # 5-step needs discovery
│   │       ├── Results.tsx      # Recommendation cards + score display
│   │       ├── RadarChart.tsx   # SVG radar chart (zero dependencies)
│   │       ├── CompareDrawer.tsx# Side-by-side with AI insights
│   │       └── ChatPanel.tsx    # Contextual AI chat
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
├── docker-compose.yml       # One-command local setup
├── .env.example
└── README.md
```

---

## Running Locally

### Option A: Docker (recommended — one command)

```bash
# 1. Clone and enter
git clone <repo-url> && cd carsense

# 2. Set your API key (optional — app works without it using fallback scoring)
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Run
docker compose up --build

# Frontend: http://localhost:5173
# Backend:  http://localhost:8000/docs (Swagger UI)
```

### Option B: Manual setup

```bash
# Terminal 1 — Backend
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_key_here  # optional
python main.py
# → Running on http://localhost:8000

# Terminal 2 — Frontend
cd frontend
npm install
npm run dev
# → Running on http://localhost:5173
```

### Option C: Deploy

- **Frontend** → Netlify: Connect GitHub repo, set build command `cd frontend && npm run build`, publish directory `frontend/dist`, env var `VITE_API_URL=https://your-backend.railway.app`
- **Backend** → Railway: Connect GitHub repo, set root directory `backend`, env var `ANTHROPIC_API_KEY`

---

## Architecture Decisions Worth Noting

1. **Fallback scoring** — The app works WITHOUT an API key. `advisor.py` contains a full deterministic scoring algorithm that evaluates cars against user priorities. This means evaluators can test the app immediately without providing an API key.

2. **Structured AI output** — Claude is prompted to return JSON, not prose. This lets us render the response in a structured UI (radar charts, score badges, pro/con lists) rather than just dumping text.

3. **Context-aware chat** — The chat endpoint receives the buyer's needs AND their shortlisted cars as system context. This means Claude can reference specific car specs without the user having to repeat themselves.

4. **No client-side routing library** — The app uses a simple `phase` state variable instead of React Router. Three phases, linear flow — a router would be ceremony without value.

5. **Custom SVG radar chart** — Zero-dependency radar chart in ~80 lines. No charting library needed for a single visualization type.
