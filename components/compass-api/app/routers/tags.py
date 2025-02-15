from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.core.auth import get_current_active_user, get_current_superuser
from app.models.response import StandardResponse
from app.models.solution import SolutionUpdate
from app.models.tag import Tag, TagCreate, TagUpdate, format_tag_name
from app.models.user import User
from app.services.solution_service import SolutionService
from app.services.tag_service import TagService

router = APIRouter()


@router.post("/", response_model=StandardResponse[Tag], status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: TagCreate,
    current_user: User = Depends(get_current_superuser),
    tag_service: TagService = Depends(),
) -> Any:
    """Create a new tag (superuser only)."""
    try:
        # Name is already formatted by the model validator
        result = await tag_service.create_tag(tag, current_user.username)
        tag_with_usage = await tag_service.get_tag_with_usage(result)
        return StandardResponse.of(tag_with_usage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=StandardResponse[List[Tag]])
async def get_tags(
    skip: int = 0,
    limit: int = 100,  # Default to 100 items
    show_all: bool = False,  # Default to only show tags with usage_count > 0
    tag_service: TagService = Depends(),
) -> Any:
    """Get all tags with pagination.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return (default: 100)
        show_all: If True, return all tags; if False, only return tags with usage_count > 0 (default: False)
    """
    tags = await tag_service.get_tags(skip=skip, limit=limit, show_all=show_all)
    total = await tag_service.count_tags(show_all=show_all)
    return StandardResponse.paginated(data=tags, total=total, skip=skip, limit=limit)


@router.get("/{tag_id}", response_model=StandardResponse[Tag])
async def get_tag(tag_id: str, tag_service: TagService = Depends()) -> Any:
    """Get a specific tag by ID."""
    tag = await tag_service.get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    tag_with_usage = await tag_service.get_tag_with_usage(tag)
    return StandardResponse.of(tag_with_usage)


@router.put("/{tag_id}", response_model=StandardResponse[Tag])
async def update_tag(
    tag_id: str,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_superuser),
    tag_service: TagService = Depends(),
) -> Any:
    """Update a tag by ID (superuser only).
    If tag name is changed to an existing tag name, the tags will be merged."""
    try:
        # Name will be formatted by the model validator
        tag = await tag_service.update_tag(
            tag_id=tag_id,
            tag_update=tag_update,
            username=current_user.username,
            update_solutions=True,
        )
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
        tag_with_usage = await tag_service.get_tag_with_usage(tag)
        return StandardResponse.of(tag_with_usage)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_tag(
    tag_id: str,
    current_user: User = Depends(get_current_superuser),
    tag_service: TagService = Depends(),
) -> None:
    """Delete a tag by ID (superuser only). Will also remove the tag from all solutions using it."""
    try:
        success = await tag_service.delete_tag(tag_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/solution/{solution_slug}", response_model=StandardResponse[List[Tag]])
async def get_solution_tags(solution_slug: str, tag_service: TagService = Depends()) -> Any:
    """Get all tags for a specific solution."""
    tags = await tag_service.get_solution_tags(solution_slug)
    return StandardResponse.of(tags)


@router.post(
    "/solution/{solution_slug}/tag/{tag_name}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_201_CREATED,
)
async def add_solution_tag(
    solution_slug: str,
    tag_name: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Add a tag to a solution. Creates the tag if it doesn't exist."""
    try:
        # Validate tag name is not empty
        if not tag_name or tag_name.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name cannot be empty",
            )

        # Format tag name
        formatted_tag_name = format_tag_name(tag_name)

        # Get the solution first
        solution = await solution_service.get_solution_by_slug(solution_slug)
        if not solution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")

        # Check if tag already exists in solution
        existing_tags = solution.tags or []
        if formatted_tag_name in existing_tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag '{formatted_tag_name}' is already added to this solution",
            )

        # Create tag if it doesn't exist and add it to solution
        solution_update = SolutionUpdate(tags=existing_tags + [formatted_tag_name])
        updated_solution = await solution_service.update_solution_by_slug(
            solution_slug, solution_update, current_user.username
        )
        if not updated_solution:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update solution with new tag",
            )

        return StandardResponse.of({"message": f"Tag '{formatted_tag_name}' added successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding tag to solution: {str(e)}",
        )


@router.delete(
    "/solution/{solution_slug}/tag/{tag_name}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def delete_solution_tag(
    solution_slug: str,
    tag_name: str,
    current_user: User = Depends(get_current_active_user),
    solution_service: SolutionService = Depends(),
) -> Any:
    """Remove a tag from a solution."""
    try:
        # Validate tag name is not empty
        if not tag_name or tag_name.isspace():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name cannot be empty",
            )

        # Format tag name
        formatted_tag_name = format_tag_name(tag_name)

        # Get the solution first
        solution = await solution_service.get_solution_by_slug(solution_slug)
        if not solution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")

        # Check if tag exists in solution
        existing_tags = solution.tags or []
        if formatted_tag_name not in existing_tags:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tag '{formatted_tag_name}' not found in this solution",
            )

        # Remove tag from solution
        updated_tags = [tag for tag in existing_tags if tag != formatted_tag_name]
        solution_update = SolutionUpdate(tags=updated_tags)
        updated_solution = await solution_service.update_solution_by_slug(
            solution_slug, solution_update, current_user.username
        )
        if not updated_solution:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update solution after removing tag",
            )

        return StandardResponse.of({"message": f"Tag '{formatted_tag_name}' removed successfully"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing tag from solution: {str(e)}",
        )
