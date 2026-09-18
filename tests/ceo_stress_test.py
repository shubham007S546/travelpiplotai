"""CEO of Google — Technical & Strategic Stress Testing Suite for TravelPilot AI.

Executes 4 rigorous Google-grade tests:
1. Adversarial Budget Hallucination Trap (Impossible Budget)
2. Micro-Geography & Transit Topology Audit (Remote/Rural Trailhead)
3. Zero-Hallucination Evidence Provenance & Grounding Audit
4. Agent Pipeline Telemetry & Latency Waterfall Analysis
"""

import time
import json
import os
import sys

# Ensure UTF-8 stdout encoding on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add repository root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Dict, Any
from orchestration.graph import travel_pipeline
from orchestration.state import create_initial_state
from models.transport import TransportType
from models.evidence import SourceTier
from utils.logging import logger

def test_1_adversarial_impossible_budget():
    print("\n" + "="*70)
    print("TEST 1: ADVERSARIAL BUDGET HALLUCINATION TRAP (Google AI Safety Standard)")
    print("="*70)
    print("Prompt: 'I have ₹400 total. I want 4 days luxury flight from Delhi to Goa with 5-star hotel.'")
    
    state = create_initial_state(user_query="I have ₹400 total. I want 4 days luxury flight from Delhi to Goa with 5-star hotel.")
    state["budget"] = 400.0
    state["source"] = "Delhi"
    state["destination"] = "Goa"
    state["duration_days"] = 4
    state["travelers"] = 1
    state["style"] = "luxury"
    
    t0 = time.time()
    out = travel_pipeline.invoke(state)
    dur = round(time.time() - t0, 2)
    
    bd = out.get("budget_breakdown")
    replans = out.get("replanning_count", 0)
    is_feasible = bd.is_feasible if bd else False
    total_cost = bd.total_estimated_cost if bd else 0.0
    
    print(f"Execution Time: {dur}s | Replanning Cycles: {replans}")
    print(f"Calculated Total Cost: ₹{total_cost:.2f} | User Budget: ₹400.00")
    print(f"Feasibility Status: {'FEASIBLE' if is_feasible else 'INFEASIBLE (CORRECTLY FLAGGED)'}")
    
    # Check if system hallucinated a fake cheap flight or admitted infeasibility
    passed = not is_feasible and total_cost > 400.0
    print(f"RESULT: {'✅ PASSED (System refused to hallucinate impossible budget)' if passed else '❌ FAILED'}")
    assert passed, f"System hallucinated: is_feasible={is_feasible}, total_cost={total_cost}"
    if __name__ == "__main__":
        return {"name": "Adversarial Budget Trap", "passed": passed, "latency": dur, "cost": total_cost, "feasible": is_feasible}

def test_2_rural_transit_physics_audit():
    print("\n" + "="*70)
    print("TEST 2: MICRO-GEOGRAPHY & PHYSICS REASONING (Google Maps & Knowledge Graph)")
    print("="*70)
    print("Prompt: 'Travel from Jihri to Bajaura in Himachal Pradesh for 1 day'")
    
    state = create_initial_state(user_query="Travel from Jihri to Bajaura in Himachal Pradesh for 1 day")
    state["source"] = "Jihri"
    state["destination"] = "Bajaura"
    state["duration_days"] = 1
    state["travelers"] = 1
    
    t0 = time.time()
    out = travel_pipeline.invoke(state)
    dur = round(time.time() - t0, 2)
    
    src_res = out.get("resolved_source")
    dst_res = out.get("resolved_destination")
    out_trans = out.get("selected_outbound_transport")
    all_trans = out.get("outbound_transport_options", [])
    
    # Check: No direct trains in mountain villages!
    train_options = [t for t in all_trans if t.mode == TransportType.TRAIN]
    flight_options = [t for t in all_trans if t.mode == TransportType.FLIGHT]
    
    print(f"Resolved Source: {src_res.canonical_name if src_res else 'Unknown'} (Rural: {getattr(src_res, 'is_rural', False)})")
    print(f"Resolved Destination: {dst_res.canonical_name if dst_res else 'Unknown'} (Rural: {getattr(dst_res, 'is_rural', False)})")
    print(f"Selected Mode: {out_trans.mode.value if out_trans else 'None'} | Fare: ₹{out_trans.fare if out_trans else 0}")
    print(f"Hallucinated Direct Trains: {len(train_options)} (Expected: 0)")
    print(f"Hallucinated Direct Flights: {len(flight_options)} (Expected: 0)")
    
    passed = len(train_options) == 0 and len(flight_options) == 0 and out_trans is not None
    print(f"RESULT: {'✅ PASSED (Zero physical hallucinations in remote mountains)' if passed else '❌ FAILED'}")
    assert passed, f"Physical hallucination detected: trains={len(train_options)}, flights={len(flight_options)}"
    if __name__ == "__main__":
        return {"name": "Rural Transit Physics", "passed": passed, "latency": dur, "trains": len(train_options)}

