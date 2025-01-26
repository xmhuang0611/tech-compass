import streamlit as st
from utils.auth import login
from utils.api import APIClient
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Tags - Tech Compass Admin",
    page_icon="🏷️",
    layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "tags_page" not in st.session_state:
    st.session_state.tags_page = 0
if "tags_per_page" not in st.session_state:
    st.session_state.tags_per_page = 100
if "selected_tag" not in st.session_state:
    st.session_state.selected_tag = None
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

def load_tags(skip=0, limit=10):
    """Load tags with pagination"""
    try:
        params = {"skip": skip, "limit": limit}
        response = APIClient.get("tags/", params)
        if response and isinstance(response, dict):
            return response.get("data", []), {
                "total": response.get("total", 0),
                "skip": response.get("skip", 0),
                "limit": response.get("limit", 10)
            }
    except Exception as e:
        st.error(f"Failed to load tags: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 10}

def update_tag(tag_name, data):
    """Update tag"""
    try:
        response = APIClient.put(f"tags/{tag_name}", data)
        if response and response.get('status_code') == 200:
            st.session_state.show_success_message = True
            return True
        else:
            error_msg = response.get('detail', 'Unknown error occurred')
            st.session_state.show_error_message = str(error_msg)
            return False
    except Exception as e:
        st.session_state.show_error_message = str(e)
        return False

def delete_tag(tag_name):
    """Delete tag"""
    try:
        response = APIClient.delete(f"tags/{tag_name}")
        if response and response.get('status_code') == 204:
            return True
        else:
            error_msg = response.get('detail', 'Unknown error occurred')
            st.session_state.show_error_message = str(error_msg)
            return False
    except Exception as e:
        st.session_state.show_error_message = str(e)
        return False

@st.dialog("Confirm Deletion")
def confirm_delete(tag_data):
    st.write(f"Are you sure you want to delete tag '{tag_data.get('name')}'?")
    st.warning("This action cannot be undone! This will remove the tag from all solutions using it.")
    
    if st.button("Yes, Delete", type="primary"):
        if delete_tag(tag_data["name"]):
            st.session_state.show_delete_success_toast = True
            st.session_state.selected_tag = None
            if 'tag_grid' in st.session_state:
                del st.session_state['tag_grid']
            st.rerun()
        else:
            st.error(f"Failed to delete tag: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

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
                st.error("Tag name is required")
                return
                
            update_data = {
                "name": name,
                "description": description if description else None
            }
            
            # Use the original name for the API call, but send the new name in the update data
            if update_tag(tag_data["name"], update_data):
                st.success("✅ Tag updated successfully!")
                st.session_state.selected_tag = None
                st.rerun()
            else:
                st.error(f"❌ Failed to update tag: {st.session_state.show_error_message}")
                st.session_state.show_error_message = None
    
    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        confirm_delete(tag_data)

def render_add_tag_form():
    """Render form for adding new tag"""
    with st.form("add_tag_form"):
        st.subheader("Add New Tag")
        
        name = st.text_input(
            "Name*",
            help="Tag name (will be automatically formatted)"
        )
        
        description = st.text_area(
            "Description",
            help="Tag description"
        )
        
        submitted = st.form_submit_button("Add Tag")
        
        if st.session_state.show_success_message:
            st.success("✅ Tag added successfully!")
            st.session_state.show_success_message = False
        
        if st.session_state.show_error_message:
            st.error(f"❌ Failed to add tag: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None
        
        if submitted:
            if not name:
                st.error("Tag name is required")
                return
                
            tag_data = {
                "name": name,
                "description": description if description else None
            }
            
            try:
                response = APIClient.post("tags/", tag_data)
                if response and response.get('status_code') == 201:
                    st.session_state.show_success_message = True
                    st.rerun()
                else:
                    error_msg = response.get('detail', 'Unknown error occurred')
                    st.session_state.show_error_message = str(error_msg)
                    st.rerun()
            except Exception as e:
                st.session_state.show_error_message = str(e)
                st.rerun()

def main():
    st.title("🏷️ Tags")
    
    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        st.toast("Tag deleted successfully!", icon="✅")
        st.session_state.show_delete_success_toast = False
    
    # Create tabs
    list_tab, add_tab = st.tabs(["Tags List", "Add New Tag"])
    
    with list_tab:
        # Get page from session state
        if "page" not in st.session_state:
            st.session_state.page = 1
        page_size = 100
        skip = (st.session_state.page - 1) * page_size
            
        tags, meta = load_tags(skip=skip, limit=page_size)
        
        # Convert tags to DataFrame for AgGrid
        if tags:
            # Create DataFrame with explicit column order
            columns = [
                'name', 'description', 'created_at', 'created_by',
                'updated_at', 'updated_by'
            ]
            df = pd.DataFrame(tags)
            df = df[columns]
            
            # Format dates
            for date_col in ['created_at', 'updated_at']:
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d %H:%M')
            
            # Configure grid options
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_selection(
                selection_mode='single',
                use_checkbox=False,
                pre_selected_rows=[]
            )
            gb.configure_pagination(
                enabled=True,
                paginationAutoPageSize=False,
                paginationPageSize=page_size
            )
            
            # Configure column properties
            column_defs = {
                'name': {'width': 150, 'headerName': 'Name'},
                'description': {'width': 300, 'headerName': 'Description'},
                'created_at': {'width': 140, 'headerName': 'Created At'},
                'created_by': {'width': 100, 'headerName': 'Created By'},
                'updated_at': {'width': 140, 'headerName': 'Updated At'},
                'updated_by': {'width': 100, 'headerName': 'Updated By'}
            }
            
            # Apply column configurations
            for col, props in column_defs.items():
                gb.configure_column(field=col, **props)
            
            gb.configure_grid_options(
                rowStyle={'cursor': 'pointer'},
                enableBrowserTooltips=True,
                rowSelection='single',
                suppressRowDeselection=False
            )
            
            # Create grid
            grid_response = AgGrid(
                df,
                gridOptions=gb.build(),
                update_mode=GridUpdateMode.SELECTION_CHANGED,
                allow_unsafe_jscode=True,
                theme='streamlit',
                key='tag_grid'
            )
            
            # Handle selection
            selected_rows = grid_response.get('selected_rows', [])
            
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