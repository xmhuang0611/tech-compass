from typing import Dict, List

from fastapi import APIRouter, Depends

from app.models.tech_radar import TechRadarData
from app.services.tech_radar_service import TechRadarService

router = APIRouter()


@router.get("/data", response_model=TechRadarData)
async def get_tech_radar_data(
    tech_radar_service: TechRadarService = Depends(),
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


@router.get("/quadrants", response_model=List[Dict[str, str]])
async def get_radar_quadrants(
    tech_radar_service: TechRadarService = Depends(),
) -> List[Dict[str, str]]:
    """Get radar quadrants ordered by their radar_quadrant value.

    Returns a list of categories that have radar_quadrant >= 0,
    ordered by their radar_quadrant value.
    Each quadrant is represented by its name.
    """
    return await tech_radar_service.get_radar_quadrants()


@router.get("/rings", response_model=List[Dict[str, str]])
def get_radar_rings(
    tech_radar_service: TechRadarService = Depends(),
) -> List[Dict[str, str]]:
    """Get radar rings in order.

    Returns a fixed list of rings in order:
    - ADOPT (innermost ring)
    - TRIAL
    - ASSESS
    - HOLD (outermost ring)
    """
    return tech_radar_service.get_radar_rings()
