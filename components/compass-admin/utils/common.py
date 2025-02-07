import os

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")
ADMIN_TITLE = os.getenv("ADMIN_TITLE", "Tech Compass Admin")

# Common constants
COMMON_DATE_COLUMNS = ["created_at", "updated_at"]
COMMON_COLUMN_DEFS = {
    "created_at": {"width": 140, "headerName": "Created At"},
    "created_by": {"width": 100, "headerName": "Created By"},
    "updated_at": {"width": 140, "headerName": "Updated At"},
    "updated_by": {"width": 100, "headerName": "Updated By"},
}

# Status options
REVIEW_STATUS_OPTIONS = ["PENDING", "APPROVED", "REJECTED"]
RECOMMEND_STATUS_OPTIONS = ["ADOPT", "TRIAL", "ASSESS", "HOLD"]
STAGE_OPTIONS = ["DEVELOPING", "UAT", "PRODUCTION", "DEPRECATED", "RETIRED"]
ADOPTION_LEVEL_OPTIONS = ["PILOT", "TEAM", "DEPARTMENT", "ENTERPRISE", "INDUSTRY"]

def initialize_page(title: str, icon: str, state_vars: dict = None):
    """Initialize page with common settings"""
    # Page configuration
    st.set_page_config(
        page_title=f"{title} - {ADMIN_TITLE}" if title != "Home" else ADMIN_TITLE,
        page_icon=icon,
        layout="wide"
    )

    # Initialize session state
    if state_vars:
        initialize_page_state(state_vars)

    # Check authentication
    if not st.session_state.get("authenticated", False):
        from utils.auth import login
        login()
        st.stop()

def format_datetime(dt_str: str) -> str:
    """Format datetime string to a consistent format"""
    if not dt_str:
        return ""
    try:
        dt = pd.to_datetime(dt_str)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return dt_str

def configure_grid(df: pd.DataFrame, column_defs: dict, page_size: int = 20) -> dict:
    """Configure AgGrid options with common settings"""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_selection(
        selection_mode="single",
        use_checkbox=False,
        pre_selected_rows=[]
    )
    gb.configure_pagination(
        enabled=True,
        paginationAutoPageSize=False,
        paginationPageSize=page_size
    )

    # Apply column configurations
    for col, props in column_defs.items():
        gb.configure_column(field=col, **props)

    gb.configure_grid_options(
        rowStyle={"cursor": "pointer"},
        enableBrowserTooltips=True,
        rowSelection="single",
        suppressRowDeselection=False,
    )

    return gb.build()

def render_grid(df: pd.DataFrame, column_defs: dict, key: str, page_size: int = 20) -> dict:
    """Render an AgGrid with common configuration"""
    grid_options = configure_grid(df, column_defs, page_size)
    return AgGrid(
        df,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        theme="streamlit",
        key=key,
    )

def format_list_to_string(items: list, separator: str = ", ") -> str:
    """Format a list to a string with given separator"""
    if not items:
        return ""
    if not isinstance(items, list):
        return str(items)
    return separator.join(str(item) for item in items)

def initialize_page_state(state_vars: dict):
    """Initialize multiple session state variables"""
    default_state = {
        "authenticated": False,
        "page": 1,
        "show_success_message": False,
        "show_error_message": None,
        "show_delete_success_toast": False,
    }
    # Update with provided state variables
    default_state.update(state_vars)
    
    # Initialize all state variables
    for var, default in default_state.items():
        if var not in st.session_state:
            st.session_state[var] = default

def show_success_toast(message: str):
    """Show a success toast message"""
    st.toast(message, icon="✅")

def show_error_message(error: str):
    """Show an error message"""
    st.error(f"❌ {error}")

def show_success_message(message: str):
    """Show a success message"""
    st.success(f"✅ {message}")

@st.dialog("Confirm Deletion")
def confirm_delete_dialog(item_name: str, delete_callback, success_callback):
    """Generic confirmation dialog for deletion"""
    st.write(f"Are you sure you want to delete {item_name}?")
    st.warning("This action cannot be undone!")
    delete_clicked = st.button("Yes, Delete", type="primary")

    if delete_clicked:
        error = delete_callback()
        if error is not None:
            st.error(f"❌ Failed to delete {item_name}: {error}")
            return False
        success_callback()
        return True
    return False

def format_dataframe_dates(df: pd.DataFrame, date_columns: list = None) -> pd.DataFrame:
    """Format date columns in a DataFrame"""
    if date_columns is None:
        date_columns = COMMON_DATE_COLUMNS
    
    for col in date_columns:
        if col in df.columns:
            df[col] = df[col].apply(format_datetime)
    return df

def handle_api_response(response: dict, success_message: str = None) -> bool:
    """Handle common API response patterns"""
    if not response:
        show_error_message("No response from server")
        return False

    if response.get("status_code") in [200, 201, 204]:
        if success_message:
            st.session_state.show_success_message = True
        return True
    else:
        st.session_state.show_error_message = response.get("detail", "Unknown error occurred")
        return False

def get_page_size_and_skip(page_size: int = 100) -> tuple:
    """Get common pagination parameters"""
    if "page" not in st.session_state:
        st.session_state.page = 1
    skip = (st.session_state.page - 1) * page_size
    return page_size, skip 