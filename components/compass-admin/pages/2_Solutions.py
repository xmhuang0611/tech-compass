import streamlit as st
import pandas as pd
from utils.api import APIClient

st.set_page_config(
    page_title="Solutions Management - Tech Compass Admin",
    page_icon="💡",
    layout="wide"
)

# Constants
RADAR_STATUS_OPTIONS = ["ADOPT", "TRIAL", "ASSESS", "HOLD"]
STAGE_OPTIONS = ["DEVELOPING", "UAT", "PRODUCTION", "DEPRECATED", "RETIRED"]
RECOMMEND_STATUS_OPTIONS = ["BUY", "HOLD", "SELL"]

def load_solutions(skip=0, limit=10, **filters):
    """Load solutions with pagination and filters"""
    params = {"skip": skip, "limit": limit, **filters}
    response = APIClient.get("solutions", params)
    
    if isinstance(response, dict):
        # 从 items 字段获取解决方案列表
        solutions = response.get("items", [])
        # 获取分页信息
        meta = {
            "total": response.get("total", 0),
            "skip": response.get("skip", 0),
            "limit": response.get("limit", 10)
        }
        return solutions, meta
    return [], {"total": 0, "skip": 0, "limit": 10}

def load_categories():
    """Load all categories"""
    response = APIClient.get("categories")
    if isinstance(response, dict):
        return response.get("data", {}).get("categories", [])
    return []

def delete_solution(slug):
    """Delete a solution"""
    response = APIClient.delete(f"solutions/{slug}")
    return response is not None

def create_solution(data):
    """Create a new solution"""
    response = APIClient.post("solutions", data)
    if isinstance(response, dict):
        st.success("Solution created successfully!")
        return True
    return False

def update_solution(slug, data):
    """Update an existing solution"""
    response = APIClient.put(f"solutions/{slug}", data)
    if isinstance(response, dict):
        st.success("Solution updated successfully!")
        return True
    return False

def solution_form(existing_data=None):
    """Form for creating/editing a solution"""
    with st.form("solution_form"):
        # Basic Information
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Name*",
                value=existing_data.get("name", "") if existing_data else "",
                help="Solution name"
            )
        with col2:
            category = st.selectbox(
                "Category",
                options=[""] + [cat["name"] for cat in load_categories()],
                index=0 if not existing_data else next(
                    (i for i, cat in enumerate(load_categories()) 
                     if cat["name"] == existing_data.get("category")), 
                    0
                ) + 1
            )
        
        description = st.text_area(
            "Description*",
            value=existing_data.get("description", "") if existing_data else "",
            help="Detailed description"
        )
        
        # Team Information
        st.subheader("Team Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            department = st.text_input(
                "Department*",
                value=existing_data.get("department", "") if existing_data else "",
                help="Department name"
            )
        with col2:
            team = st.text_input(
                "Team*",
                value=existing_data.get("team", "") if existing_data else "",
                help="Team name"
            )
        with col3:
            team_email = st.text_input(
                "Team Email",
                value=existing_data.get("team_email", "") if existing_data else "",
                help="Team contact email"
            )
            
        # Status Information
        st.subheader("Status Information")
        col1, col2, col3 = st.columns(3)
        with col1:
            radar_status = st.selectbox(
                "Radar Status*",
                options=RADAR_STATUS_OPTIONS,
                index=RADAR_STATUS_OPTIONS.index(existing_data.get("radar_status", "ASSESS")) if existing_data else 0,
                help="Tech Radar status"
            )
        with col2:
            stage = st.selectbox(
                "Stage",
                options=[""] + STAGE_OPTIONS,
                index=STAGE_OPTIONS.index(existing_data.get("stage")) + 1 if existing_data and existing_data.get("stage") else 0,
                help="Development stage"
            )
        with col3:
            recommend_status = st.selectbox(
                "Recommend Status",
                options=[""] + RECOMMEND_STATUS_OPTIONS,
                index=RECOMMEND_STATUS_OPTIONS.index(existing_data.get("recommend_status")) + 1 if existing_data and existing_data.get("recommend_status") else 0,
                help="Strategic recommendation"
            )
            
        # URLs
        st.subheader("URLs")
        col1, col2, col3 = st.columns(3)
        with col1:
            official_website = st.text_input(
                "Official Website",
                value=existing_data.get("official_website", "") if existing_data else "",
                help="Official website URL"
            )
        with col2:
            documentation_url = st.text_input(
                "Documentation URL",
                value=existing_data.get("documentation_url", "") if existing_data else "",
                help="Documentation URL"
            )
        with col3:
            demo_url = st.text_input(
                "Demo URL",
                value=existing_data.get("demo_url", "") if existing_data else "",
                help="Demo/POC URL"
            )
            
        # Pros & Cons
        st.subheader("Pros & Cons")
        col1, col2 = st.columns(2)
        with col1:
            pros = st.text_area(
                "Pros",
                value="\n".join(existing_data.get("pros", [])) if existing_data else "",
                help="List advantages (one per line)"
            )
        with col2:
            cons = st.text_area(
                "Cons",
                value="\n".join(existing_data.get("cons", [])) if existing_data else "",
                help="List disadvantages (one per line)"
            )
            
        submitted = st.form_submit_button("Save Solution")
        
        if submitted:
            if not name or not description or not department or not team or not radar_status:
                st.error("Please fill in all required fields (*)")
                return None
                
            data = {
                "name": name,
                "description": description,
                "category": category if category else None,
                "radar_status": radar_status,
                "department": department,
                "team": team,
                "team_email": team_email if team_email else None,
                "official_website": official_website if official_website else None,
                "documentation_url": documentation_url if documentation_url else None,
                "demo_url": demo_url if demo_url else None,
                "stage": stage if stage else None,
                "recommend_status": recommend_status if recommend_status else None,
                "pros": [p.strip() for p in pros.split("\n") if p.strip()] if pros else None,
                "cons": [c.strip() for c in cons.split("\n") if c.strip()] if cons else None
            }
            
            return data
    return None

