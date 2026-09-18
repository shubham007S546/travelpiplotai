"""Deterministic Budget Optimization and Grounded Arithmetic Engine."""

from typing import List, Tuple, Optional
from models.budget import BudgetBreakdown, BudgetCategoryItem
from models.transport import TransportOption, FareType
from models.accommodation import StayOption
from models.activity import ActivityOption, FoodOption
from utils.logging import logger


class BudgetOptimizer:
    """Performs deterministic financial allocation and automated constraint repair with uncertainty ranges."""

    @staticmethod
    def calculate_cost(
        budget: float,
        outbound_transport: Optional[TransportOption],
        return_transport: Optional[TransportOption],
        stay: Optional[StayOption],
        food_list: List[FoodOption],
        activity_list: List[ActivityOption],
        local_transit_cost: float,
        travelers: int = 1,
        nights: int = 1,
        currency: str = "INR"
    ) -> BudgetBreakdown:
        # Calculate cost components handling nullable fares
        out_price = outbound_transport.price if outbound_transport else 0.0
        ret_price = return_transport.price if return_transport else 0.0
        transport_cost = (out_price + ret_price) * travelers

        stay_price = stay.price_per_night_safe if stay else 0.0
        stay_cost = stay_price * nights

        food_cost = sum(f.cost_estimate * travelers for f in food_list)
        activity_cost = sum(a.cost * travelers for a in activity_list)
        total_local = local_transit_cost * travelers

        # Determine types and provenance
        out_type = outbound_transport.fare_type if outbound_transport else "UNKNOWN"
        ret_type = return_transport.fare_type if return_transport else "UNKNOWN"
        trans_type = "LIVE" if (out_type == "LIVE" and ret_type == "LIVE") else (
            "OFFICIAL_TARIFF" if (out_type in ("LIVE", "OFFICIAL_TARIFF") and ret_type in ("LIVE", "OFFICIAL_TARIFF")) else "ESTIMATED"
        )
        if transport_cost == 0.0 and (not outbound_transport or outbound_transport.fare is None):
            trans_type = "UNKNOWN"

        stay_type = "LIVE" if (stay and stay.price_per_night is not None) else "UNKNOWN"

        category_items = [
            BudgetCategoryItem(
                category="Intercity Transport",
                amount=round(transport_cost, 2),
                min_amount=round(transport_cost * 0.90, 2),
                max_amount=round(transport_cost * 1.15, 2),
                type=trans_type,
                source=outbound_transport.provider if outbound_transport else "Route Engine",
                confidence=0.90 if trans_type != "UNKNOWN" else 0.0
            ),
            BudgetCategoryItem(
                category="Stay",
                amount=round(stay_cost, 2),
                min_amount=round(stay_cost * 0.90, 2),
                max_amount=round(stay_cost * 1.25, 2),
                type=stay_type,
                source=stay.name if stay else "Lodging Matrix",
                confidence=0.92 if stay_type == "LIVE" else 0.50
            ),
            BudgetCategoryItem(
                category="Food",
                amount=round(food_cost, 2),
                min_amount=round(food_cost * 0.85, 2),
                max_amount=round(food_cost * 1.20, 2),
                type="ESTIMATED",
                source="Regional Meal Tariffs",
                confidence=0.85
            ),
            BudgetCategoryItem(
                category="Activities",
                amount=round(activity_cost, 2),
                min_amount=round(activity_cost, 2),
                max_amount=round(activity_cost * 1.10, 2),
                type="OFFICIAL_TARIFF" if activity_cost > 0 else "ESTIMATED",
                source="Attraction Entry Tariffs",
                confidence=0.92
            ),
            BudgetCategoryItem(
                category="Local Mobility",
                amount=round(total_local, 2),
                min_amount=round(total_local * 0.80, 2),
                max_amount=round(total_local * 1.30, 2),
                type="ESTIMATED",
                source="Local Transit Matrix",
                confidence=0.85
            )
        ]

        return BudgetBreakdown.compute(
            total_budget=budget,
            intercity_transport=round(transport_cost, 2),
            stay=round(stay_cost, 2),
            food=round(food_cost, 2),
            activities=round(activity_cost, 2),
            local_mobility=round(total_local, 2),
            emergency_pct=0.08,
            currency=currency,
            category_items=category_items
        )

    @classmethod
    def repair_budget(
        cls,
        budget: float,
        outbound_options: List[TransportOption],
        return_options: List[TransportOption],
        stay_options: List[StayOption],
        food_options: List[FoodOption],
        activity_options: List[ActivityOption],
        travelers: int = 1,
        nights: int = 1,
        currency: str = "INR"
    ) -> Tuple[Optional[TransportOption], Optional[TransportOption], Optional[StayOption], List[FoodOption], List[ActivityOption], float, BudgetBreakdown]:
        """Greedy deterministic repair algorithm ensuring constraint satisfaction."""
        sorted_outbound = sorted(outbound_options, key=lambda x: x.price)
        sorted_return = sorted(return_options, key=lambda x: x.price)
        sorted_stays = sorted(stay_options, key=lambda x: x.price_per_night_safe)

        selected_outbound = sorted_outbound[0] if sorted_outbound else None
        selected_return = sorted_return[0] if sorted_return else None
        selected_stay = sorted_stays[0] if sorted_stays else None

        economical_food = [f for f in food_options if f.price_level == "cheap"] or food_options[:2]
        selected_food = economical_food[:3]

        sorted_activities = sorted(activity_options, key=lambda x: x.cost)
        selected_activities = sorted_activities[:3]

        local_transit_cost = 35.0  # economical local transit

        breakdown = cls.calculate_cost(
            budget=budget,
            outbound_transport=selected_outbound,
            return_transport=selected_return,
            stay=selected_stay,
            food_list=selected_food,
            activity_list=selected_activities,
            local_transit_cost=local_transit_cost,
            travelers=travelers,
            nights=nights,
            currency=currency
        )

        suggestions = []
        if not breakdown.is_feasible:
            free_activities = [a for a in selected_activities if a.cost == 0.0]
            if len(free_activities) < len(selected_activities):
                selected_activities = free_activities
                suggestions.append("Replaced ticketed activities with free viewpoints and heritage sites.")
                breakdown = cls.calculate_cost(
                    budget=budget,
                    outbound_transport=selected_outbound,
                    return_transport=selected_return,
                    stay=selected_stay,
                    food_list=selected_food,
                    activity_list=selected_activities,
                    local_transit_cost=local_transit_cost,
                    travelers=travelers,
                    nights=nights,
                    currency=currency
                )

        if not breakdown.is_feasible:
            min_required = breakdown.total_estimated_cost
            suggestions.append(
                f"No feasible plan exists under {currency} {budget:.0f}. "
                f"Minimum baseline cost is {currency} {min_required:.0f}. "
                f"Consider increasing budget by {currency} {breakdown.violation_amount:.0f} or reducing nights."
            )

        breakdown.downgrade_suggestions = suggestions
        return (selected_outbound, selected_return, selected_stay, selected_food, selected_activities, local_transit_cost, breakdown)
