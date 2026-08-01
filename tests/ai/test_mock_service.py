from datetime import date
from decimal import Decimal
from app.schemas.itinerary import TripPlanRequest
from app.services.ai_service import MockAIService

def test_mock_works_without_key() -> None:
    trip=TripPlanRequest(starting_location="Chennai",destination="Mysuru",start_date=date(2026,8,10),end_date=date(2026,8,10),travellers=1,total_budget=Decimal("1000"))
    result=MockAIService().generate_itinerary(trip)
    assert result.provider=="mock"
    assert result.estimated_total==Decimal("1000.00")

