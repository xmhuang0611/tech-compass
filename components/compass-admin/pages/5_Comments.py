import streamlit as st
from utils.auth import login
from utils.api import APIClient
import pandas as pd
import os
from utils.common import (
    initialize_page_state,
    render_grid,
    show_success_toast,
    show_error_message,
    show_success_message,
    confirm_delete_dialog,
    format_dataframe_dates,
)

# Environment variables
ADMIN_TITLE = os.getenv("ADMIN_TITLE", "Tech Compass Admin")

# Page configuration
st.set_page_config(
    page_title=f"Comments - {ADMIN_TITLE}",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
initialize_page_state({
    "authenticated": False,
    "selected_comment": None,
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
    "_id": {"width": 120, "headerName": "Comment ID"},
    "solution_slug": {"width": 150, "headerName": "Solution"},
    "content": {"width": 400, "headerName": "Content"},
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
        if response and response.get("success"):
            return response.get("data", [])
    except Exception as e:
        show_error_message(f"Failed to load solutions: {str(e)}")
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
            show_error_message(response.get("detail", "Unknown error occurred"))
    except Exception as e:
        show_error_message(f"Failed to load comments: {str(e)}")
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
    response = APIClient.delete(f"comments/{comment_id}")
    if response and response.get("status_code") == 204:
        return
    else:
        return response.get("detail", "Unknown error occurred")

def render_comment_form(comment_data):
    """Render form for editing comment"""
    with st.form("edit_comment_form"):
        st.subheader("Edit Comment")

        # Display comment metadata
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "Solution",
                value=comment_data.get("solution_slug", ""),
                disabled=True
            )
            st.text_input(
                "Username",
                value=comment_data.get("username", ""),
                disabled=True
            )
            st.text_input(
                "Full Name",
                value=comment_data.get("full_name", ""),
                disabled=True
            )
            st.text_input(
                "Created At",
                value=comment_data.get("created_at", ""),
                disabled=True
            )
        with col2:
            st.text_input(
                "Comment ID",
                value=comment_data.get("_id", ""),
                disabled=True
            )
            st.text_input(
                "Updated At",
                value=comment_data.get("updated_at", ""),
                disabled=True
            )

        # Comment content
        content = st.text_area(
            "Content",
            value=comment_data.get("content", ""),
            help="Comment content"
        )

        # Save Changes and Delete buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete Comment")

        # Show update messages inside form
        if st.session_state.show_success_message:
            show_success_message("Comment updated successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to update comment: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

        if submitted:
            update_data = {"content": content}

            if update_comment(comment_data["_id"], update_data):
                st.session_state.selected_comment = None
                st.rerun()

    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        confirm_delete_dialog("this comment", lambda: delete_comment(comment_data["_id"]), delete_success_callback)

def delete_success_callback():
    st.toast("Comment deleted successfully!", icon="✅")
    st.session_state.show_delete_success_toast = True
    st.session_state.selected_comment = None
    if "comment_grid" in st.session_state:
        del st.session_state["comment_grid"]
    st.rerun()

def main():
    st.title("💬 Comments")

    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        show_success_toast("Comment deleted successfully!")
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

    page_size = 20
    skip = (st.session_state.page - 1) * page_size

    # Load comments with filters
    comments, meta = load_comments(
        solution_slug=solution_slug if solution_slug != "All" else None,
        skip=skip,
        limit=page_size,
    )

    if comments:
        # Create DataFrame with explicit column order
        df = pd.DataFrame(comments)[COLUMN_DEFS.keys()]
        df = format_dataframe_dates(df, ["created_at", "updated_at"])

        # Render grid
        grid_response = render_grid(df, COLUMN_DEFS, "comment_grid", page_size)
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
