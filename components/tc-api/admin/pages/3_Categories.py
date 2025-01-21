import streamlit as st
import pandas as pd
from utils.api import APIClient

st.set_page_config(
    page_title="Categories Management - Tech Compass Admin",
    page_icon="📑",
    layout="wide"
)

def load_categories(skip=0, limit=10):
    """Load categories with pagination"""
    params = {"skip": skip, "limit": limit}
    response = APIClient.get("categories", params)
    
    if isinstance(response, dict):
        # 从正确的路径获取分类列表
        categories = response.get("items", {}).get("categories", [])
        meta = {
            "total": response.get("total", 0),
            "skip": response.get("skip", 0),
            "limit": response.get("limit", 10)
        }
        return categories, meta
    return [], {"total": 0, "skip": 0, "limit": 10}

def delete_category(category_id):
    """Delete a category"""
    response = APIClient.delete(f"categories/{category_id}")
    return response is not None

def create_category(data):
    """Create a new category"""
    response = APIClient.post("categories", data)
    if isinstance(response, dict):
        st.success("Category created successfully!")
        return True
    return False

def update_category(category_id, data):
    """Update an existing category"""
    response = APIClient.put(f"categories/{category_id}", data)
    if isinstance(response, dict):
        st.success("Category updated successfully!")
        return True
    return False

def category_form(existing_data=None):
    """Form for creating/editing a category"""
    with st.form("category_form"):
        name = st.text_input(
            "Name*",
            value=existing_data.get("name", "") if existing_data else "",
            help="Category name"
        )
        
        description = st.text_area(
            "Description",
            value=existing_data.get("description", "") if existing_data else "",
            help="Category description"
        )
        
        submitted = st.form_submit_button("Save Category")
        
        if submitted:
            if not name:
                st.error("Please fill in the category name")
                return None
                
            data = {
                "name": name,
                "description": description if description else None
            }
            
            return data
    return None

def main():
    st.title("Categories Management")
    
    # Tabs for list/create views
    tab1, tab2 = st.tabs(["Categories List", "Add Category"])
    
    # Categories List Tab
    with tab1:
        # 分页设置
        page_size = 10
        if "category_page" not in st.session_state:
            st.session_state.category_page = 1
        skip = (st.session_state.category_page - 1) * page_size
            
        categories, meta = load_categories(skip=skip, limit=page_size)
        
        if categories:
            # Convert to DataFrame for better display
            df = pd.DataFrame(categories)
            
            # Debug: print the actual columns
            st.write("Debug - Available columns:", df.columns.tolist())
            
            # Format timestamps if they exist
            timestamp_fields = ['created_at', 'updated_at']
            for field in timestamp_fields:
                if field in df.columns:
                    df[field] = pd.to_datetime(df[field]).dt.strftime('%Y-%m-%d %H:%M')
            
            # Get available columns for display
            display_columns = ["name", "description", "_id", "created_at", "updated_at", "created_by", "updated_by"]
            
            # Display categories in a table
            st.dataframe(
                df[display_columns],
                column_config={
                    "name": "Name",
                    "description": "Description",
                    "_id": "ID",
                    "created_at": "Created At",
                    "updated_at": "Updated At",
                    "created_by": "Created By",
                    "updated_by": "Updated By"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # 添加分页控件到右下方
            total_pages = (meta["total"] - 1) // page_size + 1
            
            # 使用列布局来对齐分页控件
            _, right_col = st.columns([2, 1])
            with right_col:
                col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 2, 1, 1, 2])
                with col1:
                    if st.session_state.category_page > 1:
                        if st.button("⏮️", key="cat_first"):
                            st.session_state.category_page = 1
                            st.rerun()
                with col2:
                    if st.session_state.category_page > 1:
                        if st.button("◀️", key="cat_prev"):
                            st.session_state.category_page -= 1
                            st.rerun()
                with col3:
                    st.write(f"Page {st.session_state.category_page} of {total_pages}")
                with col4:
                    if st.session_state.category_page < total_pages:
                        if st.button("▶️", key="cat_next"):
                            st.session_state.category_page += 1
                            st.rerun()
                with col5:
                    if st.session_state.category_page < total_pages:
                        if st.button("⏭️", key="cat_last"):
                            st.session_state.category_page = total_pages
                            st.rerun()
                with col6:
                    st.write(f"(Total: {meta['total']} items)")
        else:
            st.info("No categories found")
    
    # Add Category Tab
    with tab2:
        category_data = category_form()
        if category_data:
            if create_category(category_data):
                st.rerun()

if __name__ == "__main__":
    main() 