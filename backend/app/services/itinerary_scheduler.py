from dataclasses import dataclass, field
from datetime import date, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional

from app.db.models.catalogue import (
    Attraction,
    Destination,
    Hotel,
    Restaurant,
    TransportOption,
)


@dataclass
class ScheduledItem:
    item_order: int
    start_time: Optional[time]
    title: str
    category: str
    estimated_cost: Decimal
    notes: Optional[str] = None


@dataclass
class ScheduledDay:
    day_number: int
    itinerary_date: date
    items: List[ScheduledItem] = field(default_factory=list)


@dataclass
class ScheduleResult:
    destination: Destination
    start_date: date
    end_date: date
    day_count: int
    traveller_count: int
    selected_hotel: Optional[Hotel]
    selected_transport: Optional[TransportOption]
    days: List[ScheduledDay]
    summary: str


class DeterministicScheduler:
    """Deterministic itinerary scheduler mapping catalogue data to day-wise activities."""

    def schedule(
        self,
        destination: Destination,
        start_date: date,
        end_date: date,
        traveller_count: int,
        starting_location: str,
        preferences: Optional[List[str]] = None,
        selected_hotel: Optional[Hotel] = None,
        selected_transport: Optional[TransportOption] = None,
        selected_restaurants: Optional[List[Restaurant]] = None,
        selected_attractions: Optional[List[Attraction]] = None,
    ) -> ScheduleResult:
        day_count = (end_date - start_date).days + 1
        prefs = [p.lower().strip() for p in (preferences or []) if p.strip()]

        # 1. Resolve Hotel
        hotel = selected_hotel
        if hotel is None and destination.hotels:
            # Pick highest rated hotel, tie-broken by lowest price
            sorted_hotels = sorted(
                destination.hotels,
                key=lambda h: (-(h.rating or Decimal("0")), h.price_per_night),
            )
            hotel = sorted_hotels[0]

        # 2. Resolve Transport
        transport = selected_transport
        if transport is None and destination.transport_options:
            matching_origin = [
                t for t in destination.transport_options
                if t.origin.strip().lower() == starting_location.strip().lower()
            ]
            if matching_origin:
                # Prefer train or flight, tie-broken by cost
                transport = sorted(matching_origin, key=lambda t: t.estimated_cost)[0]
            else:
                transport = sorted(destination.transport_options, key=lambda t: t.estimated_cost)[0]

        # 3. Resolve Attractions Pool
        attractions = selected_attractions
        if attractions is None:
            if destination.attractions:
                def attraction_score(a: Attraction) -> tuple:
                    matches_pref = 1 if any(p in (a.category or "").lower() or p in a.name.lower() for p in prefs) else 0
                    rating = float(a.rating or 0)
                    return (-matches_pref, -rating, float(a.entry_fee))

                attractions = sorted(destination.attractions, key=attraction_score)
            else:
                attractions = []

        # 4. Resolve Restaurants Pool
        restaurants = selected_restaurants
        if restaurants is None:
            if destination.restaurants:
                def restaurant_score(r: Restaurant) -> tuple:
                    matches_pref = 1 if any(p in (r.cuisine or "").lower() or p in r.name.lower() for p in prefs) else 0
                    rating = float(r.rating or 0)
                    return (-matches_pref, -rating, float(r.average_cost_per_person or 0))

                restaurants = sorted(destination.restaurants, key=restaurant_score)
            else:
                restaurants = []

        # Build day-wise schedule
        days: List[ScheduledDay] = []
        attraction_index = 0
        restaurant_index = 0

        def get_next_attraction() -> Optional[Attraction]:
            nonlocal attraction_index
            if not attractions:
                return None
            att = attractions[attraction_index % len(attractions)]
            attraction_index += 1
            return att

        def get_next_restaurant() -> Optional[Restaurant]:
            nonlocal restaurant_index
            if not restaurants:
                return None
            rest = restaurants[restaurant_index % len(restaurants)]
            restaurant_index += 1
            return rest

        for day_num in range(1, day_count + 1):
            curr_date = start_date + timedelta(days=day_num - 1)
            day_items: List[ScheduledItem] = []
            item_order = 1

            if day_num == 1:
                # --- DAY 1 ---
                # Transport arrival
                if transport:
                    trans_cost = (transport.estimated_cost * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(8, 30),
                            title=f"Transit from {starting_location} to {destination.city} ({transport.mode.title()})",
                            category="transportation",
                            estimated_cost=trans_cost,
                            notes=f"Provider: {transport.provider or 'Direct'} | Duration: {transport.duration_minutes or 120} mins",
                        )
                    )
                    item_order += 1
                else:
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(8, 30),
                            title=f"Arrival & Orientation in {destination.city}",
                            category="transportation",
                            estimated_cost=Decimal("0.00"),
                            notes="Self-arranged local transit",
                        )
                    )
                    item_order += 1

                # Hotel check-in
                if hotel:
                    hotel_cost = hotel.price_per_night.quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(11, 30),
                            title=f"Check-in at {hotel.name}",
                            category="accommodation",
                            estimated_cost=hotel_cost,
                            notes=f"Night 1 accommodation | Rating: {hotel.rating or 'N/A'}/5.0",
                        )
                    )
                    item_order += 1

                # Lunch
                lunch_rest = get_next_restaurant()
                if lunch_rest:
                    lunch_cost = ((lunch_rest.average_cost_per_person or Decimal("250.00")) * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(13, 0),
                            title=f"Welcome Lunch at {lunch_rest.name}",
                            category="food",
                            estimated_cost=lunch_cost,
                            notes=f"Cuisine: {lunch_rest.cuisine or 'Local Delicacies'}",
                        )
                    )
                    item_order += 1

                # Afternoon Attraction
                att1 = get_next_attraction()
                if att1:
                    att1_cost = (att1.entry_fee * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(15, 30),
                            title=f"Visit {att1.name}",
                            category="attractions",
                            estimated_cost=att1_cost,
                            notes=f"Category: {att1.category or 'Sightseeing'} | Rating: {att1.rating or 'N/A'}/5.0",
                        )
                    )
                    item_order += 1

                # Evening Dinner
                dinner_rest = get_next_restaurant()
                if dinner_rest:
                    dinner_cost = ((dinner_rest.average_cost_per_person or Decimal("350.00")) * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(19, 30),
                            title=f"Dinner at {dinner_rest.name}",
                            category="food",
                            estimated_cost=dinner_cost,
                            notes=f"Cuisine: {dinner_rest.cuisine or 'Regional Dining'}",
                        )
                    )
                    item_order += 1

            elif day_num < day_count:
                # --- MIDDLE DAYS (Day 2 to N-1) ---
                # Daily Hotel stay
                if hotel:
                    hotel_cost = hotel.price_per_night.quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(9, 0),
                            title=f"Stay at {hotel.name}",
                            category="accommodation",
                            estimated_cost=hotel_cost,
                            notes=f"Night {day_num} accommodation",
                        )
                    )
                    item_order += 1

                # Morning Attraction
                att_m = get_next_attraction()
                if att_m:
                    att_m_cost = (att_m.entry_fee * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(10, 30),
                            title=f"Morning Excursion: {att_m.name}",
                            category="attractions",
                            estimated_cost=att_m_cost,
                            notes=f"Category: {att_m.category or 'Sightseeing'}",
                        )
                    )
                    item_order += 1

                # Midday Lunch
                lunch_rest = get_next_restaurant()
                if lunch_rest:
                    lunch_cost = ((lunch_rest.average_cost_per_person or Decimal("250.00")) * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(13, 0),
                            title=f"Lunch at {lunch_rest.name}",
                            category="food",
                            estimated_cost=lunch_cost,
                            notes=f"Cuisine: {lunch_rest.cuisine or 'Local Dining'}",
                        )
                    )
                    item_order += 1

                # Afternoon Attraction
                att_a = get_next_attraction()
                if att_a:
                    att_a_cost = (att_a.entry_fee * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(15, 30),
                            title=f"Afternoon Tour: {att_a.name}",
                            category="attractions",
                            estimated_cost=att_a_cost,
                            notes=f"Category: {att_a.category or 'Sightseeing'}",
                        )
                    )
                    item_order += 1

                # Evening Dinner
                dinner_rest = get_next_restaurant()
                if dinner_rest:
                    dinner_cost = ((dinner_rest.average_cost_per_person or Decimal("350.00")) * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(19, 30),
                            title=f"Dinner at {dinner_rest.name}",
                            category="food",
                            estimated_cost=dinner_cost,
                            notes=f"Cuisine: {dinner_rest.cuisine or 'Evening Dining'}",
                        )
                    )
                    item_order += 1

            else:
                # --- FINAL DAY (Day N) ---
                # Morning Attraction
                att_final = get_next_attraction()
                if att_final:
                    att_f_cost = (att_final.entry_fee * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(9, 30),
                            title=f"Morning Visit: {att_final.name}",
                            category="attractions",
                            estimated_cost=att_f_cost,
                            notes=f"Category: {att_final.category or 'Sightseeing'}",
                        )
                    )
                    item_order += 1

                # Farewell Lunch
                lunch_rest = get_next_restaurant()
                if lunch_rest:
                    lunch_cost = ((lunch_rest.average_cost_per_person or Decimal("300.00")) * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(12, 30),
                            title=f"Farewell Lunch at {lunch_rest.name}",
                            category="food",
                            estimated_cost=lunch_cost,
                            notes=f"Cuisine: {lunch_rest.cuisine or 'Regional Fare'}",
                        )
                    )
                    item_order += 1

                # Hotel check-out
                if hotel and day_count > 1:
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(15, 0),
                            title=f"Check-out from {hotel.name}",
                            category="accommodation",
                            estimated_cost=Decimal("0.00"),
                            notes="Settle incidental charges and pack luggage",
                        )
                    )
                    item_order += 1

                # Return Transit
                if transport:
                    ret_cost = (transport.estimated_cost * traveller_count).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(17, 30),
                            title=f"Return Transit to {starting_location} ({transport.mode.title()})",
                            category="transportation",
                            estimated_cost=ret_cost,
                            notes=f"Provider: {transport.provider or 'Direct'}",
                        )
                    )
                    item_order += 1
                else:
                    day_items.append(
                        ScheduledItem(
                            item_order=item_order,
                            start_time=time(17, 30),
                            title=f"Departure from {destination.city}",
                            category="transportation",
                            estimated_cost=Decimal("0.00"),
                            notes="Self-arranged return transit",
                        )
                    )
                    item_order += 1

            days.append(
                ScheduledDay(
                    day_number=day_num,
                    itinerary_date=curr_date,
                    items=day_items,
                )
            )

        pref_str = ", ".join(prefs) if prefs else "general sightseeing"
        summary = (
            f"A {day_count}-day structured itinerary in {destination.city}, {destination.country} "
            f"for {traveller_count} traveller(s), tailored for {pref_str}."
        )

        return ScheduleResult(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            day_count=day_count,
            traveller_count=traveller_count,
            selected_hotel=hotel,
            selected_transport=transport,
            days=days,
            summary=summary,
        )