def main():
    st.title("Solutions Management")
    
    # Tabs for list/create views
    tab1, tab2 = st.tabs(["Solutions List", "Add Solution"])
    
    # Solutions List Tab
    with tab1:
        # Filters
        with st.expander("Filters", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                category = st.selectbox(
                    "Category",
                    options=["All"] + [cat["name"] for cat in load_categories()]
                )
            with col2:
                department = st.text_input("Department")
            with col3:
                stage = st.selectbox(
                    "Stage",
                    options=["All"] + STAGE_OPTIONS
                )
            with col4:
                radar_status = st.selectbox(
                    "Radar Status",
                    options=["All"] + RADAR_STATUS_OPTIONS
                )
        
        # Load solutions with filters
        filters = {}
        if category != "All":
            filters["category"] = category
        if department:
            filters["department"] = department
        if stage != "All":
            filters["stage"] = stage
        if radar_status != "All":
            filters["radar_status"] = radar_status
            
        # 移除原来的分页输入控件
        page_size = 10
        page = 1
        if "page" not in st.session_state:
            st.session_state.page = 1
        skip = (st.session_state.page - 1) * page_size
            
        solutions, meta = load_solutions(skip=skip, limit=page_size, **filters)
        
        if solutions:
            # Convert to DataFrame for better display
            df = pd.DataFrame(solutions)
            
            # Format timestamps
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            df['updated_at'] = pd.to_datetime(df['updated_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            # Join tags list into string
            df['tags'] = df['tags'].apply(lambda x: ', '.join(x) if x else '')
            
            # Display solutions in a table
            st.dataframe(
                df[[
                    "name", "category", "department", "team",
                    "radar_status", "stage", "recommend_status",
                    "version", "tags", "maintainer_name", 
                    "maintainer_email", "created_at", "updated_at",
                    "created_by", "updated_by"
                ]],
                column_config={
                    "name": "Name",
                    "category": "Category",
                    "department": "Department",
                    "team": "Team",
                    "radar_status": "Radar Status",
                    "stage": "Stage",
                    "recommend_status": "Recommend",
                    "version": "Version",
                    "tags": "Tags",
                    "maintainer_name": "Maintainer",
                    "maintainer_email": "Maintainer Email",
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
                    if st.session_state.page > 1:
                        if st.button("⏮️"):
                            st.session_state.page = 1
                            st.rerun()
                with col2:
                    if st.session_state.page > 1:
                        if st.button("◀️"):
                            st.session_state.page -= 1
                            st.rerun()
                with col3:
                    st.write(f"Page {st.session_state.page} of {total_pages}")
                with col4:
                    if st.session_state.page < total_pages:
                        if st.button("▶️"):
                            st.session_state.page += 1
                            st.rerun()
                with col5:
                    if st.session_state.page < total_pages:
                        if st.button("⏭️"):
                            st.session_state.page = total_pages
                            st.rerun()
                with col6:
                    st.write(f"(Total: {meta['total']} items)")
        else:
            st.info("No solutions found")
    
    # Add Solution Tab
    with tab2:
        solution_data = solution_form()
        if solution_data:
            if create_solution(solution_data):
                st.rerun()

if __name__ == "__main__":
    main() 