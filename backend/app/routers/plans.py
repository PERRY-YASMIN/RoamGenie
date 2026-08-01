from fastapi import APIRouter, Depends
from app.schemas.itinerary import ItineraryProposal, TripPlanRequest
from app.services.ai_service import MockAIService, get_ai_service

router = APIRouter(prefix="/plans", tags=["plans"])

@router.post("/preview", response_model=ItineraryProposal)
def preview_plan(trip: TripPlanRequest, service: MockAIService = Depends(get_ai_service)) -> ItineraryProposal:
    """Return an unsaved mock proposal for early UI/contract integration."""
    return service.generate_itinerary(trip)

