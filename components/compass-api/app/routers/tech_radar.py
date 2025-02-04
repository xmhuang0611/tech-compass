from fastapi import APIRouter, Depends

from app.models.tech_radar import TechRadarData
from app.services.tech_radar_service import TechRadarService

router = APIRouter()

@router.get("/data", response_model=TechRadarData)
async def get_tech_radar_data(
    tech_radar_service: TechRadarService = Depends()
) -> TechRadarData:
    """Get tech radar data in Zalando Tech Radar format.
    
    Returns a list of all approved solutions with their:
    - quadrant (from category's radar_quadrant)
    - ring (mapped from recommend_status: ADOPT=1, TRIAL=2, ASSESS=3, HOLD=4)
    - label (solution name)
    - active (always true for approved solutions)
    - moved (always 0)
    """
    return await tech_radar_service.get_tech_radar_data() 