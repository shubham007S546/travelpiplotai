"""Budget and Cost Optimization Models with Grounded Uncertainty."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class BudgetCategoryItem(BaseModel):
    """Structured line item with provenance, uncertainty, and grounding."""
    category: str
    amount: float = Field(default=0.0, ge=0.0)
    min_amount: float = Field(default=0.0, ge=0.0)
    max_amount: float = Field(default=0.0, ge=0.0)
    type: str = Field(default="ESTIMATED", description="LIVE, OFFICIAL_TARIFF, ESTIMATED, UNKNOWN")
    source: str = Field(default="Tariff Model / Local Rates")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0)


class BudgetBreakdown(BaseModel):
    """Detailed category-by-category arithmetic budget breakdown with uncertainty modeling."""
    total_budget: float = Field(..., ge=0.0)
    intercity_transport_cost: float = Field(default=0.0, ge=0.0)
    stay_cost: float = Field(default=0.0, ge=0.0)
    food_cost: float = Field(default=0.0, ge=0.0)
    activity_cost: float = Field(default=0.0, ge=0.0)
    local_mobility_cost: float = Field(default=0.0, ge=0.0)
    emergency_reserve: float = Field(default=0.0, ge=0.0)
    total_estimated_cost: float = Field(default=0.0, ge=0.0)
    remaining_budget: float = Field(default=0.0)
    budget_utilization_pct: float = Field(default=0.0)
    is_feasible: bool = Field(default=True)
    violation_amount: float = Field(default=0.0, ge=0.0)
    currency: str = Field(default="INR")
    category_shares: Dict[str, float] = Field(default_factory=dict)
    downgrade_suggestions: List[str] = Field(default_factory=list)

    # Uncertainty bounds
    minimum_cost: float = Field(default=0.0, ge=0.0)
    expected_cost: float = Field(default=0.0, ge=0.0)
    maximum_cost: float = Field(default=0.0, ge=0.0)
    feasibility_status_message: str = Field(default="Budget compliant")
    category_items: List[BudgetCategoryItem] = Field(default_factory=list)

    @classmethod
    def compute(
        cls,
        total_budget: float,
        intercity_transport: float,
        stay: float,
        food: float,
        activities: float,
        local_mobility: float,
        emergency_pct: float = 0.08,
        currency: str = "INR",
        category_items: Optional[List[BudgetCategoryItem]] = None
    ) -> "BudgetBreakdown":
        """Deterministic pure-Python budget arithmetic with range uncertainty."""
        subtotal = intercity_transport + stay + food + activities + local_mobility
        emergency = round(total_budget * emergency_pct, 2)
        total = round(subtotal + emergency, 2)
        remaining = round(total_budget - total, 2)
        violation = round(max(0.0, -remaining), 2)
        is_feasible = remaining >= 0.0
        utilization = round((total / total_budget * 100) if total_budget > 0 else 0.0, 1)

        # Build default category items if not passed
        items = category_items or [
            BudgetCategoryItem(
                category="Intercity Transport",
                amount=intercity_transport,
                min_amount=round(intercity_transport * 0.9, 2),
                max_amount=round(intercity_transport * 1.15, 2),
                type="ESTIMATED" if intercity_transport > 0 else "UNKNOWN",
                source="Route Distance + Tariff Model",
                confidence=0.85
            ),
            BudgetCategoryItem(
                category="Stay",
                amount=stay,
                min_amount=round(stay * 0.9, 2),
                max_amount=round(stay * 1.20, 2),
                type="ESTIMATED" if stay > 0 else "UNKNOWN",
                source="Lodging Tariff Matrix",
                confidence=0.88
            ),
            BudgetCategoryItem(
                category="Food",
                amount=food,
                min_amount=round(food * 0.85, 2),
                max_amount=round(food * 1.25, 2),
                type="ESTIMATED",
                source="Local Meal Rate Card",
                confidence=0.80
            ),
            BudgetCategoryItem(
                category="Activities",
                amount=activities,
                min_amount=activities,
                max_amount=round(activities * 1.1, 2),
                type="OFFICIAL_TARIFF" if activities > 0 else "ESTIMATED",
                source="Attraction Entry Rates",
                confidence=0.90
            ),
            BudgetCategoryItem(
                category="Local Mobility",
                amount=local_mobility,
                min_amount=round(local_mobility * 0.8, 2),
                max_amount=round(local_mobility * 1.3, 2),
                type="ESTIMATED",
                source="Local Transit Matrix",
                confidence=0.82
            )
        ]

        min_total = round(sum(i.min_amount for i in items) + emergency, 2)
        exp_total = total
        max_total = round(sum(i.max_amount for i in items) + emergency, 2)

        # Explainable feasibility message considering bounds
        if total_budget <= 0:
            msg = "No budget specified"
        elif total_budget < min_total:
            msg = f"Budget insufficient: Minimum feasible cost is {currency} {min_total:,.0f}"
        elif min_total <= total_budget < max_total:
            msg = f"Potentially feasible, but the upper-bound estimate ({currency} {max_total:,.0f}) exceeds your budget."
        else:
            msg = f"Fully budget compliant (Expected: {currency} {exp_total:,.0f}, Max: {currency} {max_total:,.0f})"

        shares = {}
        if total > 0:
            shares = {
                "Intercity Transport": round(intercity_transport / total * 100, 1),
                "Stay": round(stay / total * 100, 1),
                "Food": round(food / total * 100, 1),
                "Activities": round(activities / total * 100, 1),
                "Local Movement": round(local_mobility / total * 100, 1),
                "Emergency Reserve": round(emergency / total * 100, 1),
            }

        return cls(
            total_budget=total_budget,
            intercity_transport_cost=intercity_transport,
            stay_cost=stay,
            food_cost=food,
            activity_cost=activities,
            local_mobility_cost=local_mobility,
            emergency_reserve=emergency,
            total_estimated_cost=total,
            remaining_budget=remaining,
            budget_utilization_pct=utilization,
            is_feasible=is_feasible,
            violation_amount=violation,
            currency=currency,
            category_shares=shares,
            minimum_cost=min_total,
            expected_cost=exp_total,
            maximum_cost=max_total,
            feasibility_status_message=msg,
            category_items=items
        )

    @property
    def total_cost(self) -> float:
        return self.total_estimated_cost

    @property
    def transport_cost(self) -> float:
        return self.intercity_transport_cost

    @property
    def accommodation_cost(self) -> float:
        return self.stay_cost

    @property
    def activities_cost(self) -> float:
        return self.activity_cost

    @property
    def local_transit_cost(self) -> float:
        return self.local_mobility_cost

    @property
    def buffer_contingency(self) -> float:
        return self.emergency_reserve

    @property
    def savings(self) -> float:
        return max(0.0, self.remaining_budget)

    @property
    def feasibility_status(self) -> str:
        return "PASSED" if self.is_feasible else "FAILED"
