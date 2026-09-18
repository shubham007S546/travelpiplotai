# TravelPilot AI 🧭
**Constraint-Aware Multi-Agent Travel Planning & Real-Time Travel Assistance System**

TravelPilot AI is a research-oriented multi-agent travel planning framework built using **LangGraph**, **Pydantic v2**, and **Streamlit**. It solves the problems of hallucinated prices, impossible travel schedules, and budget violations by enforcing deterministic arithmetic, verified evidence provenance, and automated replanning.

---

## 🚀 Key Features

1. **Zero-Hallucination Evidence Provenance:**
   Every factual claim (fare, tariff, location, schedule) is tagged with verifiable evidence and categorized into a 6-tier reliability hierarchy (from Official Gov Portals to Provider APIs).
2. **Deterministic Constraint Engine:**
   Budget arithmetic, distance calculations, and time feasibility are evaluated in pure Python code rather than left to LLM guesswork.
3. **Live Free API Integrations Out of the Box:**
   - **Open-Meteo:** Real-time 7-day weather forecasts and temperature without requiring any API keys.
   - **Frankfurter:** Live foreign exchange rate conversion.
4. **Hybrid Live API & Mock Fallback:**
   Supports live API keys (`GROQ_API_KEY`, `GEMINI_API_KEY`, `TAVILY_API_KEY`, `SERPAPI_API_KEY`, `AMADEUS_CLIENT_ID`, `OPENROUTESERVICE_API_KEY`) in `.env`. If a key is not provided, the service seamlessly falls back to high-fidelity structured data without crashing.
5. **Dynamic Re-Planning Loop:**
   If a plan violates a hard constraint (e.g. over budget or conflicting opening hours), the Re-Planner agent repairs the itinerary (up to 3 iterations) before user presentation.
6. **Local Mobility Trade-offs:**
   Recommends walking vs local bus vs auto/cab with explicit time and money trade-off explanations.
7. **24x7 Safety & Emergency Grid:**
   Maps nearby hospitals, pharmacies, police stations, ATMs, and transit hubs for every destination.

---

## 🛠️ Quickstart Installation

### 1. Clone & Navigate to Repository
```bash
cd TravelPilotAI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env` (already done by default):
```bash
# Add your optional keys whenever ready:
# GROQ_API_KEY=...
# TAVILY_API_KEY=...
# SERPAPI_API_KEY=...
```
*(Note: TravelPilot AI runs immediately out of the box with realistic mock fallbacks and live Open-Meteo weather even without paid keys!)*

---

## 💻 Running the Streamlit UI

Launch the interactive dashboard:
```bash
streamlit run app.py
```

### Streamlit Pages:
- **1. Plan My Trip:** Natural language travel request input with quick sample buttons.
- **2. Trip Overview:** Feasibility badge (PASS/FAIL), total cost, remaining budget, and radar score chart.
- **3. Transport:** Outbound and return journey cards with provider tariffs and schedule links.
- **4. Accommodations:** Recommended stay, rating, nightly price, amenities, and evidence.
- **5. Itinerary:** Chronological timeline with transit legs, meal stops, and activity fees.
- **6. Budget Breakdown:** Interactive Plotly distribution bar chart and reserve margin table.
- **7. Local Safety & Essentials:** 24x7 emergency medical, police, pharmacy, and transit directory.
- **8. Agent Observability Trace:** Execution durations in milliseconds, tool calls, and status for all 12 agents.

---

## 🧪 Running Automated Tests

Run the full pytest suite (unit tests for budget, constraints, itinerary, grounding, and full pipeline integration):
```bash
pytest tests/ -v
```

---

## 📊 Running the Research Benchmark

Evaluate the system across the 12 research benchmark scenarios:
```bash
python research/evaluation.py
```
Outputs Constraint Satisfaction Rate (CSR), Budget Violation Rate (BVR), Grounded Claim Rate (GCR), and Replanning Success Rate (RSR).

---

## 📁 Repository Structure
```
TravelPilotAI/
├── app.py                     # Streamlit application entrypoint
├── models/                    # Pydantic v2 domain schemas (evidence, transport, stay, state)
├── agents/                    # 12 LangGraph agent nodes with telemetry
├── orchestration/             # StateGraph assembly, routing, and reducers
├── services/                  # Live APIs (Open-Meteo, Frankfurter, Tavily, SerpApi, Amadeus)
├── optimization/              # Deterministic budget, timetable, and constraint engines
├── verification/              # Grounding, temporal, spatial, and consistency audit checkers
├── ui/                        # Modular Streamlit page views
├── utils/                     # Structured logging, TTL caching, and helpers
├── tests/                     # Automated pytest suite
├── research/                  # Evaluation dataset, metrics, and experiments documentation
├── .env.example               # Environment variables template
└── requirements.txt           # Project dependencies
```
