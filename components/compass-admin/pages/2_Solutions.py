import streamlit as st
from utils.auth import login
from utils.api import APIClient
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

from utils.common import confirm_delete_dialog

# Page configuration
st.set_page_config(
    page_title="Solutions - Tech Compass Admin", page_icon="💡", layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "solutions_page" not in st.session_state:
    st.session_state.solutions_page = 0
if "solutions_per_page" not in st.session_state:
    st.session_state.solutions_per_page = 100
if "selected_solution" not in st.session_state:
    st.session_state.selected_solution = None
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

# Constants
RECOMMEND_STATUS_OPTIONS = ["ADOPT", "TRIAL", "ASSESS", "HOLD"]
STAGE_OPTIONS = ["DEVELOPING", "UAT", "PRODUCTION", "DEPRECATED", "RETIRED"]


def load_categories():
    """Load all categories"""
    try:
        response = APIClient.get("categories/")
        if response and isinstance(response, dict):
            return response.get("data", [])
    except Exception as e:
        st.error(f"Failed to load categories: {str(e)}")
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
        st.error(f"Failed to load solutions: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 10}


def update_solution(solution_slug, data):
    """Update solution"""
    try:
        response = APIClient.put(f"solutions/{solution_slug}", data)
        if response:
            st.session_state.show_success_message = True
            return True
    except Exception as e:
        st.session_state.show_error_message = str(e)
    return False


def delete_solution(solution_slug):
    """Delete solution"""
    # For DELETE requests with 204 response, APIClient.delete returns None
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

        description = st.text_area(
            "Description",
            value=solution_data.get("description", ""),
            help="Solution description",
        )

        # Status Information
        col1, col2, col3 = st.columns(3)
        with col1:
            review_status = st.selectbox(
                "Review Status",
                options=[""] + ["PENDING", "APPROVED", "REJECTED"],
                index=(
                    0
                    if not solution_data.get("review_status")
                    else ["PENDING", "APPROVED", "REJECTED"].index(
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
                help="Enter pros (one per line)",
            )
        with col2:
            cons = st.text_area(
                "Cons (one per line)",
                value=solution_data.get("cons", ""),
                help="Enter cons (one per line)",
            )

        # Save Changes button only in the form
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete Solution")

        # Show update messages inside form
        if st.session_state.show_success_message:
            st.success("✅ Solution updated successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            st.error(
                f"❌ Failed to update solution: {st.session_state.show_error_message}"
            )
            st.session_state.show_error_message = None

        if submitted:
            update_data = {
                "name": name,
                "category": category if category else None,
                "stage": stage if stage else None,
                "recommend_status": recommend_status if recommend_status else None,
                "review_status": review_status if review_status else None,
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
                "description": description,
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
    st.toast("Solution deleted successfully!", icon="✅")
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

        description = st.text_area("Description", help="Solution description")

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

        # Add button
        submitted = st.form_submit_button("Add Solution")

        # Show messages right below the button
        if st.session_state.show_success_message:
            st.success("✅ Solution added successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            st.error(
                f"❌ Failed to add solution: {st.session_state.show_error_message}"
            )
            st.session_state.show_error_message = None

        if submitted:
            solution_data = {
                "name": name,
                "description": description,
                "category": category if category else None,
                "stage": stage if stage else None,
                "recommend_status": recommend_status if recommend_status else None,
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
                if response and response.get("status_code") == 201:
                    st.session_state.show_success_message = True
                    st.rerun()
                else:
                    # Get error message from response
                    error_msg = response.get("detail", "Unknown error occurred")
                    st.session_state.show_error_message = error_msg
                    st.rerun()
            except Exception as e:
                st.session_state.show_error_message = str(e)
                st.rerun()


def main():
    st.title("💡 Solutions")

    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        st.toast("Solution deleted successfully!", icon="✅")
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
                department = st.text_input("Department", key="filter_department")
            with col3:
                stage = st.selectbox(
                    "Stage", options=["All"] + STAGE_OPTIONS, key="filter_stage"
                )

        # Load solutions with filters
        filters = {}
        if category != "All":
            filters["category"] = category
        if department:
            filters["department"] = department
        if stage != "All":
            filters["stage"] = stage

        # Get page from session state
        if "page" not in st.session_state:
            st.session_state.page = 1
        page_size = 100
        skip = (st.session_state.page - 1) * page_size

        solutions, meta = load_solutions(skip=skip, limit=page_size, **filters)

        # Convert solutions to DataFrame for AgGrid
        if solutions:
            # Create DataFrame with explicit column order
            columns = [
                "name",
                "category",
                "review_status",
                "stage",
                "recommend_status",
                "department",
                "team",
                "team_email",
                "maintainer_id",
                "maintainer_name",
                "maintainer_email",
                "version",
                "tags",
                "slug",
                "logo",
                "official_website",
                "documentation_url",
                "demo_url",
                "description",
                "pros",
                "cons",
                "created_at",
                "created_by",
                "updated_at",
                "updated_by",
            ]
            df = pd.DataFrame(solutions)  # Create DataFrame from solutions
            df = df[columns]  # Reorder columns to desired order

            # Format dates
            for date_col in ["created_at", "updated_at"]:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime(
                        "%Y-%m-%d %H:%M"
                    )

            # Format lists to string
            # Format tags with commas, pros and cons with newlines
            if "tags" in df.columns:
                df["tags"] = df["tags"].apply(
                    lambda x: ", ".join(x) if isinstance(x, list) else ""
                )
            for list_col in ["pros", "cons"]:
                if list_col in df.columns:
                    df[list_col] = df[list_col].apply(
                        lambda x: "\n".join(x) if isinstance(x, list) else ""
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
                "slug": {"width": 120, "headerName": "Slug"},
                "name": {"width": 150, "headerName": "Name"},
                "description": {"width": 200, "headerName": "Description"},
                "category": {"width": 120, "headerName": "Category"},
                "stage": {"width": 100, "headerName": "Stage"},
                "recommend_status": {"width": 120, "headerName": "Recommend"},
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
                "created_at": {"width": 140, "headerName": "Created At"},
                "created_by": {"width": 100, "headerName": "Created By"},
                "updated_at": {"width": 140, "headerName": "Updated At"},
                "updated_by": {"width": 100, "headerName": "Updated By"},
            }

            # Apply column configurations
            for col, props in column_defs.items():
                gb.configure_column(field=col, **props)

            gb.configure_grid_options(
                rowStyle={"cursor": "pointer"},
                enableBrowserTooltips=True,
                rowSelection="single",  # Enforce single row selection
                suppressRowDeselection=False,  # Allow deselecting a row
            )

            # Create grid
            grid_response = AgGrid(
                df,
                gridOptions=gb.build(),
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True,
                theme="streamlit",
                key="solution_grid",
            )

            # Handle selection - always use first selected row if any
            selected_rows = grid_response.get("selected_rows", [])

            # Show edit form only if we have selected rows and no deletion just happened
            if (
                selected_rows is not None
                and not st.session_state.show_delete_success_toast
            ):
                selected_solution = selected_rows.iloc[0].to_dict()
                st.session_state.selected_solution = selected_solution
                render_solution_form(selected_solution)
        else:
            st.info("No solutions found")

    with add_tab:
        render_add_solution_form()


if __name__ == "__main__":
    main()
