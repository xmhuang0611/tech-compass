import streamlit as st
from utils.auth import login
from utils.api import APIClient
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Comments - Tech Compass Admin", page_icon="💬", layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "selected_comment" not in st.session_state:
    st.session_state.selected_comment = None
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
        if response and response.get("success"):
            return response.get("data", [])
    except Exception as e:
        st.error(f"Failed to load solutions: {str(e)}")
    return []


def load_comments(solution_slug=None, skip=0, limit=20):
    """Load comments with pagination"""
    try:
        if solution_slug:
            # Load comments for specific solution
            params = {"skip": skip, "limit": limit, "sort": "-created_at"}
            response = APIClient.get(f"comments/solution/{solution_slug}", params)
        else:
            # Load all comments
            params = {"skip": skip, "limit": limit, "sort": "-created_at"}
            response = APIClient.get("comments/", params)

        if response and response.get("status_code") == 200:
            return response.get("data", []), {
                "total": response.get("total", 0),
                "skip": response.get("skip", 0),
                "limit": response.get("limit", 20),
            }
        else:
            st.error(
                f"Failed to load comments: {response.get('detail', 'Unknown error occurred')}"
            )
    except Exception as e:
        st.error(f"Failed to load comments: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 20}


def update_comment(comment_id, data):
    """Update comment"""
    try:
        response = APIClient.put(f"comments/{comment_id}", data)
        if response and response.get("success"):
            st.session_state.show_success_message = True
            return True
    except Exception as e:
        st.session_state.show_error_message = str(e)
    return False


def delete_comment(comment_id):
    """Delete comment"""
    try:
        response = APIClient.delete(f"comments/{comment_id}")
        if response.get("status_code") == 204:
            return True
    except Exception as e:
        st.session_state.show_error_message = str(e)
    return False


@st.dialog("Confirm Deletion")
def confirm_delete(comment_data):
    st.write(f"Are you sure you want to delete this comment?")
    st.warning("This action cannot be undone!")

    if st.button("Yes, Delete", type="primary"):
        if delete_comment(comment_data["id"]):
            st.session_state.show_delete_success_toast = True
            st.session_state.selected_comment = None
            # Clear the grid selection by regenerating the key
            if "comment_grid" in st.session_state:
                del st.session_state["comment_grid"]
            st.rerun()


def render_comment_form(comment_data):
    """Render form for editing comment"""
    with st.form("edit_comment_form"):
        st.subheader("Edit Comment")

        # Display comment metadata
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Solution", value=comment_data.get("solution_slug", ""), disabled=True
            )
            st.text_input(
                "Username", value=comment_data.get("username", ""), disabled=True
            )
            st.text_input(
                "Created At", value=comment_data.get("created_at", ""), disabled=True
            )
        with col2:
            st.text_input("Comment ID", value=comment_data.get("id", ""), disabled=True)
            st.text_input(
                "Updated At", value=comment_data.get("updated_at", ""), disabled=True
            )

        # Comment content
        content = st.text_area(
            "Content", value=comment_data.get("content", ""), help="Comment content"
        )

        # Save Changes and Delete buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete Comment")

        # Show update messages inside form
        if st.session_state.show_success_message:
            st.success("✅ Comment updated successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            st.error(
                f"❌ Failed to update comment: {st.session_state.show_error_message}"
            )
            st.session_state.show_error_message = None

        if submitted:
            update_data = {"content": content}

            if update_comment(comment_data["id"], update_data):
                st.session_state.selected_comment = None
                st.rerun()

    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        confirm_delete(comment_data)


def main():
    st.title("💬 Comments")

    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        st.toast("Comment deleted successfully!", icon="✅")
        st.session_state.show_delete_success_toast = False

    # Load solutions for dropdown
    solutions = load_solutions()
    solution_options = ["All"] + [solution["slug"] for solution in solutions]

    # Filters
    with st.expander("Filters", expanded=True):
        solution_slug = st.selectbox(
            "Solution",
            options=solution_options,
            help="Filter comments by solution",
            key="filter_solution_slug",
        )

    # Get page from session state
    if "page" not in st.session_state:
        st.session_state.page = 1
    page_size = 20
    skip = (st.session_state.page - 1) * page_size

    # Load comments with filters
    comments, meta = load_comments(
        solution_slug=solution_slug if solution_slug != "All" else None,
        skip=skip,
        limit=page_size,
    )

    # Convert comments to DataFrame for AgGrid
    if comments:
        # Create DataFrame with explicit column order
        columns = [
            "id",
            "solution_slug",
            "content",
            "username",
            "created_at",
            "updated_at",
        ]
        df = pd.DataFrame(comments)
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
            "id": {"width": 120, "headerName": "Comment ID"},
            "solution_slug": {"width": 150, "headerName": "Solution"},
            "content": {"width": 400, "headerName": "Content"},
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
            key="comment_grid",
        )

        # Handle selection
        selected_rows = grid_response.get("selected_rows", [])

        # Show edit form only if we have selected rows and no deletion just happened
        if selected_rows is not None and not st.session_state.show_delete_success_toast:
            selected_comment = selected_rows.iloc[0].to_dict()
            st.session_state.selected_comment = selected_comment
            render_comment_form(selected_comment)
    else:
        st.info("No comments found")


if __name__ == "__main__":
    main()
