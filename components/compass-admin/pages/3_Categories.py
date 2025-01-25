import streamlit as st
from utils.auth import login
from utils.api import APIClient
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Categories - Tech Compass Admin",
    page_icon="📑",
    layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "categories_page" not in st.session_state:
    st.session_state.categories_page = 0
if "categories_per_page" not in st.session_state:
    st.session_state.categories_per_page = 100
if "selected_category" not in st.session_state:
    st.session_state.selected_category = None
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

def load_categories(skip=0, limit=10):
    """Load categories with pagination"""
    try:
        params = {"skip": skip, "limit": limit, "sort": "-updated_at"}
        response = APIClient.get("categories/", params)
        if response and isinstance(response, dict):
            return response.get("items", {}).get("categories", []), {
                "total": response.get("total", 0),
                "skip": response.get("skip", 0),
                "limit": response.get("limit", 10)
            }
    except Exception as e:
        st.error(f"Failed to load categories: {str(e)}")
    return [], {"total": 0, "skip": 0, "limit": 10}

def update_category(category_name, data):
    """Update category"""
    try:
        response = APIClient.put(f"categories/{category_name}", data)
        if response:
            st.session_state.show_success_message = True
            return True
    except Exception as e:
        st.session_state.show_error_message = str(e)
    return False

def delete_category(category_name):
    """Delete category"""
    try:
        response = APIClient.delete(f"categories/{category_name}")
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
def confirm_delete(category_data):
    st.write(f"Are you sure you want to delete category '{category_data.get('name')}'?")
    st.warning("This action cannot be undone!")
    
    if st.button("Yes, Delete", type="primary"):
        if delete_category(category_data["name"]):
            st.session_state.show_delete_success_toast = True
            st.session_state.selected_category = None
            if 'category_grid' in st.session_state:
                del st.session_state['category_grid']
            st.rerun()
        else:
            st.error(f"Failed to delete category: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None

def render_category_form(category_data):
    """Render form for editing category"""
    with st.form("edit_category_form"):
        st.subheader("Edit Category")
        
        # Basic Information
        name = st.text_input(
            "Name*",
            value=category_data.get("name", ""),
            help="Category name",
            disabled=True  # Name cannot be changed as it's the identifier
        )
        
        description = st.text_area(
            "Description",
            value=category_data.get("description", ""),
            help="Category description"
        )
        
        # Save Changes and Delete buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            submitted = st.form_submit_button("Save Changes")
        with col2:
            delete_clicked = st.form_submit_button("Delete Category")
        
        # Show update messages inside form
        if st.session_state.show_success_message:
            st.success("✅ Category updated successfully!")
            st.session_state.show_success_message = False
        
        if st.session_state.show_error_message:
            st.error(f"❌ Failed to update category: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None
        
        if submitted:
            if not name:
                st.error("Category name is required")
                return
                
            update_data = {
                "name": name,
                "description": description if description else None
            }
            
            if update_category(name, update_data):
                st.session_state.selected_category = None
                st.rerun()
    
    # Show delete confirmation dialog when delete button is clicked
    if delete_clicked:
        confirm_delete(category_data)

def render_add_category_form():
    """Render form for adding new category"""
    with st.form("add_category_form"):
        st.subheader("Add New Category")
        
        name = st.text_input(
            "Name*",
            help="Category name"
        )
        
        description = st.text_area(
            "Description",
            help="Category description"
        )
        
        submitted = st.form_submit_button("Add Category")
        
        if st.session_state.show_success_message:
            st.success("✅ Category added successfully!")
            st.session_state.show_success_message = False
        
        if st.session_state.show_error_message:
            st.error(f"❌ Failed to add category: {st.session_state.show_error_message}")
            st.session_state.show_error_message = None
        
        if submitted:
            if not name:
                st.error("Category name is required")
                return
                
            category_data = {
                "name": name,
                "description": description if description else None
            }
            
            try:
                response = APIClient.post("categories/", category_data)
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
    st.title("📑 Categories")
    
    # Show toast message if deletion was successful
    if st.session_state.show_delete_success_toast:
        st.toast("Category deleted successfully!", icon="✅")
        st.session_state.show_delete_success_toast = False
    
    # Create tabs
    list_tab, add_tab = st.tabs(["Categories List", "Add New Category"])
    
    with list_tab:
        # Get page from session state
        if "page" not in st.session_state:
            st.session_state.page = 1
        page_size = 100
        skip = (st.session_state.page - 1) * page_size
            
        categories, meta = load_categories(skip=skip, limit=page_size)
        
        # Convert categories to DataFrame for AgGrid
        if categories:
            # Create DataFrame with explicit column order
            columns = [
                'name', 'description', 'created_at', 'created_by',
                'updated_at', 'updated_by'
            ]
            df = pd.DataFrame(categories)
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
                key='category_grid'
            )
            
            # Handle selection
            selected_rows = grid_response.get('selected_rows', [])
            
            # Show edit form only if we have selected rows and no deletion just happened
            if selected_rows is not None and not st.session_state.show_delete_success_toast:
                selected_category = selected_rows.iloc[0].to_dict()
                st.session_state.selected_category = selected_category
                render_category_form(selected_category)
        else:
            st.info("No categories found")
    
    with add_tab:
        render_add_category_form()

if __name__ == "__main__":
    main() 