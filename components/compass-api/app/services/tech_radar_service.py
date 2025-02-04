from typing import Dict, List

from app.core.database import get_database
from app.models.tech_radar import TechRadarEntry, TechRadarData
from app.models.category import CategoryInDB


class TechRadarService:
    def __init__(self):
        self.db = get_database()
        self.solutions = self.db.solutions
        self.categories = self.db.categories

    async def get_tech_radar_data(self) -> TechRadarData:
        """Generate tech radar data from approved solutions.
        Only includes solutions whose categories have radar_quadrant >= 0.
        """
        # Get all approved solutions
        cursor = self.solutions.find({"review_status": "APPROVED"})
        
        # Status to ring mapping (1-based as per requirements)
        status_to_ring: Dict[str, int] = {
            "ADOPT": 0,
            "TRIAL": 1,
            "ASSESS": 2,
            "HOLD": 3
        }
        
        entries: List[TechRadarEntry] = []
        async for solution in cursor:
            # Get category information
            category_data = await self.categories.find_one({"name": solution["category"]})
            if not category_data:
                continue  # Skip if category not found
            
            # Parse category data using CategoryInDB model
            category = CategoryInDB(**category_data)
            
            # Skip if radar_quadrant is negative
            if category.radar_quadrant < 0:
                continue
            
            # Create radar entry
            entry = TechRadarEntry(
                quadrant=category.radar_quadrant,
                ring=status_to_ring[solution["recommend_status"]],
                label=solution["name"],
                active=True,  # Always true for approved solutions
                moved=0  # Always 0 as per requirements
            )
            entries.append(entry)
        
        # Create and return radar data with current date
        return TechRadarData.create_current(entries) 