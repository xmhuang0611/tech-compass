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
)

# Initialize session state
initialize_page("Users", "👥", {
    "authenticated": False,
    "users_page": 0,
    "users_per_page": 100,
    "selected_user": None,
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
    "username": {"width": 120, "headerName": "Username"},
    "email": {"width": 200, "headerName": "Email"},
    "full_name": {"width": 200, "headerName": "Full Name"},
    "is_active": {"width": 100, "headerName": "Active"},
    "is_superuser": {"width": 100, "headerName": "Admin"},
    **COMMON_COLUMN_DEFS
}

def load_users(skip=0, limit=10):
    """Load users with pagination"""
    try:
        params = {"skip": skip, "limit": limit}
        response = APIClient.get("users/", params)
        if response and isinstance(response, dict):
            return response.get("data", []), {
                "total": response.get("total", 0),
                "skip": response.get("skip", 0),
                "limit": response.get("limit", 10),
            }
    except Exception as e:
        show_error_message(f"Failed to load users: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 10}

def update_user(username, data):
    """Update user"""
    try:
        response = APIClient.put(f"users/manage/{username}", data)
        return handle_api_response(response, "User updated successfully")
    except Exception as e:
        show_error_message(str(e))
        return False

def delete_user(username):
    """Delete user"""
    response = APIClient.delete(f"users/manage/{username}")
    if response and response.get("status_code") == 204:
        return
    else:
        return response.get("detail", "Unknown error occurred")

def render_user_form(user_data):
    """Render form for editing user"""
    with st.form("edit_user_form"):
        st.subheader("Edit User")

        # Basic Information
        username = st.text_input(
            "Username*",
            value=user_data.get("username", ""),
            help="Username",
            disabled=True  # Username cannot be changed
        )
        email = st.text_input(
            "Email*",
            value=user_data.get("email", ""),
            help="User email"
        )
        full_name = st.text_input(
            "Full Name",
            value=user_data.get("full_name", ""),
            help="User's full name"
        )
        
        # Status and Role
        col1, col2 = st.columns(2)
        with col1:
            is_active = st.checkbox(
                "Active",
                value=user_data.get("is_active", True),
                help="Whether the user account is active"
            )
        with col2:
            is_superuser = st.checkbox(
                "Admin",
                value=user_data.get("is_superuser", False),
                help="Whether the user has admin privileges"
            )
        
        # Optional password change
        password = st.text_input(
            "New Password",
            type="password",
            help="Leave empty to keep current password",
            value=""
        )

        # Save Changes and Delete buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete User")

        if submitted:
            if not email:
                show_error_message("Email is required")
                return

            update_data = {
                "email": email,
                "username": username,
                "full_name": full_name if full_name else None,
                "is_active": is_active,
                "is_superuser": is_superuser,
            }
            
            if password:
                update_data["password"] = password

            if update_user(username, update_data):
                st.session_state.selected_user = None
                st.rerun()
        
        if st.session_state.show_success_message:
            show_success_message("User updated successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to update user: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        confirm_delete_dialog(f"user '{username}'", lambda: delete_user(username), delete_success_callback)

def delete_success_callback():
    show_success_toast("User deleted successfully!")
    st.session_state.show_delete_success_toast = True
    st.session_state.selected_user = None
    if "user_grid" in st.session_state:
        del st.session_state["user_grid"]
    st.rerun()

def render_add_user_form():
    """Render form for adding new user"""
    with st.form("add_user_form"):
        st.subheader("Add New User")

        username = st.text_input("Username*", help="Username for login")
        email = st.text_input("Email*", help="User email")
        full_name = st.text_input("Full Name", help="User's full name")
        password = st.text_input("Password*", type="password", help="User password")
        
        col1, col2 = st.columns(2)
        with col1:
            is_active = st.checkbox("Active", value=True, help="Whether the user account is active")
        with col2:
            is_superuser = st.checkbox("Admin", value=False, help="Whether the user has admin privileges")

        submitted = st.form_submit_button("Add User")

        if st.session_state.show_success_message:
            show_success_message("User added successfully!")
            st.session_state.show_success_message = False

        if st.session_state.show_error_message:
            show_error_message(f"Failed to add user: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

        if submitted:
            if not all([username, email, password]):
                show_error_message("Username, email and password are required")
                return

            user_data = {
                "username": username,
                "email": email,
                "full_name": full_name if full_name else None,
                "password": password,
                "is_active": is_active,
                "is_superuser": is_superuser,
            }

            try:
                response = APIClient.post("users/", user_data)
                if handle_api_response(response, "User added successfully"):
                    st.rerun()
            except Exception as e:
                show_error_message(str(e))
                st.rerun()

def main():
    st.title("👥 Users")

    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        show_success_toast("User deleted successfully!")
        st.session_state.show_delete_success_toast = False

    # Create tabs
    list_tab, add_tab = st.tabs(["Users List", "Add New User"])

    with list_tab:
        page_size, skip = get_page_size_and_skip()
        users, meta = load_users(skip=skip, limit=page_size)

        if users:
            # Create DataFrame with explicit column order
            df = pd.DataFrame(users)[COLUMN_DEFS.keys()]
            df = format_dataframe_dates(df)  # Using default date columns

            # Render grid
            grid_response = render_grid(df, COLUMN_DEFS, "user_grid", page_size)
            selected_rows = grid_response.get("selected_rows", [])

            # Show edit form only if we have selected rows and no deletion just happened
            if selected_rows is not None and not st.session_state.show_delete_success_toast:
                selected_user = selected_rows.iloc[0].to_dict()
                st.session_state.selected_user = selected_user
                render_user_form(selected_user)
        else:
            st.info("No users found")

    with add_tab:
        render_add_user_form()

if __name__ == "__main__":
    main() 