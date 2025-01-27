import streamlit as st
from utils.auth import login
from utils.api import APIClient
import pandas as pd
from utils.common import (
    initialize_page_state,
    render_grid,
    show_success_toast,
    show_error_message,
    show_success_message,
    confirm_delete_dialog,
    format_dataframe_dates,
)

# Page configuration
st.set_page_config(
    page_title="Tags - Tech Compass Admin",
    page_icon="🏷️",
    layout="wide"
)

# Initialize session state
initialize_page_state({
    "authenticated": False,
    "tags_page": 0,
    "tags_per_page": 100,
    "selected_tag": None,
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
    "description": {"width": 300, "headerName": "Description"},
    "created_at": {"width": 140, "headerName": "Created At"},
    "created_by": {"width": 100, "headerName": "Created By"},
    "updated_at": {"width": 140, "headerName": "Updated At"},
    "updated_by": {"width": 100, "headerName": "Updated By"},
}

def load_tags(skip=0, limit=10):
    """Load tags with pagination"""
    try:
        params = {"skip": skip, "limit": limit}
        response = APIClient.get("tags/", params)
        if response and isinstance(response, dict):
            return response.get("data", []), {
                "total": response.get("total", 0),
                "skip": response.get("skip", 0),
                "limit": response.get("limit", 10),
            }
    except Exception as e:
        show_error_message(f"Failed to load tags: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 10}

def update_tag(tag_name, data):
    """Update tag"""
    try:
        response = APIClient.put(f"tags/{tag_name}", data)
        if response and response.get("status_code") == 200:
            st.session_state.show_success_message = True
            return True
        else:
            st.session_state.show_error_message = response.get("detail", "Unknown error occurred")
            return False
    except Exception as e:
        st.session_state.show_error_message = str(e)
        return False

def delete_tag(tag_name):
    """Delete tag"""
    try:
        response = APIClient.delete(f"tags/{tag_name}")
        if response and response.get("status_code") == 204:
            return True
        else:
            st.session_state.show_error_message = response.get("detail", "Unknown error occurred")
            return False
    except Exception as e:
        st.session_state.show_error_message = str(e)
        return False

def render_tag_form(tag_data):
    """Render form for editing tag"""
    with st.form("edit_tag_form"):
        st.subheader("Edit Tag")

        # Basic Information
        name = st.text_input(
            "Name*",
            value=tag_data.get("name", ""),
            help="Tag name (will be automatically formatted)"
        )
        description = st.text_area(
            "Description",
            value=tag_data.get("description", ""),
            help="Tag description"
        )

        # Save Changes and Delete buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete Tag")

        if submitted:
            if not name:
                show_error_message("Tag name is required")
                return

            update_data = {
                "name": name,
                "description": description if description else None,
            }

            if update_tag(tag_data["name"], update_data):
                st.session_state.selected_tag = None
                st.rerun()

    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        if confirm_delete_dialog(f"tag '{tag_data['name']}'", lambda: delete_tag(tag_data["name"])):
            st.session_state.show_delete_success_toast = True
            st.session_state.selected_tag = None
            if "tag_grid" in st.session_state:
                del st.session_state["tag_grid"]
            st.rerun()

def render_add_tag_form():
    """Render form for adding new tag"""
    with st.form("add_tag_form"):
        st.subheader("Add New Tag")

        name = st.text_input("Name*", help="Tag name (will be automatically formatted)")
        description = st.text_area("Description", help="Tag description")
        submitted = st.form_submit_button("Add Tag")

        if st.session_state.show_success_message:
            show_success_message("Tag added successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to add tag: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

        if submitted:
            if not name:
                show_error_message("Tag name is required")
                return

            tag_data = {
                "name": name,
                "description": description if description else None,
            }

            try:
                response = APIClient.post("tags/", tag_data)
                if response and response.get("status_code") == 201:
                    st.session_state.show_success_message = True
                    st.rerun()
                else:
                    st.session_state.show_error_message = response.get("detail", "Unknown error occurred")
                    st.rerun()
            except Exception as e:
                st.session_state.show_error_message = str(e)
                st.rerun()

def main():
    st.title("🏷️ Tags")

    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        show_success_toast("Tag deleted successfully!")
        st.session_state.show_delete_success_toast = False

    # Create tabs
    list_tab, add_tab = st.tabs(["Tags List", "Add New Tag"])

    with list_tab:
        page_size = 100
        skip = (st.session_state.page - 1) * page_size
        tags, meta = load_tags(skip=skip, limit=page_size)

        if tags:
            # Create DataFrame with explicit column order
            df = pd.DataFrame(tags)[COLUMN_DEFS.keys()]
            df = format_dataframe_dates(df, ["created_at", "updated_at"])

            # Render grid
            grid_response = render_grid(df, COLUMN_DEFS, "tag_grid", page_size)
            selected_rows = grid_response.get("selected_rows", [])

            # Show edit form only if we have selected rows and no deletion just happened
            if selected_rows is not None and not st.session_state.show_delete_success_toast:
                selected_tag = selected_rows.iloc[0].to_dict()
                st.session_state.selected_tag = selected_tag
                render_tag_form(selected_tag)
        else:
            st.info("No tags found")

    with add_tab:
        render_add_tag_form()

if __name__ == "__main__":
    main()
