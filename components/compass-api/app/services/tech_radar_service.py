from typing import Dict, List

from app.core.database import get_database
from app.models.category import CategoryInDB
from app.models.solution import RecommendStatusEnum
from app.models.tech_radar import TechRadarData, TechRadarEntry


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

        # Status to ring mapping (0-based index)
        status_to_ring: Dict[RecommendStatusEnum, int] = {
            "ADOPT": 0,
            "TRIAL": 1,
            "ASSESS": 2,
            "HOLD": 3,
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
                link=f"/solutions/{solution.get('slug', '')}",
                active=True,  # Always true for approved solutions
                moved=0,  # Always 0 as per requirements
            )
            entries.append(entry)

        # Create and return radar data with current date
        return TechRadarData.create_current(entries)

    async def get_radar_quadrants(self) -> List[Dict[str, str]]:
        """Get radar quadrants from categories collection.
        Returns categories with radar_quadrant >= 0, ordered by radar_quadrant.
        """
        # Find all categories with radar_quadrant >= 0 and sort by radar_quadrant
        cursor = self.categories.find({"radar_quadrant": {"$gte": 0}}, {"name": 1, "radar_quadrant": 1, "_id": 0}).sort(
            "radar_quadrant", 1
        )

        # Create a list to store quadrants in order
        quadrants = [None] * 4  # Initialize with None for all possible positions

        # Fill the quadrants list based on radar_quadrant value
        async for category in cursor:
            quadrant_index = category["radar_quadrant"]
            if 0 <= quadrant_index < 4:  # Ensure index is valid
                quadrants[quadrant_index] = {"name": category["name"]}

        # Filter out any None values and create final list
        return [q for q in quadrants if q is not None]

    def get_radar_rings(self) -> List[Dict[str, str]]:
        """Get radar rings in order (ADOPT, TRIAL, ASSESS, HOLD)."""
        return [{"name": status} for status in RecommendStatusEnum.__args__]
