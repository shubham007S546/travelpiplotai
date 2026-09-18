# TravelPilot AI: Architectural & Research Context

## 1. Executive Summary
**TravelPilot AI** is a constraint-aware, evidence-grounded multi-agent autonomous travel planning and real-time travel assistance framework. It addresses the fundamental flaw of generative LLM travel planners: factual hallucination, impossible transit velocities, and inaccurate budget arithmetic.

## 2. Core Operational Axiom
> **API / Web Data = Facts**  
> **LLM = Semantic Reasoning & Intent Parsing**  
> **Python Code = Deterministic Constraints & Spatio-Temporal Math**

The LLM is strictly prohibited from inventing fares, hotel rates, distances, opening hours, or geographic coordinates.

## 3. Architecture Overview
Built on **LangGraph** with a strongly-typed shared `TravelState`:
1. **Intent Agent:** Parses natural language into strongly-typed temporal and financial parameters.
2. **Place Resolution Agent:** Administrative hierarchy disambiguation, micro-rural flags, and mountain roadhead mapping.
3. **Concurrent Discovery Engine:** High-speed parallel fan-out (`ThreadPoolExecutor`, ~3.8x speedup) executing:
   - **Transport Agent:** Finds grounded intercity bus, rail, cab, and flight connections.
   - **Stay Agent:** Selects budget-matched lodging, verified homestays, and campsite/tent rentals.
   - **Food Agent:** Route-aligned breakfast, lunch, and dinner recommendations.
   - **Activity Agent:** Curates authentic attractions matching user interests with real entry fees.
   - **Safety & Services Agent:** Maps 24x7 emergency medical, police, ATMs, and live Open-Meteo weather.
4. **Route Verification Agent:** Cross-audits road distances and OSRM/ORS driving routes.
5. **Fare Verification Agent:** Evaluates stage-carriage bus formulas and provider tariffs.
6. **Local Mobility Agent:** Recommends intra-city transit trade-offs (walk vs local bus vs auto/cab).
7. **Trip Disruption Agent:** Real-time meteorological hazard detection (>20mm rain, snow, landslides) and automated detour advisories (e.g. NH-21 Mandi-Pandoh bypass).
8. **Budget Optimizer:** Pure-Python financial allocation and emergency reserve calculation.
9. **Itinerary Optimizer:** Chronological scheduler ensuring non-overlapping activities and transit buffers.
10. **Data Consistency Agent:** Validates cross-provider spatial and pricing agreement within 15% tolerance.
11. **Verification Agent:** Rigorous multi-criteria audit (CSR, BVR, GCR, confidence).
12. **Re-Planner Agent:** Dynamic self-healing repair loop (up to 3 cycles) resolving constraint failures.
13. **Finalizer Agent:** Formats verified dossiers and printable PDF travel passes.

## 4. Source Reliability Hierarchy
- **Tier 1:** Official Government / Tourism / Transport Portals (Weight: 1.0)
- **Tier 2:** Official Provider APIs (Amadeus, IRCTC, etc.) (Weight: 0.95)
- **Tier 3:** Structured Maps & Transit Matrices (Google Maps, ORS, OSRM) (Weight: 0.90)
- **Tier 4:** Trusted Travel Portals (TripAdvisor, Booking.com, Agoda) (Weight: 0.80)
- **Tier 5:** General Web Search (Tavily, News, Travel Blogs) (Weight: 0.65)
- **Tier 6:** Unverified LLM Inference (Weight: 0.25 — Strictly Disallowed for Facts)

## 5. Core Research & Engineering Novelties
1. **Deterministic Physics & Velocity Gating:** Rejection of super-human or physically impossible transit speeds ($v \le 95\text{ km/h}$ for buses on state roads).
2. **Tripartite Separation of Concerns:** Prohibits generative models from calculating money or inventing schedules.
3. **6-Tier Evidence Provenance:** Every factual claim carries an immutable cryptographic ledger entry.
4. **Zero-Fabrication Multimodal Image Grounding:** Replaces hallucinated stock photos with Google Images & YouTube on-site travel vlog thumbnails.
5. **Micro-Regional Topology & Ecotourism Modeling:** Native modeling of rural roadheads, trekking trailheads, shared sumos, and alpine tent rentals.
6. **Self-Healing Re-Planning State Machine:** Automated dynamic downgrades and schedule shifts when hard constraints fail.
7. **High-Speed Concurrent Discovery Fan-Out:** Independent domain retrievers run concurrently in thread pools with deterministic state reduction.
8. **Proactive Terrain & Weather Disruption Engine:** Real-time road disaster mitigation mapping live meteorological telemetry to active highway bypass corridors.
