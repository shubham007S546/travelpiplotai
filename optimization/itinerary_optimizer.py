"""Spatio-Temporal Day-by-Day Itinerary Optimization Engine."""

from typing import List, Optional
from models.travel_state import ItineraryDay, ItineraryItem
from models.transport import TransportOption
from models.accommodation import StayOption
from models.activity import ActivityOption, FoodOption
from utils.helpers import add_minutes_to_time_str


class ItineraryOptimizer:
    """Schedules chronological itineraries with realistic transit windows and operating hours."""

    @classmethod
    def build_itinerary(
        cls,
        duration_days: int,
        source: str,
        destination: str,
        outbound_transport: Optional[TransportOption],
        return_transport: Optional[TransportOption],
        stay: Optional[StayOption],
        food_list: List[FoodOption],
        activities: List[ActivityOption],
        currency: str = "INR"
    ) -> List[ItineraryDay]:
        days: List[ItineraryDay] = []
        days_to_plan = max(1, duration_days)

        # Distribute activities across days
        acts_per_day = 2
        remaining_activities = list(activities)

        for d in range(1, days_to_plan + 1):
            items: List[ItineraryItem] = []
            day_cost = 0.0

            if d == 1:
                # DAY 1: Departure -> Arrival -> Check-in -> Lunch -> Sightseeing -> Dinner
                # 1. Outbound Transit
                dep_time = outbound_transport.departure_time if outbound_transport and outbound_transport.departure_time != "Flexible" else "07:30"
                arr_time = outbound_transport.arrival_time if outbound_transport and outbound_transport.arrival_time != "Flexible" else "12:00"
                raw_out_cost = float(outbound_transport.price) if (outbound_transport and outbound_transport.price is not None) else 0.0
                transit_cost = raw_out_cost if raw_out_cost > 0 else 120.0
                day_cost += transit_cost

                out_prov = outbound_transport.provider if (outbound_transport and outbound_transport.provider) else "State Transport (HRTC/UTC Ordinary)"
                items.append(ItineraryItem(
                    id=f"day1-transit-out",
                    day_number=1,
                    start_time=dep_time,
                    end_time=arr_time,
                    title=f"Transit: {source} -> {destination}",
                    item_type="travel",
                    location=f"{source} to {destination}",
                    duration_mins=outbound_transport.duration_mins if outbound_transport else 270,
                    transport_mode=outbound_transport.transport_type.value if outbound_transport else "bus",
                    estimated_cost=transit_cost,
                    currency=currency,
                    notes=f"Provider: {out_prov}",
                    evidence=outbound_transport.evidence if outbound_transport else None
                ))

                # 2. Arrival & Check-in / Luggage Drop
                checkin_start = arr_time
                checkin_end = add_minutes_to_time_str(checkin_start, 45)
                stay_cost = float(stay.price_per_night) if (stay and stay.price_per_night is not None) else 0.0
                day_cost += stay_cost

                items.append(ItineraryItem(
                    id=f"day1-checkin",
                    day_number=1,
                    start_time=checkin_start,
                    end_time=checkin_end,
                    title=f"Check-in / Freshen up at {stay.name if stay else 'Accommodations'}",
                    item_type="checkin",
                    location=stay.address if stay else destination,
                    duration_mins=45,
                    estimated_cost=stay_cost,
                    currency=currency,
                    notes=f"Rating: {stay.rating if stay else 4.0}/5.0 | {stay.stay_type.value if stay else 'stay'}",
                    evidence=stay.evidence if stay else None
                ))

                # 3. Lunch
                lunch_start = checkin_end
                lunch_end = add_minutes_to_time_str(lunch_start, 60)
                lunch_item = next((f for f in food_list if f.meal_type.value == "lunch"), None)
                lunch_cost = lunch_item.cost_estimate if lunch_item else 150.0
                day_cost += lunch_cost

                items.append(ItineraryItem(
                    id=f"day1-lunch",
                    day_number=1,
                    start_time=lunch_start,
                    end_time=lunch_end,
                    title=f"Lunch: {lunch_item.name if lunch_item else 'Local Himachali Dhaba'}",
                    item_type="dining",
                    location=lunch_item.location if lunch_item else destination,
                    duration_mins=60,
                    estimated_cost=lunch_cost,
                    currency=currency,
                    notes=lunch_item.cuisine if lunch_item else "Regional Specialties",
                    evidence=lunch_item.evidence if lunch_item else None
                ))

                # 4. Afternoon Activity
                curr_time = lunch_end
                day_acts = remaining_activities[:acts_per_day]
                remaining_activities = remaining_activities[acts_per_day:]

                for idx, act in enumerate(day_acts):
                    transit_to_act = 20
                    act_start = add_minutes_to_time_str(curr_time, transit_to_act)
                    act_end = add_minutes_to_time_str(act_start, act.duration_mins)
                    day_cost += act.cost

                    items.append(ItineraryItem(
                        id=f"day1-act-{idx+1}",
                        day_number=1,
                        start_time=act_start,
                        end_time=act_end,
                        title=act.name,
                        item_type="attraction",
                        location=act.location,
                        duration_mins=act.duration_mins,
                        travel_time_from_prev_mins=transit_to_act,
                        transport_mode="walking/local transit",
                        estimated_cost=act.cost,
                        currency=currency,
                        notes=f"Category: {act.category.value} (Open {act.opening_time} - {act.closing_time})",
                        evidence=act.evidence
                    ))
                    curr_time = act_end

                # 5. Dinner
                dinner_start = max(curr_time, "19:30")
                dinner_end = add_minutes_to_time_str(dinner_start, 60)
                dinner_item = next((f for f in food_list if f.meal_type.value == "dinner"), None)
                dinner_cost = dinner_item.cost_estimate if dinner_item else 200.0
                day_cost += dinner_cost

                items.append(ItineraryItem(
                    id=f"day1-dinner",
                    day_number=1,
                    start_time=dinner_start,
                    end_time=dinner_end,
                    title=f"Dinner: {dinner_item.name if dinner_item else 'Pine View Dining'}",
                    item_type="dining",
                    location=dinner_item.location if dinner_item else destination,
                    duration_mins=60,
                    estimated_cost=dinner_cost,
                    currency=currency,
                    notes="Relaxed dinner and evening walk",
                    evidence=dinner_item.evidence if dinner_item else None
                ))

                days.append(ItineraryDay(
                    day_number=1,
                    theme=f"Arrival & Exploring {destination} Core",
                    items=items,
                    daily_cost=round(day_cost, 2)
                ))

            else:
                # DAY 2+: Breakfast -> Morning Sightseeing -> Lunch -> Afternoon Exploration -> Return Journey
                curr_time = "08:30"
                # Breakfast
                bfast_start = curr_time
                bfast_end = add_minutes_to_time_str(bfast_start, 45)
                bfast_item = next((f for f in food_list if f.meal_type.value == "breakfast"), None)
                bfast_cost = bfast_item.cost_estimate if bfast_item else 80.0
                day_cost += bfast_cost

                items.append(ItineraryItem(
                    id=f"day{d}-bfast",
                    day_number=d,
                    start_time=bfast_start,
                    end_time=bfast_end,
                    title=f"Breakfast: {bfast_item.name if bfast_item else 'Local Morning Eatery'}",
                    item_type="dining",
                    location=bfast_item.location if bfast_item else destination,
                    duration_mins=45,
                    estimated_cost=bfast_cost,
                    currency=currency,
                    evidence=bfast_item.evidence if bfast_item else None
                ))
                curr_time = bfast_end

                # Activity
                day_acts = remaining_activities[:acts_per_day]
                remaining_activities = remaining_activities[acts_per_day:]
                if not day_acts and activities:
                    day_acts = [activities[-1]]

                for idx, act in enumerate(day_acts):
                    transit_to_act = 20
                    act_start = add_minutes_to_time_str(curr_time, transit_to_act)
                    act_end = add_minutes_to_time_str(act_start, act.duration_mins)
                    day_cost += act.cost

                    items.append(ItineraryItem(
                        id=f"day{d}-act-{idx+1}",
                        day_number=d,
                        start_time=act_start,
                        end_time=act_end,
                        title=act.name,
                        item_type="attraction",
                        location=act.location,
                        duration_mins=act.duration_mins,
                        travel_time_from_prev_mins=transit_to_act,
                        transport_mode="walking/local bus",
                        estimated_cost=act.cost,
                        currency=currency,
                        evidence=act.evidence
                    ))
                    curr_time = act_end

                # Checkout & Return Transit if last day
                if d == days_to_plan:
                    nominal_dep = return_transport.departure_time if return_transport and return_transport.departure_time != "Flexible" else "16:00"
                    # Ensure departure is at least 45 mins after the last activity
                    earliest_dep = add_minutes_to_time_str(curr_time, 45)
                    ret_dep = max(nominal_dep, earliest_dep)
                    dur = return_transport.duration_mins if return_transport else 270
                    ret_arr = add_minutes_to_time_str(ret_dep, dur)
                    raw_ret_cost = float(return_transport.price) if (return_transport and return_transport.price is not None) else 0.0
                    ret_cost = raw_ret_cost if raw_ret_cost > 0 else 120.0
                    day_cost += ret_cost

                    ret_prov = return_transport.provider if (return_transport and return_transport.provider) else "State Transport (HRTC/UTC Ordinary)"
                    items.append(ItineraryItem(
                        id=f"day{d}-return-transit",
                        day_number=d,
                        start_time=ret_dep,
                        end_time=ret_arr,
                        title=f"Return Journey: {destination} -> {source}",
                        item_type="travel",
                        location=f"{destination} to {source}",
                        duration_mins=dur,
                        transport_mode=return_transport.transport_type.value if return_transport else "bus",
                        estimated_cost=ret_cost,
                        currency=currency,
                        notes=f"Provider: {ret_prov}",
                        evidence=return_transport.evidence if return_transport else None
                    ))

                days.append(ItineraryDay(
                    day_number=d,
                    theme=f"Scenic Exploration & Return Journey" if d == days_to_plan else f"Immersive {destination} Heritage",
                    items=items,
                    daily_cost=round(day_cost, 2)
                ))

        return days
