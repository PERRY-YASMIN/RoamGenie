from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List

from app.schemas.trip import BudgetAllocationResponse, BudgetSummaryResponse
from app.services.itinerary_scheduler import ScheduledDay


@dataclass
class BudgetCalculationResult:
    total_budget: Decimal
    estimated_total: Decimal
    remaining_budget: Decimal
    deficit: Decimal
    utilization_percentage: Decimal
    status: str  # 'within_budget', 'exact', 'over_budget'
    category_totals: Dict[str, Decimal] = field(default_factory=dict)
    allocations: List[BudgetAllocationResponse] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_summary_response(self) -> BudgetSummaryResponse:
        return BudgetSummaryResponse(
            total_budget=self.total_budget,
            estimated_total=self.estimated_total,
            remaining_budget=self.remaining_budget,
            deficit=self.deficit,
            utilization_percentage=self.utilization_percentage,
            status=self.status,
            categories=self.allocations,
            warnings=self.warnings,
        )


class BudgetCalculator:
    """Calculates category aggregations, deficits, remaining budgets, and status."""

    STANDARD_CATEGORIES = [
        "accommodation",
        "transportation",
        "food",
        "attractions",
    ]

    def calculate(
        self, total_budget: Decimal, scheduled_days: List[ScheduledDay]
    ) -> BudgetCalculationResult:
        # Standardize precision
        budget = total_budget.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        category_totals: Dict[str, Decimal] = {cat: Decimal("0.00") for cat in self.STANDARD_CATEGORIES}

        # Aggregate items across days
        for day in scheduled_days:
            for item in day.items:
                cat = item.category.lower().strip()
                if cat in ("attraction", "attractions", "activity", "activities"):
                    norm_cat = "attractions"
                elif cat in ("hotel", "accommodation", "stay"):
                    norm_cat = "accommodation"
                elif cat in ("food", "dining", "restaurant", "meal"):
                    norm_cat = "food"
                elif cat in ("transport", "transportation", "transit"):
                    norm_cat = "transportation"
                else:
                    norm_cat = "other"

                cost = item.estimated_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                category_totals[norm_cat] = category_totals.get(norm_cat, Decimal("0.00")) + cost

        estimated_total = sum(category_totals.values(), Decimal("0.00")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        remaining_budget = (budget - estimated_total).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        deficit = max(Decimal("0.00"), (estimated_total - budget)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if budget > Decimal("0.00"):
            utilization_pct = ((estimated_total / budget) * Decimal("100.00")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            utilization_pct = Decimal("0.00")

        if remaining_budget > Decimal("0.00"):
            budget_status = "within_budget"
        elif remaining_budget == Decimal("0.00"):
            budget_status = "exact"
        else:
            budget_status = "over_budget"

        warnings: List[str] = []
        if deficit > Decimal("0.00"):
            warnings.append(
                f"Estimated trip cost (₹{estimated_total}) exceeds total budget (₹{budget}) by ₹{deficit}."
            )
            # Find largest expense category
            top_category = max(category_totals.items(), key=lambda x: x[1])
            warnings.append(
                f"Highest cost driver: '{top_category[0]}' at ₹{top_category[1]}."
            )

        allocations = [
            BudgetAllocationResponse(
                category=cat,
                amount=amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
                trip_id=0,
            )
            for cat, amount in category_totals.items()
        ]

        return BudgetCalculationResult(
            total_budget=budget,
            estimated_total=estimated_total,
            remaining_budget=remaining_budget,
            deficit=deficit,
            utilization_percentage=utilization_pct,
            status=budget_status,
            category_totals=category_totals,
            allocations=allocations,
            warnings=warnings,
        )
