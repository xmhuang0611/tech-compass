import pandas as pd
import streamlit as st
from utils.api import APIClient
from utils.auth import login
from utils.common import (
    initialize_page,
    render_grid,
    show_success_toast,
    show_error_message,
    show_success_message,
    confirm_delete_dialog,
    format_dataframe_dates,
    handle_api_response,
    get_page_size_and_skip,
    COMMON_COLUMN_DEFS,
    REVIEW_STATUS_OPTIONS,
    RECOMMEND_STATUS_OPTIONS,
    STAGE_OPTIONS,
    ADOPTION_LEVEL_OPTIONS,
)

# Initialize session state
initialize_page("Solutions", "💡", {
    "authenticated": False,
    "solutions_page": 0,
    "solutions_per_page": 100,
    "selected_solution": None,
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
    "name": {"width": 150, "headerName": "Name"},
    "description": {"width": 200, "headerName": "Description"},
    "category": {"width": 120, "headerName": "Category"},
    "stage": {"width": 100, "headerName": "Stage"},
    "recommend_status": {"width": 120, "headerName": "Recommend"},
    "adoption_level": {"width": 120, "headerName": "Adoption Level"},
    "adoption_user_count": {"width": 120, "headerName": "User Count"},
    "department": {"width": 120, "headerName": "Department"},
    "team": {"width": 120, "headerName": "Team"},
    "team_email": {"width": 150, "headerName": "Team Email"},
    "maintainer_id": {"width": 120, "headerName": "Maintainer ID"},
    "maintainer_name": {"width": 120, "headerName": "Maintainer Name"},
    "maintainer_email": {"width": 150, "headerName": "Maintainer Email"},
    "version": {"width": 100, "headerName": "Version"},
    "tags": {"width": 150, "headerName": "Tags"},
    "official_website": {"width": 150, "headerName": "Official Website"},
    "documentation_url": {"width": 150, "headerName": "Documentation URL"},
    "demo_url": {"width": 150, "headerName": "Demo URL"},
    "pros": {"width": 200, "headerName": "Pros"},
    "cons": {"width": 200, "headerName": "Cons"},
    **COMMON_COLUMN_DEFS
}

def load_categories():
    """Load all categories"""
    try:
        response = APIClient.get("categories/")
        if response and isinstance(response, dict):
            return response.get("data", [])
    except Exception as e:
        show_error_message(f"Failed to load categories: {str(e)}")
    return []

def load_solutions(skip=0, limit=10, **filters):
    """Load solutions with pagination and filters"""
    try:
        params = {"skip": skip, "limit": limit, "sort": "name", **filters}
        response = APIClient.get("solutions/", params)
        if response and isinstance(response, dict):
            return response.get("data", []), {
                "total": response.get("total", 0),
                "skip": response.get("skip", 0),
                "limit": response.get("limit", 10),
            }
    except Exception as e:
        show_error_message(f"Failed to load solutions: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 10}

def update_solution(solution_slug, data):
    """Update solution"""
    try:
        response = APIClient.put(f"solutions/{solution_slug}", data)
        return handle_api_response(response, "Solution updated successfully")
    except Exception as e:
        show_error_message(str(e))
        return False

def delete_solution(solution_slug):
    """Delete solution"""
    response = APIClient.delete(f"solutions/{solution_slug}")
    if response and response.get("status_code") == 204:
        return
    else:
        return response.get("detail", "Unknown error occurred")

def render_solution_form(solution_data):
    """Render form for editing solution"""
    with st.form("edit_solution_form"):
        st.subheader("Edit Solution")

        # Basic Information
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input(
                "Name", value=solution_data.get("name", ""), help="Solution name"
            )
        with col2:
            categories = load_categories()
            category_names = [""] + [cat["name"] for cat in categories]
            current_category = solution_data.get("category", "")

            # Find the index of the current category
            selected_index = 0
            if current_category:
                try:
                    selected_index = category_names.index(current_category)
                except ValueError:
                    selected_index = 0

            category = st.selectbox(
                "Category",
                options=category_names,
                index=selected_index,
                help="Solution category",
            )
        with col3:
            logo = st.text_input(
                "Logo URL",
                value=solution_data.get("logo", ""),
                help="URL to the solution's logo image"
            )

        # Status Information
        col1, col2, col3 = st.columns(3)
        with col1:
            review_status = st.selectbox(
                "Review Status",
                options=[""] + REVIEW_STATUS_OPTIONS,
                index=(
                    0
                    if not solution_data.get("review_status")
                    else REVIEW_STATUS_OPTIONS.index(
                        solution_data.get("review_status")
                    )
                    + 1
                ),
                help="Select review status",
            )
        with col2:
            stage = st.selectbox(
                "Stage",
                options=[""] + STAGE_OPTIONS,
                index=(
                    0
                    if not solution_data.get("stage")
                    else STAGE_OPTIONS.index(solution_data.get("stage")) + 1
                ),
                help="Select stage",
            )
        with col3:
            recommend_status = st.selectbox(
                "Recommend Status",
                options=[""] + RECOMMEND_STATUS_OPTIONS,
                index=(
                    0
                    if not solution_data.get("recommend_status")
                    else RECOMMEND_STATUS_OPTIONS.index(
                        solution_data.get("recommend_status")
                    )
                    + 1
                ),
                help="Select recommend status",
            )

        # Adoption Information
        col1, col2 = st.columns(2)
        with col1:
            adoption_level = st.selectbox(
                "Adoption Level",
                options=[""] + ADOPTION_LEVEL_OPTIONS,
                index=(
                    0
                    if not solution_data.get("adoption_level")
                    else ADOPTION_LEVEL_OPTIONS.index(solution_data.get("adoption_level")) + 1
                ),
                help="Select adoption level",
            )
        with col2:
            adoption_user_count = st.number_input(
                "Adoption User Count",
                min_value=0,
                value=solution_data.get("adoption_user_count", 0),
                help="Number of users adopting this solution",
            )

        # Team Information
        col1, col2, col3 = st.columns(3)
        with col1:
            department = st.text_input(
                "Department",
                value=solution_data.get("department", ""),
                help="Department name",
            )
        with col2:
            team = st.text_input(
                "Team", value=solution_data.get("team", ""), help="Team name"
            )
        with col3:
            team_email = st.text_input(
                "Team Email",
                value=solution_data.get("team_email", ""),
                help="Team email address",
            )

        # Maintainer Information
        col1, col2, col3 = st.columns(3)
        with col1:
            maintainer_id = st.text_input(
                "Maintainer ID",
                value=solution_data.get("maintainer_id", ""),
                help="Maintainer's ID",
            )
        with col2:
            maintainer_name = st.text_input(
                "Maintainer Name",
                value=solution_data.get("maintainer_name", ""),
                help="Maintainer's name",
            )
        with col3:
            maintainer_email = st.text_input(
                "Maintainer Email",
                value=solution_data.get("maintainer_email", ""),
                help="Maintainer's email",
            )

        # Version and Tags in the same row
        col1, col2 = st.columns(2)
        with col1:
            version = st.text_input(
                "Version",
                value=solution_data.get("version", ""),
                help="Solution version",
            )
        with col2:
            tags = st.text_input(
                "Tags (comma-separated)",
                value=solution_data.get("tags", ""),
                help="Enter tags separated by commas",
            )

        # URLs
        col1, col2, col3 = st.columns(3)
        with col1:
            official_website = st.text_input(
                "Official Website",
                value=solution_data.get("official_website", ""),
                help="Official website URL",
            )
        with col2:
            documentation_url = st.text_input(
                "Documentation URL",
                value=solution_data.get("documentation_url", ""),
                help="Documentation URL",
            )
        with col3:
            demo_url = st.text_input(
                "Demo URL", value=solution_data.get("demo_url", ""), help="Demo/POC URL"
            )

        # Pros & Cons
        col1, col2 = st.columns(2)
        with col1:
            pros = st.text_area(
                "Pros (one per line)",
                value=solution_data.get("pros", ""),
                help="Enter pros (one per line)"
            )
        with col2:
            cons = st.text_area(
                "Cons (one per line)",
                value=solution_data.get("cons", ""),
                help="Enter cons (one per line)"
            )

        # Brief Description after Pros & Cons
        brief = st.text_area(
            "Brief Description",
            value=solution_data.get("brief", ""),
            help="Brief description of the solution"
        )

        # Full Description at the end
        description = st.text_area(
            "Description",
            value=solution_data.get("description", ""),
            help="Detailed solution description",
            placeholder="Markdown supported",
            height=300
        )

        # Save Changes button only in the form
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete Solution")

        # Show update messages inside form
        if st.session_state.show_success_message:
            show_success_message("Solution updated successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to update solution: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

        if submitted:
            update_data = {
                "name": name,
                "brief": brief,
                "description": description,
                "category": category if category else None,
                "stage": stage if stage else None,
                "recommend_status": recommend_status if recommend_status else None,
                "review_status": review_status if review_status else None,
                "adoption_level": adoption_level if adoption_level else None,
                "adoption_user_count": adoption_user_count,
                "department": department,
                "team": team,
                "team_email": team_email if team_email else None,
                "maintainer_name": maintainer_name,
                "maintainer_email": maintainer_email if maintainer_email else None,
                "maintainer_id": maintainer_id if maintainer_id else None,
                "official_website": official_website if official_website else None,
                "documentation_url": documentation_url if documentation_url else None,
                "demo_url": demo_url if demo_url else None,
                "version": version if version else None,
                "logo": logo if logo else None,
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "pros": [pro.strip() for pro in pros.split("\n") if pro.strip()],
                "cons": [con.strip() for con in cons.split("\n") if con.strip()],
            }

            if update_solution(solution_data["slug"], update_data):
                st.session_state.selected_solution = None
                st.rerun()

    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        confirm_delete_dialog("this solution", lambda: delete_solution(solution_data["slug"]), delete_success_callback)

def delete_success_callback():
    show_success_toast("Solution deleted successfully!")
    st.session_state.show_delete_success_toast = True
    st.session_state.selected_solution = None
    if "solution_grid" in st.session_state:
        del st.session_state["solution_grid"]
    st.rerun()

def render_add_solution_form():
    """Render form for adding new solution"""
    with st.form("add_solution_form"):
        st.subheader("Add New Solution")

        # Basic Information
        col1, col2, col3 = st.columns(3)
        with col1:
            name = st.text_input("Name", help="Solution name")
        with col2:
            categories = load_categories()
            category_names = [""] + [cat["name"] for cat in categories]
            category = st.selectbox(
                "Category", options=category_names, help="Solution category"
            )
        with col3:
            logo = st.text_input(
                "Logo URL",
                help="URL to the solution's logo image"
            )

        # Status Information
        col1, col2, col3 = st.columns(3)
        with col1:
            stage = st.selectbox(
                "Stage", options=[""] + STAGE_OPTIONS, help="Select stage"
            )
        with col2:
            recommend_status = st.selectbox(
                "Recommend Status",
                options=[""] + RECOMMEND_STATUS_OPTIONS,
                help="Select recommend status",
            )
        with col3:
            review_status = st.selectbox(
                "Review Status",
                options=[""] + REVIEW_STATUS_OPTIONS,
                help="Select review status",
            )

        # Adoption Information
        col1, col2 = st.columns(2)
        with col1:
            adoption_level = st.selectbox(
                "Adoption Level",
                options=[""] + ADOPTION_LEVEL_OPTIONS,
                help="Select adoption level",
            )
        with col2:
            adoption_user_count = st.number_input(
                "Adoption User Count",
                min_value=0,
                value=1,
                help="Number of users adopting this solution",
            )

        # Team Information
        col1, col2, col3 = st.columns(3)
        with col1:
            department = st.text_input("Department", help="Department name")
        with col2:
            team = st.text_input("Team", help="Team name")
        with col3:
            team_email = st.text_input("Team Email", help="Team email address")

        # Maintainer Information
        col1, col2, col3 = st.columns(3)
        with col1:
            maintainer_id = st.text_input("Maintainer ID", help="Maintainer's ID")
        with col2:
            maintainer_name = st.text_input("Maintainer Name", help="Maintainer's name")
        with col3:
            maintainer_email = st.text_input(
                "Maintainer Email", help="Maintainer's email"
            )

        # Version and Tags in the same row
        col1, col2 = st.columns(2)
        with col1:
            version = st.text_input("Version", help="Solution version")
        with col2:
            tags = st.text_input(
                "Tags (comma-separated)", help="Enter tags separated by commas"
            )

        # URLs
        col1, col2, col3 = st.columns(3)
        with col1:
            official_website = st.text_input(
                "Official Website", help="Official website URL"
            )
        with col2:
            documentation_url = st.text_input(
                "Documentation URL", help="Documentation URL"
            )
        with col3:
            demo_url = st.text_input("Demo URL", help="Demo/POC URL")

        # Pros & Cons
        col1, col2 = st.columns(2)
        with col1:
            pros = st.text_area("Pros (one per line)", help="Enter pros (one per line)")
        with col2:
            cons = st.text_area("Cons (one per line)", help="Enter cons (one per line)")

        # Brief Description after Pros & Cons
        brief = st.text_area(
            "Brief Description",
            help="Brief description of the solution"
        )

        # Full Description at the end
        description = st.text_area(
            "Description",
            help="Detailed solution description",
            placeholder="Markdown supported",
            height=300
        )

        # Add button
        submitted = st.form_submit_button("Add Solution")

        # Show messages right below the button
        if st.session_state.show_success_message:
            show_success_message("Solution added successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to add solution: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

        if submitted:
            solution_data = {
                "name": name,
                "brief": brief,
                "description": description,
                "category": category if category else None,
                "stage": stage if stage else None,
                "recommend_status": recommend_status if recommend_status else None,
                "adoption_level": adoption_level if adoption_level else None,
                "adoption_user_count": adoption_user_count,
                "department": department,
                "team": team,
                "team_email": team_email if team_email else None,
                "maintainer_name": maintainer_name,
                "maintainer_email": maintainer_email if maintainer_email else None,
                "maintainer_id": maintainer_id if maintainer_id else None,
                "official_website": official_website if official_website else None,
                "documentation_url": documentation_url if documentation_url else None,
                "demo_url": demo_url if demo_url else None,
                "version": version if version else None,
                "logo": logo if logo else None,
                "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                "pros": [pro.strip() for pro in pros.split("\n") if pro.strip()],
                "cons": [con.strip() for con in cons.split("\n") if con.strip()],
            }

            try:
                response = APIClient.post("solutions/", solution_data)
                if handle_api_response(response, "Solution added successfully"):
                    st.rerun()
            except Exception as e:
                show_error_message(str(e))
                st.rerun()

def main():
    st.title("💡 Solutions")

    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        show_success_toast("Solution deleted successfully!")
        st.session_state.show_delete_success_toast = False

    # Create tabs
    list_tab, add_tab = st.tabs(["Solutions List", "Add New Solution"])

    with list_tab:
        # Filters
        with st.expander("Filters", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                category = st.selectbox(
                    "Category",
                    options=["All"] + [cat["name"] for cat in load_categories()],
                    key="filter_category",
                )
            with col2:
                review_status = st.selectbox(
                    "Review Status",
                    options=["All"] + REVIEW_STATUS_OPTIONS,
                    key="filter_review_status"
                )
            with col3:
                recommend_status = st.selectbox(
                    "Recommend Status",
                    options=["All"] + RECOMMEND_STATUS_OPTIONS,
                    key="filter_recommend_status"
                )

        # Load solutions with filters
        filters = {}
        if category != "All":
            filters["category"] = category
        if review_status != "All":
            filters["review_status"] = review_status
        if recommend_status != "All":
            filters["recommend_status"] = recommend_status

        page_size, skip = get_page_size_and_skip()
        solutions, meta = load_solutions(skip=skip, limit=page_size, **filters)

        if solutions:
            # Create DataFrame with explicit column order
            df = pd.DataFrame(solutions)[COLUMN_DEFS.keys()]
            df = format_dataframe_dates(df)  # Using default date columns

            # Render grid
            grid_response = render_grid(df, COLUMN_DEFS, "solution_grid", page_size)
            selected_rows = grid_response.get("selected_rows", [])

            # Show edit form only if we have selected rows and no deletion just happened
            if selected_rows is not None and not st.session_state.show_delete_success_toast:
                selected_solution = selected_rows.iloc[0].to_dict()
                st.session_state.selected_solution = selected_solution
                render_solution_form(selected_solution)
        else:
            st.info("No solutions found")

    with add_tab:
        render_add_solution_form()

if __name__ == "__main__":
    main()
