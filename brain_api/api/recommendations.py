from fastapi import APIRouter, HTTPException, status

from ..schemas import RecommendationRequest, RecommendationResponse
from .dependencies import RecommendationServiceDep

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post(
    "",
    response_model=RecommendationResponse,
    summary="Get charging station recommendation",
)
def get_recommendation(
    request: RecommendationRequest,
    service: RecommendationServiceDep,
) -> RecommendationResponse:
    """
    Get a charging station recommendation based on vehicle position and battery level.
    
    The recommendation algorithm considers:
    - Distance from vehicle to charging stations
    - Available charging power at nodes
    - Current node occupancy status
    - Vehicle battery urgency
    """
    try:
        recommendation = service.get_recommendation(request)
        
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No available charging stations found"
            )
        
        return recommendation
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendation: {str(e)}"
        )
