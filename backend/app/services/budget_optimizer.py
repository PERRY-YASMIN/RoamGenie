from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional

from app.db.models.catalogue import Destination, Hotel, Restaurant, Attraction, TransportOption
from app.services.budget_service import BudgetCalculationResult, BudgetCalculator
from app.services.itinerary_scheduler import DeterministicScheduler, ScheduleResult


@dataclass
class OptimizationResult:
    schedule_result: ScheduleResult
    budget_result: BudgetCalculationResult
    optimization_applied: bool
    warnings: List[str]


class BudgetOptimizer:
    """Optimizes itineraries to fit within budget using deterministic catalogue alternatives."""

    def __init__(self):
        self.scheduler = DeterministicScheduler()
        self.calculator = BudgetCalculator()

    def optimize(
        self,
        destination: Destination,
        start_date: date,
        end_date: date,
        traveller_count: int,
        starting_location: str,
        total_budget: Decimal,
        preferences: Optional[List[str]] = None,
    ) -> OptimizationResult:
        # Step 1: Initial default schedule (preferred/top-rated)
        current_schedule = self.scheduler.schedule(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            traveller_count=traveller_count,
            starting_location=starting_location,
            preferences=preferences,
        )
        current_budget = self.calculator.calculate(
            total_budget=total_budget,
            scheduled_days=current_schedule.days,
        )

        if current_budget.deficit == Decimal("0.00"):
            return OptimizationResult(
                schedule_result=current_schedule,
                budget_result=current_budget,
                optimization_applied=False,
                warnings=[],
            )

        # Deficit detected -> Begin iterative optimization
        optimization_applied = False
        warnings: List[str] = []

        # Candidate pools sorted by lowest cost
        cheapest_hotels = sorted(destination.hotels or [], key=lambda h: h.price_per_night)
        
        matching_transports = [
            t for t in (destination.transport_options or [])
            if t.origin.strip().lower() == starting_location.strip().lower()
        ]
        pool_transports = matching_transports if matching_transports else (destination.transport_options or [])
        cheapest_transports = sorted(pool_transports, key=lambda t: t.estimated_cost)

        cheapest_restaurants = sorted(
            destination.restaurants or [],
            key=lambda r: r.average_cost_per_person or Decimal("0.00"),
        )
        cheapest_attractions = sorted(
            destination.attractions or [],
            key=lambda a: a.entry_fee,
        )

        selected_hotel = current_schedule.selected_hotel
        selected_transport = current_schedule.selected_transport
        selected_restaurants: Optional[List[Restaurant]] = None
        selected_attractions: Optional[List[Attraction]] = None

        # Optimization Step 1: Swap Hotel to cheapest available
        if cheapest_hotels and (not selected_hotel or selected_hotel.id != cheapest_hotels[0].id):
            selected_hotel = cheapest_hotels[0]
            optimization_applied = True
            current_schedule = self.scheduler.schedule(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                traveller_count=traveller_count,
                starting_location=starting_location,
                preferences=preferences,
                selected_hotel=selected_hotel,
                selected_transport=selected_transport,
                selected_restaurants=selected_restaurants,
                selected_attractions=selected_attractions,
            )
            current_budget = self.calculator.calculate(total_budget, current_schedule.days)
            if current_budget.deficit == Decimal("0.00"):
                warnings.append(f"Optimized budget: Switched accommodation to economical stay at '{selected_hotel.name}'.")
                return OptimizationResult(
                    schedule_result=current_schedule,
                    budget_result=current_budget,
                    optimization_applied=True,
                    warnings=warnings,
                )

        # Optimization Step 2: Swap Transport to cheapest mode
        if cheapest_transports and (not selected_transport or selected_transport.id != cheapest_transports[0].id):
            selected_transport = cheapest_transports[0]
            optimization_applied = True
            current_schedule = self.scheduler.schedule(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                traveller_count=traveller_count,
                starting_location=starting_location,
                preferences=preferences,
                selected_hotel=selected_hotel,
                selected_transport=selected_transport,
                selected_restaurants=selected_restaurants,
                selected_attractions=selected_attractions,
            )
            current_budget = self.calculator.calculate(total_budget, current_schedule.days)
            if current_budget.deficit == Decimal("0.00"):
                warnings.append(f"Optimized budget: Switched transit to budget mode ({selected_transport.mode.title()}).")
                return OptimizationResult(
                    schedule_result=current_schedule,
                    budget_result=current_budget,
                    optimization_applied=True,
                    warnings=warnings,
                )

        # Optimization Step 3: Swap Dining to cheapest restaurants
        if cheapest_restaurants:
            selected_restaurants = cheapest_restaurants
            optimization_applied = True
            current_schedule = self.scheduler.schedule(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                traveller_count=traveller_count,
                starting_location=starting_location,
                preferences=preferences,
                selected_hotel=selected_hotel,
                selected_transport=selected_transport,
                selected_restaurants=selected_restaurants,
                selected_attractions=selected_attractions,
            )
            current_budget = self.calculator.calculate(total_budget, current_schedule.days)
            if current_budget.deficit == Decimal("0.00"):
                warnings.append("Optimized budget: Selected affordable regional dining options.")
                return OptimizationResult(
                    schedule_result=current_schedule,
                    budget_result=current_budget,
                    optimization_applied=True,
                    warnings=warnings,
                )

        # Optimization Step 4: Swap Attractions to free / lowest fee
        if cheapest_attractions:
            selected_attractions = cheapest_attractions
            optimization_applied = True
            current_schedule = self.scheduler.schedule(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                traveller_count=traveller_count,
                starting_location=starting_location,
                preferences=preferences,
                selected_hotel=selected_hotel,
                selected_transport=selected_transport,
                selected_restaurants=selected_restaurants,
                selected_attractions=selected_attractions,
            )
            current_budget = self.calculator.calculate(total_budget, current_schedule.days)
            if current_budget.deficit == Decimal("0.00"):
                warnings.append("Optimized budget: Prioritized free and low-entry-fee attractions.")
                return OptimizationResult(
                    schedule_result=current_schedule,
                    budget_result=current_budget,
                    optimization_applied=True,
                    warnings=warnings,
                )

        # Unavoidable deficit remains even after choosing all cheapest options
        warnings.append(
            f"Unavoidable deficit: Even after applying all lowest-cost catalogue alternatives, "
            f"the estimated cost (₹{current_budget.estimated_total}) exceeds the budget (₹{current_budget.total_budget}) "
            f"by ₹{current_budget.deficit}."
        )
        return OptimizationResult(
            schedule_result=current_schedule,
            budget_result=current_budget,
            optimization_applied=optimization_applied,
            warnings=warnings,
        )


_budget_optimizer = BudgetOptimizer()


def get_budget_optimizer() -> BudgetOptimizer:
    return _budget_optimizer

