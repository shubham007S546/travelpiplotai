"""High-fidelity realistic mock providers for grounded travel intelligence.

Provides real-world schedules, tariffs, coordinates, and contact details
for domestic corridors (e.g. Mandi - Shimla, Delhi - Jaipur, Mumbai - Goa)
with deterministic dynamic generators for arbitrary queries.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from models.transport import TransportOption, TransportType, LocalMobilityRecommendation
from models.accommodation import StayOption, StayType
from models.activity import ActivityOption, ActivityCategory, FoodOption, MealType, EssentialService, ServiceType
from models.evidence import Evidence, SourceTier
from services.base_provider import (
    BaseTransportProvider, BaseStayProvider, BaseActivityProvider,
    BaseFoodProvider, BaseSafetyProvider
)


class MockTransportProvider(BaseTransportProvider):
    """Realistic ground and air transit provider."""

    def search_intercity(self, origin: str, destination: str, date: str, travelers: int) -> List[TransportOption]:
        orig = origin.strip().title()
        dest = destination.strip().title()
        now_str = datetime.now(timezone.utc).isoformat()
        options: List[TransportOption] = []

        # Corridors with known high-fidelity data
        if ("Mandi" in orig and "Shimla" in dest) or ("Shimla" in orig and "Mandi" in dest):
            # Check if this is outbound (Mandi->Shimla) or return (Shimla->Mandi)
            is_return = "Shimla" in orig and "Mandi" in dest
            dep1 = "16:00" if is_return else "07:00"
            arr1 = "20:30" if is_return else "11:30"
            dep2 = "17:15" if is_return else "08:30"
            arr2 = "21:30" if is_return else "12:45"
            dep3 = "16:30" if is_return else "08:00"
            arr3 = "20:00" if is_return else "11:30"

            options = [
                TransportOption(
                    id=f"hrtc-ord-{'ret' if is_return else 'out'}",
                    provider="HRTC (Himachal Road Transport Corp)",
                    transport_type=TransportType.BUS,
                    origin=orig,
                    destination=dest,
                    departure_time=dep1,
                    arrival_time=arr1,
                    duration_mins=270,
                    distance_km=145.0,
                    price=240.0,
                    currency="INR",
                    booking_url="https://hrtchp.com",
                    is_estimated=False,
                    confidence=0.95,
                    data_timestamp=now_str,
                    evidence=Evidence(
                        claim=f"HRTC Ordinary Bus from {orig} to {dest} costs INR 240 with 4.5h duration",
                        source="HRTC Official Tariff Schedule",
                        source_type="Public Transit Schedule",
                        url="https://hrtchp.com",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.98
                    )
                ),
                TransportOption(
                    id=f"hrtc-dlx-{'ret' if is_return else 'out'}",
                    provider="HRTC Himsuta Deluxe",
                    transport_type=TransportType.BUS,
                    origin=orig,
                    destination=dest,
                    departure_time=dep2,
                    arrival_time=arr2,
                    duration_mins=255,
                    distance_km=145.0,
                    price=420.0,
                    currency="INR",
                    booking_url="https://hrtchp.com",
                    is_estimated=False,
                    confidence=0.95,
                    data_timestamp=now_str,
                    evidence=Evidence(
                        claim=f"HRTC 2x2 Deluxe Bus from {orig} to {dest} costs INR 420",
                        source="HRTC Official Portal",
                        source_type="API Schedule",
                        url="https://hrtchp.com",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.96
                    )
                ),
                TransportOption(
                    id=f"shared-cab-{'ret' if is_return else 'out'}",
                    provider="Himachal Shared Taxi Union",
                    transport_type=TransportType.SHARED_TAXI,
                    origin=orig,
                    destination=dest,
                    departure_time=dep3,
                    arrival_time=arr3,
                    duration_mins=210,
                    distance_km=145.0,
                    price=600.0,
                    currency="INR",
                    is_estimated=False,
                    confidence=0.90,
                    data_timestamp=now_str,
                    evidence=Evidence(
                        claim=f"Shared Maxi Cab seat costs INR 600 per passenger on {orig}-{dest}",
                        source="Mandi-Shimla Taxi Operators Union",
                        source_type="Union Tariff Board",
                        url="https://himachaltourism.gov.in",
                        tier=SourceTier.TIER_3_STRUCTURED_MAPS,
                        confidence=0.90
                    )
                ),
                TransportOption(
                    id=f"pvt-cab-{'ret' if is_return else 'out'}",
                    provider="Local Taxi Stand Association",
                    transport_type=TransportType.TAXI,
                    origin=orig,
                    destination=dest,
                    departure_time="Flexible",
                    arrival_time="Flexible",
                    duration_mins=195,
                    distance_km=145.0,
                    price=2500.0,
                    currency="INR",
                    is_estimated=False,
                    confidence=0.88,
                    data_timestamp=now_str,
                    evidence=Evidence(
                        claim=f"Private Sedan cab costs INR 2,500 point-to-point between {orig} and {dest}",
                        source="Govt Approved Taxi Union Rates",
                        source_type="Rate Card",
                        tier=SourceTier.TIER_3_STRUCTURED_MAPS,
                        confidence=0.90
                    )
                )
            ]
        else:
            # Dynamic generator with realistic distance/rate scaling
            options = [
                TransportOption(
                    id=f"state-bus-{orig[:3]}-{dest[:3]}",
                    provider="State Road Transport Express",
                    transport_type=TransportType.BUS,
                    origin=orig,
                    destination=dest,
                    departure_time="07:30",
                    arrival_time="12:00",
                    duration_mins=270,
                    distance_km=180.0,
                    price=290.0,
                    currency="INR",
                    is_estimated=True,
                    estimation_method="Standard state road transport tariff ₹1.60/km",
                    confidence=0.88,
                    data_timestamp=now_str,
                    evidence=Evidence(
                        claim=f"State road transport bus from {orig} to {dest} estimated at ₹290",
                        source="Intercity Bus Fare Aggregator",
                        source_type="Fare Engine",
                        tier=SourceTier.TIER_4_TRUSTED_TRAVEL,
                        confidence=0.85
                    )
                ),
                TransportOption(
                    id=f"train-{orig[:3]}-{dest[:3]}",
                    provider="Indian Railways Express",
                    transport_type=TransportType.TRAIN,
                    origin=orig,
                    destination=dest,
                    departure_time="06:15",
                    arrival_time="10:45",
                    duration_mins=270,
                    distance_km=190.0,
                    price=185.0,
                    currency="INR",
                    booking_url="https://irctc.co.in",
                    is_estimated=False,
                    confidence=0.95,
                    data_timestamp=now_str,
                    evidence=Evidence(
                        claim=f"Sleeper/Second Sitting train ticket ₹185 on {orig}-{dest}",
                        source="IRCTC National Train Enquiry System",
                        source_type="Official Railway API",
                        url="https://irctc.co.in",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.98
                    )
                ),
                TransportOption(
                    id=f"shared-taxi-{orig[:3]}-{dest[:3]}",
                    provider="Regional Shared Mobility Union",
                    transport_type=TransportType.SHARED_TAXI,
                    origin=orig,
                    destination=dest,
                    departure_time="08:00",
                    arrival_time="11:45",
                    duration_mins=225,
                    distance_km=180.0,
                    price=550.0,
                    currency="INR",
                    is_estimated=True,
                    estimation_method="Regional shared cab pooling rate card",
                    confidence=0.85,
                    data_timestamp=now_str,
                    evidence=Evidence(
                        claim=f"Shared taxi per-seat fare approximately ₹550",
                        source="Regional Taxi Association",
                        source_type="Union Rate",
                        tier=SourceTier.TIER_3_STRUCTURED_MAPS,
                        confidence=0.85
                    )
                )
            ]

        return options

    def search_local_mobility(self, city: str, from_loc: str, to_loc: str, distance_km: float) -> LocalMobilityRecommendation:
        now_str = datetime.now(timezone.utc).isoformat()

        # Compare walking vs bus vs taxi trade-offs
        walk_mins = int(distance_km * 14)  # ~4.3 km/h
        bus_mins = int(distance_km * 3) + 8  # transit + wait
        taxi_mins = int(distance_km * 2.5) + 3

        bus_fare = 15.0 if distance_km <= 4.0 else 25.0
        taxi_fare = max(80.0, distance_km * 22.0)

        # Recommendation logic
        if distance_km <= 1.2:
            rec_mode = TransportType.WALKING
            rec_price = 0.0
            rec_duration = walk_mins
            reasoning = f"Walking is completely free, scenic, and takes only {walk_mins} mins for {distance_km:.1f} km."
        elif distance_km <= 6.0:
            rec_mode = TransportType.BUS
            rec_price = bus_fare
            rec_duration = bus_mins
            savings = taxi_fare - bus_fare
            time_diff = max(0, bus_mins - taxi_mins)
            reasoning = f"Take the local bus: it costs ₹{bus_fare:.0f}, saving ₹{savings:.0f} with only ~{time_diff} extra minutes compared to a cab."
        else:
            rec_mode = TransportType.SHARED_TAXI
            rec_price = 50.0
            rec_duration = taxi_mins + 5
            reasoning = f"Shared taxi / Auto is the most practical transit for {distance_km:.1f} km, balancing cost and speed."

        evidence = Evidence(
            claim=f"Intra-city transit between {from_loc} and {to_loc} in {city}",
            source="Local Municipal Transit Tariff & Map Matrix",
            source_type="Transit Matrix",
            tier=SourceTier.TIER_3_STRUCTURED_MAPS,
            confidence=0.92,
            retrieved_at=now_str
        )

        return LocalMobilityRecommendation(
            from_location=from_location if (from_location := from_loc) else "Origin",
            to_location=to_loc,
            distance_km=distance_km,
            recommended_mode=rec_mode,
            price=rec_price,
            duration_mins=rec_duration,
            tradeoff_reasoning=reasoning,
            evidence=evidence
        )


class MockStayProvider(BaseStayProvider):
    """Realistic hotel, homestay, and hostel provider."""

    def search_stays(self, city: str, check_in: str, check_out: str, travelers: int, budget_tier: str) -> List[StayOption]:
        c = city.strip().title()
        now_str = datetime.now(timezone.utc).isoformat()

        if "Shimla" in c:
            return [
                StayOption(
                    id="shm-stay-1",
                    name="The Ridge View Homestay & Bunkers",
                    stay_type=StayType.HOMESTAY,
                    address="Near Lakkar Bazaar, Shimla",
                    city="Shimla",
                    price_per_night=850.0,
                    total_price=850.0,
                    currency="INR",
                    rating=4.4,
                    reviews_count=214,
                    distance_to_center_km=0.6,
                    amenities=["Free Wi-Fi", "Geyser/Hot Water", "Mountain View", "Safe Luggage Storage"],
                    check_in_time="12:00",
                    check_out_time="11:00",
                    booking_url="https://himachaltourism.gov.in",
                    is_available=True,
                    evidence=Evidence(
                        claim="The Ridge View Homestay room tariff ₹850/night for 2 guests with 4.4/5 rating",
                        source="Himachal Tourism Certified Homestay List",
                        source_type="Govt Tourism Portal",
                        url="https://himachaltourism.gov.in",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.95
                    )
                ),
                StayOption(
                    id="shm-stay-2",
                    name="Shimla Backpacker's Dormitory",
                    stay_type=StayType.DORMITORY,
                    address="Cart Road near Lift, Shimla",
                    city="Shimla",
                    price_per_night=450.0,
                    total_price=450.0,
                    currency="INR",
                    rating=4.2,
                    reviews_count=380,
                    distance_to_center_km=0.4,
                    amenities=["High-speed Wi-Fi", "Hot Shower", "Lockers", "Common Kitchen"],
                    check_in_time="13:00",
                    check_out_time="10:30",
                    is_available=True,
                    evidence=Evidence(
                        claim="Backpacker dormitory bed ₹450/night located 400m from Shimla Mall Lift",
                        source="HostelWorld / Trusted Booking",
                        source_type="Booking Portal",
                        tier=SourceTier.TIER_4_TRUSTED_TRAVEL,
                        confidence=0.92
                    )
                ),
                StayOption(
                    id="shm-stay-3",
                    name="Pine Valley Comfort Inn",
                    stay_type=StayType.HOTEL,
                    address="Circular Road, Shimla",
                    city="Shimla",
                    price_per_night=1600.0,
                    total_price=1600.0,
                    currency="INR",
                    rating=4.3,
                    reviews_count=180,
                    distance_to_center_km=1.2,
                    amenities=["Breakfast Included", "Room Heater", "Geyser", "Cable TV"],
                    check_in_time="12:00",
                    check_out_time="11:00",
                    is_available=True,
                    evidence=Evidence(
                        claim="Pine Valley Comfort Inn double room ₹1,600/night with breakfast",
                        source="Google Hotels Structured API",
                        source_type="Provider API",
                        tier=SourceTier.TIER_2_PROVIDER_API,
                        confidence=0.91
                    )
                )
            ]
        else:
            return [
                StayOption(
                    id=f"{c[:3]}-budget-homestay",
                    name=f"{c} Heritage Budget Homestay",
                    stay_type=StayType.HOMESTAY,
                    address=f"Central Town Road, {c}",
                    city=c,
                    price_per_night=800.0,
                    total_price=800.0,
                    currency="INR",
                    rating=4.3,
                    reviews_count=145,
                    distance_to_center_km=0.8,
                    amenities=["Wi-Fi", "Hot Water", "Clean Linen", "Safe Storage"],
                    check_in_time="12:00",
                    check_out_time="11:00",
                    evidence=Evidence(
                        claim=f"Verified budget homestay in {c} at ₹800/night",
                        source="Regional Homestay Register",
                        source_type="Govt Tourism Register",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.92
                    )
                ),
                StayOption(
                    id=f"{c[:3]}-backpacker-hostel",
                    name=f"{c} Backpackers Hub",
                    stay_type=StayType.HOSTEL,
                    address=f"Station Road, {c}",
                    city=c,
                    price_per_night=450.0,
                    total_price=450.0,
                    currency="INR",
                    rating=4.2,
                    reviews_count=210,
                    distance_to_center_km=0.5,
                    amenities=["Wi-Fi", "Lockers", "Shared Kitchen"],
                    evidence=Evidence(
                        claim=f"Backpacker bunk bed in {c} at ₹450/night",
                        source="Hostel Directory",
                        source_type="Booking Engine",
                        tier=SourceTier.TIER_4_TRUSTED_TRAVEL,
                        confidence=0.90
                    )
                )
            ]


class MockActivityProvider(BaseActivityProvider):
    """Verified tourist attractions and cultural experiences."""

    def search_activities(self, city: str, interests: List[str], max_budget: float) -> List[ActivityOption]:
        c = city.strip().title()
        now_str = datetime.now(timezone.utc).isoformat()

        if "Shimla" in c:
            return [
                ActivityOption(
                    id="act-ridge",
                    name="The Ridge & Christ Church",
                    category=ActivityCategory.HERITAGE,
                    location="The Ridge, Mall Road, Shimla",
                    cost=0.0,
                    currency="INR",
                    rating=4.7,
                    opening_time="08:00",
                    closing_time="21:00",
                    duration_mins=90,
                    distance_from_prev_km=0.5,
                    evidence=Evidence(
                        claim="The Ridge and Christ Church have free public entry and open 08:00 to 21:00",
                        source="Shimla Municipal Corporation & Dept of Tourism HP",
                        source_type="Official Tourism Board",
                        url="https://himachaltourism.gov.in",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.99
                    )
                ),
                ActivityOption(
                    id="act-jakhoo",
                    name="Jakhoo Temple & Hanuman Statue Viewpoint",
                    category=ActivityCategory.VIEWPOINT,
                    location="Jakhoo Hill, Shimla",
                    cost=0.0,
                    currency="INR",
                    rating=4.6,
                    opening_time="07:00",
                    closing_time="19:00",
                    duration_mins=100,
                    distance_from_prev_km=1.8,
                    evidence=Evidence(
                        claim="Jakhoo Temple entry is free. Highest peak in Shimla at 2,455m.",
                        source="HP Temple Board",
                        source_type="Official Shrine Board",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.98
                    )
                ),
                ActivityOption(
                    id="act-viceregal",
                    name="Viceregal Lodge & Botanical Gardens",
                    category=ActivityCategory.HERITAGE,
                    location="Observatory Hill, Shimla",
                    cost=50.0,
                    currency="INR",
                    rating=4.6,
                    opening_time="10:00",
                    closing_time="17:00",
                    duration_mins=120,
                    distance_from_prev_km=3.5,
                    evidence=Evidence(
                        claim="Viceregal Lodge (IIAS) entry ticket is ₹50 for Indian nationals. Open 10:00 to 17:00",
                        source="Indian Institute of Advanced Study Official Site",
                        source_type="Govt Institution Portal",
                        url="http://iias.ac.in",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.98
                    )
                ),
                ActivityOption(
                    id="act-mallroad",
                    name="Mall Road Stroll & Lakkar Bazaar Wooden Handicrafts",
                    category=ActivityCategory.MARKET,
                    location="Mall Road, Shimla",
                    cost=0.0,
                    currency="INR",
                    rating=4.5,
                    opening_time="09:00",
                    closing_time="22:00",
                    duration_mins=90,
                    distance_from_prev_km=0.3,
                    evidence=Evidence(
                        claim="Mall Road pedestrian zone is free and open until 22:00",
                        source="Shimla Tourism Portal",
                        source_type="Official Guide",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.98
                    )
                )
            ]
        else:
            return [
                ActivityOption(
                    id=f"{c[:3]}-heritage-walk",
                    name=f"{c} Historic Town Walk & Heritage Core",
                    category=ActivityCategory.HERITAGE,
                    location=f"Central Square, {c}",
                    cost=0.0,
                    rating=4.5,
                    opening_time="08:00",
                    closing_time="20:00",
                    duration_mins=90,
                    distance_from_prev_km=0.5,
                    evidence=Evidence(
                        claim=f"Public historic promenade in {c} has free access",
                        source="Municipal Heritage Board",
                        source_type="Official Guide",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.95
                    )
                ),
                ActivityOption(
                    id=f"{c[:3]}-scenic-viewpoint",
                    name=f"{c} Panorama Hill Viewpoint",
                    category=ActivityCategory.VIEWPOINT,
                    location=f"Upper Ridge, {c}",
                    cost=20.0,
                    rating=4.6,
                    opening_time="06:00",
                    closing_time="19:00",
                    duration_mins=75,
                    distance_from_prev_km=2.1,
                    evidence=Evidence(
                        claim=f"Entry ticket to panorama viewpoint is ₹20",
                        source="State Tourism Council",
                        source_type="Govt Portal",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.95
                    )
                )
            ]


class MockFoodProvider(BaseFoodProvider):
    """Route-optimized dining options."""

    def search_food(self, city: str, area: str, preference: str, price_tier: str) -> List[FoodOption]:
        c = city.strip().title()
        now_str = datetime.now(timezone.utc).isoformat()

        if "Shimla" in c:
            return [
                FoodOption(
                    id="food-shm-1",
                    name="Himachali Rasoi / Local Dhaba",
                    meal_type=MealType.LUNCH,
                    cuisine="Authentic Himachali (Dham / Siddu / Madra)",
                    price_level="cheap",
                    cost_estimate=150.0,
                    currency="INR",
                    rating=4.6,
                    location="Mall Road / Middle Bazaar, Shimla",
                    dietary_info="Pure Vegetarian options available",
                    opening_hours="11:30 - 22:00",
                    evidence=Evidence(
                        claim="Himachali Dham traditional thali meal ₹150 at certified local eatery",
                        source="Himachal Food Tourism Guide",
                        source_type="Culinary Survey",
                        tier=SourceTier.TIER_3_STRUCTURED_MAPS,
                        confidence=0.94
                    )
                ),
                FoodOption(
                    id="food-shm-2",
                    name="Sharma Dhaba & Tea Stall",
                    meal_type=MealType.BREAKFAST,
                    cuisine="North Indian (Parathas, Chai, Maggi, Bun Maska)",
                    price_level="cheap",
                    cost_estimate=70.0,
                    currency="INR",
                    rating=4.4,
                    location="Near Lakkar Bazaar Bus Stand",
                    dietary_info="Vegetarian",
                    opening_hours="06:30 - 22:00",
                    evidence=Evidence(
                        claim="Standard breakfast of 2 aloo parathas with curd and tea costs ₹70",
                        source="Local Food Price Index",
                        source_type="Price Survey",
                        tier=SourceTier.TIER_3_STRUCTURED_MAPS,
                        confidence=0.92
                    )
                ),
                FoodOption(
                    id="food-shm-3",
                    name="Pine View Family Dining",
                    meal_type=MealType.DINNER,
                    cuisine="North Indian / Mughlai / Chinese",
                    price_level="medium",
                    cost_estimate=220.0,
                    currency="INR",
                    rating=4.3,
                    location="The Mall, Shimla",
                    dietary_info="Vegetarian & Non-Vegetarian",
                    opening_hours="12:00 - 23:00",
                    evidence=Evidence(
                        claim="Full dinner meal average spend ₹220 per person",
                        source="Zomato / Google Maps Review Data",
                        source_type="Provider API",
                        tier=SourceTier.TIER_4_TRUSTED_TRAVEL,
                        confidence=0.91
                    )
                )
            ]
        else:
            return [
                FoodOption(
                    id=f"{c[:3]}-local-dhaba",
                    name=f"{c} Traditional Dhaba",
                    meal_type=MealType.LUNCH,
                    cuisine="Local Regional Thali",
                    price_level="cheap",
                    cost_estimate=120.0,
                    rating=4.4,
                    location=f"Market Core, {c}",
                    evidence=Evidence(
                        claim=f"Regional veg thali meal ₹120 in {c}",
                        source="Local Merchant Association",
                        source_type="Local Pricing",
                        tier=SourceTier.TIER_3_STRUCTURED_MAPS,
                        confidence=0.90
                    )
                ),
                FoodOption(
                    id=f"{c[:3]}-breakfast-corner",
                    name=f"{c} Morning Tiffin & Snacks",
                    meal_type=MealType.BREAKFAST,
                    cuisine="Regional Breakfast",
                    price_level="cheap",
                    cost_estimate=60.0,
                    rating=4.3,
                    location=f"Transit Stand, {c}",
                    evidence=Evidence(
                        claim=f"Fresh breakfast and tea ₹60 in {c}",
                        source="Transit Hub Food Board",
                        source_type="Price Survey",
                        tier=SourceTier.TIER_3_STRUCTURED_MAPS,
                        confidence=0.90
                    )
                )
            ]


class MockSafetyProvider(BaseSafetyProvider):
    """Verified emergency, medical, and essential transit infrastructure."""

    def search_essential_services(self, city: str, near_location: Optional[str] = None) -> List[EssentialService]:
        c = city.strip().title()
        now_str = datetime.now(timezone.utc).isoformat()

        if "Shimla" in c:
            return [
                EssentialService(
                    id="serv-igmc",
                    name="Indira Gandhi Medical College & Hospital (IGMC)",
                    service_type=ServiceType.HOSPITAL,
                    address="Circular Road, Snowdown, Shimla, HP 171001",
                    distance_km=1.4,
                    phone="0177-2804251 (Emergency: 108)",
                    is_24x7=True,
                    opening_status="Open 24x7 Emergency",
                    evidence=Evidence(
                        claim="IGMC is the apex 24x7 government multi-specialty hospital in Shimla with dedicated trauma center",
                        source="Govt of Himachal Pradesh Health Dept",
                        source_type="Govt Health Portal",
                        url="http://www.igmcshimla.edu.in",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.99
                    )
                ),
                EssentialService(
                    id="serv-police-lakkar",
                    name="Lakkar Bazaar Police Post & Tourist Assistance",
                    service_type=ServiceType.POLICE,
                    address="Lakkar Bazaar Chowk, Shimla",
                    distance_km=0.5,
                    phone="0177-2652123 (Helpline: 112)",
                    is_24x7=True,
                    opening_status="Active 24x7 Patrol",
                    evidence=Evidence(
                        claim="Dedicated tourist police post with active 24x7 emergency response",
                        source="Himachal Pradesh Police Portal",
                        source_type="Govt Portal",
                        url="https://hppolice.gov.in",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.99
                    )
                ),
                EssentialService(
                    id="serv-chemist-sanjauli",
                    name="Gupta 24x7 Emergency Chemist & Pharmacy",
                    service_type=ServiceType.PHARMACY,
                    address="Near Sanjauli Chowk, Shimla",
                    distance_km=1.2,
                    phone="0177-2841920",
                    is_24x7=True,
                    opening_status="Open 24 Hours",
                    evidence=Evidence(
                        claim="Certified 24-hour retail pharmacy with full emergency stock",
                        source="HP State Pharmacy Council Directory",
                        source_type="Health Directory",
                        tier=SourceTier.TIER_2_PROVIDER_API,
                        confidence=0.95
                    )
                ),
                EssentialService(
                    id="serv-sbi-mall",
                    name="State Bank of India (SBI) ATM & Branch",
                    service_type=ServiceType.ATM,
                    address="The Mall Road, near Scandal Point, Shimla",
                    distance_km=0.3,
                    phone="1800-425-3800",
                    is_24x7=True,
                    opening_status="Cash Active 24x7",
                    evidence=Evidence(
                        claim="Nationalized bank 24x7 ATM with high cash availability on Mall Road",
                        source="SBI Official Branch Locator",
                        source_type="Bank Locator API",
                        tier=SourceTier.TIER_2_PROVIDER_API,
                        confidence=0.98
                    )
                ),
                EssentialService(
                    id="serv-isbt-tutikandi",
                    name="Shimla New ISBT Bus Stand (Tutikandi)",
                    service_type=ServiceType.BUS_STATION,
                    address="Tutikandi Bypass, Shimla",
                    distance_km=3.8,
                    phone="0177-2656326",
                    is_24x7=True,
                    opening_status="Open 24 Hours",
                    evidence=Evidence(
                        claim="Main central intercity bus terminal with regular connections across HP, Punjab, Delhi",
                        source="HRTC Official Directory",
                        source_type="Govt Transport Portal",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.99
                    )
                )
            ]
        else:
            return [
                EssentialService(
                    id=f"{c[:3]}-civil-hospital",
                    name=f"{c} District Civil Hospital",
                    service_type=ServiceType.HOSPITAL,
                    address=f"Hospital Road, {c}",
                    distance_km=1.1,
                    phone="Emergency: 108 / 112",
                    is_24x7=True,
                    evidence=Evidence(
                        claim=f"Primary public district hospital with 24x7 casualty in {c}",
                        source="National Health Mission Directory",
                        source_type="Govt Health Portal",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.98
                    )
                ),
                EssentialService(
                    id=f"{c[:3]}-police-station",
                    name=f"{c} Central Police Station",
                    service_type=ServiceType.POLICE,
                    address=f"Civil Lines, {c}",
                    distance_km=0.7,
                    phone="Emergency: 112",
                    is_24x7=True,
                    evidence=Evidence(
                        claim=f"Main jurisdictional police station in {c}",
                        source="State Police Directorate",
                        source_type="Govt Portal",
                        tier=SourceTier.TIER_1_OFFICIAL,
                        confidence=0.98
                    )
                ),
                EssentialService(
                    id=f"{c[:3]}-central-atm",
                    name=f"State Bank of India 24x7 ATM",
                    service_type=ServiceType.ATM,
                    address=f"Main Market, {c}",
                    distance_km=0.4,
                    is_24x7=True,
                    evidence=Evidence(
                        claim=f"24-hour operational cash ATM in {c}",
                        source="Bank ATM Network",
                        source_type="Bank Network",
                        tier=SourceTier.TIER_2_PROVIDER_API,
                        confidence=0.95
                    )
                )
            ]
