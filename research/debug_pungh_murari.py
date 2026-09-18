import sys
import os

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.place_resolution_agent import PlaceResolutionAgent
from services.transport_verification import TransportVerificationPipeline

pa = PlaceResolutionAgent()
src = pa._resolve_single_place('pungh sundernagar')
dst = pa._resolve_single_place('murari devi')

print("=== PLACE RESOLUTION ===")
print("SRC:", src.canonical_name, src.latitude, src.longitude, src.is_valid, src.confidence, src.source)
print("DST:", dst.canonical_name, dst.latitude, dst.longitude, dst.is_valid, dst.confidence, dst.source)

pipeline = TransportVerificationPipeline()
opts, rres, msgs = pipeline.discover_and_verify_transport(src, dst, '2026-10-01', 1)

print("\n=== ROUTE VERIFICATION ===")
if rres:
    print("ROAD KM:", rres.road_distance_km)
    print("STATUS:", rres.distance_status)
    print("PROVIDER:", rres.provider)
else:
    print("ROUTE_RES IS NONE")

print("\n=== TRANSIT OPTIONS ===")
print("COUNT:", len(opts))
for o in opts:
    print(f" - {o.mode}: {o.provider} | {o.distance_km} km | ₹{o.fare}")

print("\n=== MESSAGES ===")
for m in msgs:
    print(" -", m)
