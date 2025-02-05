import streamlit as st
from utils.auth import login
from utils.api import APIClient
import pandas as pd
from utils.common import (
    initialize_page_state,
    render_grid,
    show_success_toast,
    show_error_message,
    format_dataframe_dates,
)

# Page configuration
st.set_page_config(
    page_title="Ratings - Tech Compass Admin",
    page_icon="⭐",
    layout="wide"
)

# Initialize session state
initialize_page_state({
    "authenticated": False,
    "selected_rating": None,
    "show_success_message": False,
    "show_error_message": None,
    "show_delete_success_toast": False,
    "page": 1
})

# Check authentication
if not st.session_state.authenticated:
    login()
    st.stop()

# Constants
COLUMN_DEFS = {
    "_id": {"width": 120, "headerName": "Rating ID"},
    "solution_slug": {"width": 150, "headerName": "Solution"},
    "score": {"width": 100, "headerName": "Score"},
    "comment": {"width": 400, "headerName": "Comment"},
    "username": {"width": 120, "headerName": "Username"},
    "full_name": {"width": 150, "headerName": "Full Name"},
    "created_at": {"width": 140, "headerName": "Created At"},
    "updated_at": {"width": 140, "headerName": "Updated At"},
}

def load_solutions():
    """Load all solutions for dropdown"""
    try:
        params = {"skip": 0, "limit": 100, "sort": "-updated_at"}
        response = APIClient.get("solutions/", params)
        if response and response.get("status_code") == 200:
            return response.get("data", [])
    except Exception as e:
        show_error_message(f"Failed to load solutions: {str(e)}")
    return []

def load_ratings(solution_slug=None, skip=0, limit=20):
    """Load ratings with pagination"""
    try:
        if solution_slug:
            # Load ratings for specific solution
            params = {
                "page": skip // limit + 1,
                "page_size": limit,
                "sort": "-created_at",
            }
            response = APIClient.get(f"ratings/solution/{solution_slug}", params)
        else:
            # Load all ratings
            params = {
                "page": skip // limit + 1,
                "page_size": limit,
                "sort": "-created_at",
            }
            response = APIClient.get("ratings/", params)

        if response and response.get("status_code") == 200:
            return response.get("data", []), {
                "total": response.get("total", 0),
                "skip": skip,
                "limit": limit,
            }
        else:
            show_error_message(response.get("detail", "Unknown error occurred"))
    except Exception as e:
        show_error_message(f"Failed to load ratings: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 20}

def load_rating_summary(solution_slug):
    """Load rating summary for a solution"""
    try:
        response = APIClient.get(f"ratings/solution/{solution_slug}/summary")
        if response and response.get("status_code") == 200:
            return response.get("data", {})
    except Exception as e:
        show_error_message(f"Failed to load rating summary: {str(e)}")
    return {}

def render_rating_details(rating_data):
    """Render rating details view"""
    st.subheader("Rating Details")

    # Display rating metadata
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Solution",
            value=rating_data.get("solution_slug", ""),
            disabled=True
        )
        st.text_input(
            "Username",
            value=rating_data.get("username", ""),
            disabled=True
        )
        st.text_input(
            "Full Name",
            value=rating_data.get("full_name", ""),
            disabled=True
        )
        st.text_input(
            "Created At",
            value=rating_data.get("created_at", ""),
            disabled=True
        )
    with col2:
        st.text_input(
            "Rating ID",
            value=rating_data.get("_id", ""),
            disabled=True
        )
        st.text_input(
            "Score",
            value=str(rating_data.get("score", "")),
            disabled=True
        )
        st.text_input(
            "Updated At",
            value=rating_data.get("updated_at", ""),
            disabled=True
        )

    # Rating content
    st.text_area(
        "Comment",
        value=rating_data.get("comment", ""),
        disabled=True,
        help="Rating comment"
    )

    # Load and display rating summary for the solution
    if rating_data.get("solution_slug"):
        st.subheader("Solution Rating Summary")
        summary = load_rating_summary(rating_data["solution_slug"])

        if summary:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Rating", f"{summary.get('average', 0):.1f} ⭐")
                st.metric("Total Ratings", summary.get("count", 0))

            with col2:
                # Display rating distribution
                distribution = summary.get("distribution", {})
                st.write("Rating Distribution:")
                for score in range(5, 0, -1):
                    count = distribution.get(str(score), 0)
                    st.write(f"{score} ⭐: {count} rating{'s' if count != 1 else ''}")

def main():
    st.title("⭐ Ratings")

    # Load solutions for dropdown
    solutions = load_solutions()
    solution_options = ["All"] + [solution["slug"] for solution in solutions]

    # Filters
    with st.expander("Filters", expanded=True):
        solution_slug = st.selectbox(
            "Solution",
            options=solution_options,
            help="Filter ratings by solution",
            key="filter_solution_slug",
        )

    page_size = 20
    skip = (st.session_state.page - 1) * page_size

    # Load ratings with filters
    ratings, meta = load_ratings(
        solution_slug=solution_slug if solution_slug != "All" else None,
        skip=skip,
        limit=page_size,
    )

    if ratings:
        # Create DataFrame with explicit column order
        df = pd.DataFrame(ratings)[COLUMN_DEFS.keys()]
        df = format_dataframe_dates(df, ["created_at", "updated_at"])

        # Render grid
        grid_response = render_grid(df, COLUMN_DEFS, "rating_grid", page_size)
        selected_rows = grid_response.get("selected_rows", [])

        # Show rating details if a row is selected
        if selected_rows is not None and len(selected_rows) > 0:
            selected_rating = selected_rows.iloc[0].to_dict()
            st.session_state.selected_rating = selected_rating
            render_rating_details(selected_rating)
    else:
        st.info("No ratings found")

if __name__ == "__main__":
    main()
