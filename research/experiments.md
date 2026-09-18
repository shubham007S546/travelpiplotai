# Research Experiments & Theoretical Formulation

## 1. Title & Abstract
**Title:** *TravelPilot: A Constraint-Aware and Evidence-Grounded Multi-Agent Framework for End-to-End Travel Planning*

**Abstract:** Conventional Large Language Model (LLM) travel assistants frequently suffer from factual hallucinations, unrealistic spatio-temporal trajectories, and silent budget violations. We present **TravelPilot AI**, a multi-agent travel architecture structured around the tenet: *API/Web Data = Facts, LLM = Semantic Reasoning, Code = Deterministic Constraints*. The system decouples intent parsing, multi-modal transport discovery, lodging search, route-aware dining, and essential emergency services into specialized agents orchestrated via LangGraph. An internal verification loop with up to three re-planning cycles detects budget overflow, temporal collisions, and ungrounded claims, repairing itineraries deterministically before user presentation.

---

## 2. Research Hypotheses

- **H1 (Constraint Satisfaction):** A multi-agent travel planner with explicit deterministic constraint checking produces significantly higher Constraint Satisfaction Rate (CSR) than a monolithic LLM planner.
- **H2 (Evidence Grounding):** Binding all factual claims (tariffs, coordinates, operating hours) to a tiered evidence hierarchy reduces the Unsupported Recommendation Rate (URR) to near zero.
- **H3 (Verification & Replanning):** Dedicated spatio-temporal audit and automated replanning stages repair violated itineraries that single-pass generative architectures fail on.
- **H4 (Budget Optimality):** Deterministic algorithmic budget allocation prevents budget violations (BVR = 0%) while preserving mandatory travel safety and accommodation.
- **H5 (Agent Specialization):** Specialized agents coordinated through a strongly-typed shared state (`TravelState`) outperform single general-purpose agents in recommendation diversity and factual reliability.

---

## 3. Related Work & Research Gap Analysis

| System | External Data Grounding | Hard Budget Constraints | Spatio-Temporal Verification | Dynamic Replanning | Local Assistance Services |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Monolithic LLM (GPT-4 / LLaMA-3)** | ❌ None | ❌ Prone to math errors | ❌ Fictional timings | ❌ None | ❌ Hallucinated |
| **TravelPlanner Benchmark (2024)** | ⚠️ Static Sandbox | ⚠️ Checked ex-post | ⚠️ Heuristic | ❌ None | ❌ Absent |
| **HiMAP-Travel / TripMind** | ⚠️ Limited APIs | ⚠️ Partial | ⚠️ Partial | ⚠️ Single-pass | ❌ Absent |
| **TravelPilot AI (Proposed)** | ✅ Tier 1-5 Provenance | ✅ Deterministic Math | ✅ Spatio-Temporal Matrix | ✅ Up to 3 Loops | ✅ 24x7 Emergency Grid |

---

## 4. Ablation Study Design (Baselines A through F)

To isolate the contributions of each architectural component, the benchmark runs across six configurations:

- **Configuration A:** LLM Only (Zero-shot monolithic generation)
- **Configuration B:** LLM + Search Retrieval (RAG baseline)
- **Configuration C:** Multi-Agent Pipeline without Deterministic Constraints
- **Configuration D:** Multi-Agent + Deterministic Budget & Temporal Constraints
- **Configuration E:** Multi-Agent + Constraints + Verification Audit Agent
- **Configuration F (Full TravelPilot AI):** Multi-Agent + Constraints + Verification + Automated Replanning Loop

---

## 5. Evaluation Metrics

1. **Constraint Satisfaction Rate (CSR):**
   $$\text{CSR} = \frac{\text{Satisfied Constraints}}{\text{Total Constraints}}$$
2. **Budget Violation Rate (BVR):**
   $$\text{BVR} = \frac{\text{Plans Exceeding Budget}}{\text{Total Plans}}$$
3. **Grounded Claim Rate (GCR):**
   $$\text{GCR} = \frac{\text{Verifiable Claims with Provenance}}{\text{Total Factual Claims}}$$
4. **Unsupported Recommendation Rate (URR):**
   $$\text{URR} = \frac{\text{Ungrounded Recommendations}}{\text{Total Recommendations}}$$
5. **Replanning Success Rate (RSR):**
   $$\text{RSR} = \frac{\text{Successfully Repaired Infeasible Plans}}{\text{Total Initially Infeasible Plans}}$$