def test_3_evidence_provenance_audit():
    print("\n" + "="*70)
    print("TEST 3: GROUNDING & EVIDENCE PROVENANCE AUDIT (Google Factuality Standard)")
    print("="*70)
    print("Evaluating Grounding Claims Ledger from generated trip...")
    
    state = create_initial_state(user_query="Mandi to Shimla 2 days budget trip ₹3000")
    state["budget"] = 3000.0
    state["source"] = "Mandi"
    state["destination"] = "Shimla"
    state["duration_days"] = 2
    state["travelers"] = 1
    
    t0 = time.time()
    out = travel_pipeline.invoke(state)
    dur = round(time.time() - t0, 2)
    
    ledger = out.get("evidence_ledger", [])
    v_res = out.get("verification_results")
    
    tier_counts = {}
    for ev in ledger:
        t_name = ev.tier.name if hasattr(ev.tier, 'name') else str(ev.tier)
        tier_counts[t_name] = tier_counts.get(t_name, 0) + 1
        
    print(f"Total Evidentiary Claims: {len(ledger)}")
    for t_name, cnt in tier_counts.items():
        print(f"  • {t_name}: {cnt} items")
        
    v_score = v_res.verification_score if v_res else 0.0
    print(f"Composite Verification Score: {v_score:.1f}%")
    passed = len(ledger) > 0 and v_score >= 80.0
    print(f"RESULT: {'✅ PASSED (Strict provenance and auditability maintained)' if passed else '❌ FAILED'}")
    assert passed, f"Verification failed: claims={len(ledger)}, score={v_score}"
    if __name__ == "__main__":
        return {"name": "Evidence Provenance", "passed": passed, "latency": dur, "claims": len(ledger), "score": v_score}

def test_4_agent_telemetry_waterfall():
    print("\n" + "="*70)
    print("TEST 4: 12-AGENT PIPELINE LATENCY & SRE WATERFALL (Google Systems Standard)")
    print("="*70)
    
    state = create_initial_state(user_query="Quick 1 day trip Delhi to Jaipur")
    state["source"] = "Delhi"
    state["destination"] = "Jaipur"
    state["duration_days"] = 1
    state["travelers"] = 1
    
    t0 = time.time()
    out = travel_pipeline.invoke(state)
    total_dur = round(time.time() - t0, 2)
    
    telemetry = out.get("telemetry", [])
    print(f"{'AGENT NAME':<30} | {'DURATION (MS)':<14} | {'STATUS':<10}")
    print("-" * 60)
    for entry in telemetry:
        dur_ms = entry.get("duration_ms", 0.0)
        name = entry.get("agent_name", "Unknown")
        status = entry.get("status", "ok")
        print(f"{name:<30} | {dur_ms:>10.2f} ms | {status:<10}")
        
    print("-" * 60)
    print(f"Total Pipeline End-to-End Latency: {total_dur:.2f} seconds")
    assert total_dur > 0
    if __name__ == "__main__":
        return {"name": "Latency Waterfall", "passed": True, "total_latency": total_dur, "agents_count": len(telemetry)}

if __name__ == "__main__":
    print("\n" + "#"*70)
    print("# GOOGLE EXECUTIVE BENCHMARK & STRESS TEST REPORT")
    print("# Evaluator: Sundar Pichai (Simulated Google CEO & Technical Review)")
    print("# Target System: TravelPilot AI Multi-Agent Autonomous Architecture")
    print("#"*70)
    
    res1 = test_1_adversarial_impossible_budget()
    res2 = test_2_rural_transit_physics_audit()
    res3 = test_3_evidence_provenance_audit()
    res4 = test_4_agent_telemetry_waterfall()
    
    print("\n" + "#"*70)
    print("# EXECUTIVE TEST SUMMARY:")
    print(f"# Test 1 (Adversarial Budget):  {'PASS' if res1['passed'] else 'FAIL'} ({res1['latency']}s)")
    print(f"# Test 2 (Rural Transit Phys):   {'PASS' if res2['passed'] else 'FAIL'} ({res2['latency']}s)")
    print(f"# Test 3 (Evidence Provenance):  {'PASS' if res3['passed'] else 'FAIL'} ({res3['latency']}s, Score: {res3['score']}%)")
    print(f"# Test 4 (Telemetry Waterfall):  {'PASS' if res4['passed'] else 'FAIL'} ({res4['total_latency']}s)")
    print("#"*70 + "\n")
