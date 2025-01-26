import streamlit as st
from utils.auth import login
from utils.api import APIClient
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Ratings - Tech Compass Admin", page_icon="⭐", layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "selected_rating" not in st.session_state:
    st.session_state.selected_rating = None
if "show_success_message" not in st.session_state:
    st.session_state.show_success_message = False
if "show_error_message" not in st.session_state:
    st.session_state.show_error_message = None
if "show_delete_success_toast" not in st.session_state:
    st.session_state.show_delete_success_toast = False

# Check authentication
if not st.session_state.authenticated:
    login()
    st.stop()


def load_solutions():
    """Load all solutions for dropdown"""
    try:
        params = {"skip": 0, "limit": 100, "sort": "-updated_at"}
        response = APIClient.get("solutions/", params)
        if response and response.get("status_code") == 200:
            return response.get("data", [])
    except Exception as e:
        st.error(f"Failed to load solutions: {str(e)}")
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
            st.error(
                f"Failed to load ratings: {response.get('detail', 'Unknown error occurred')}"
            )
    except Exception as e:
        st.error(f"Failed to load ratings: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 20}


def load_rating_summary(solution_slug):
    """Load rating summary for a solution"""
    try:
        response = APIClient.get(f"ratings/solution/{solution_slug}/summary")
        if response and response.get("status_code") == 200:
            return response.get("data", {})
    except Exception as e:
        st.error(f"Failed to load rating summary: {str(e)}")
    return {}


def render_rating_details(rating_data):
    """Render rating details view"""
    st.subheader("Rating Details")

    # Display rating metadata
    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Solution", value=rating_data.get("solution_slug", ""), disabled=True
        )
        st.text_input("Username", value=rating_data.get("username", ""), disabled=True)
        st.text_input(
            "Created At", value=rating_data.get("created_at", ""), disabled=True
        )
    with col2:
        st.text_input("Rating ID", value=rating_data.get("id", ""), disabled=True)
        st.text_input("Score", value=str(rating_data.get("score", "")), disabled=True)
        st.text_input(
            "Updated At", value=rating_data.get("updated_at", ""), disabled=True
        )

    # Rating content
    st.text_area(
        "Comment",
        value=rating_data.get("comment", ""),
        disabled=True,
        help="Rating comment",
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

    # Get page from session state
    if "page" not in st.session_state:
        st.session_state.page = 1
    page_size = 20
    skip = (st.session_state.page - 1) * page_size

    # Load ratings with filters
    ratings, meta = load_ratings(
        solution_slug=solution_slug if solution_slug != "All" else None,
        skip=skip,
        limit=page_size,
    )

    # Convert ratings to DataFrame for AgGrid
    if ratings:
        # Create DataFrame with explicit column order
        columns = [
            "id",
            "solution_slug",
            "score",
            "comment",
            "username",
            "created_at",
            "updated_at",
        ]
        df = pd.DataFrame(ratings)
        df = df[columns]  # Reorder columns to desired order

        # Format dates
        for date_col in ["created_at", "updated_at"]:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col]).dt.strftime(
                    "%Y-%m-%d %H:%M"
                )

        # Configure grid options
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_selection(
            selection_mode="single", use_checkbox=False, pre_selected_rows=[]
        )
        gb.configure_pagination(
            enabled=True, paginationAutoPageSize=False, paginationPageSize=page_size
        )

        # Configure column properties
        column_defs = {
            "id": {"width": 120, "headerName": "Rating ID"},
            "solution_slug": {"width": 150, "headerName": "Solution"},
            "score": {"width": 100, "headerName": "Score"},
            "comment": {"width": 400, "headerName": "Comment"},
            "username": {"width": 120, "headerName": "Username"},
            "created_at": {"width": 140, "headerName": "Created At"},
            "updated_at": {"width": 140, "headerName": "Updated At"},
        }

        # Apply column configurations
        for col, props in column_defs.items():
            gb.configure_column(field=col, **props)

        gb.configure_grid_options(
            rowStyle={"cursor": "pointer"},
            enableBrowserTooltips=True,
            rowSelection="single",
            suppressRowDeselection=False,
        )

        # Create grid
        grid_response = AgGrid(
            df,
            gridOptions=gb.build(),
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            allow_unsafe_jscode=True,
            theme="streamlit",
            key="rating_grid",
        )

        # Handle selection
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
