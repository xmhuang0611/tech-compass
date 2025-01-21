import streamlit as st
from utils.auth import check_auth, login
from utils.api import APIClient

# Page configuration
st.set_page_config(
    page_title="Tech Compass Admin",
    page_icon="🧭",
    layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def load_dashboard_stats():
    """Load dashboard statistics from API"""
    default_stats = {
        "total_solutions": "--",
        "active_users": "--",
        "new_comments": "--"
    }
    
    try:
        # 尝试获取解决方案总数
        solutions = APIClient.get("solutions", {"page": 1, "page_size": 1})
        if solutions and isinstance(solutions, dict):
            total_solutions = solutions.get("meta", {}).get("total", "--")
            default_stats["total_solutions"] = total_solutions
            
        # 尝试获取评论数
        comments = APIClient.get("solutions/comments", {"page": 1, "page_size": 1})
        if comments and isinstance(comments, dict):
            total_comments = comments.get("meta", {}).get("total", "--")
            default_stats["new_comments"] = total_comments
            
    except Exception as e:
        st.error(f"Failed to load some statistics: {str(e)}")
        
    return default_stats

def main():
    if not st.session_state.authenticated:
        login()
        return

    st.title("Tech Compass Admin")
    
    # Welcome message and dashboard overview
    st.markdown("""
    Welcome to the Tech Compass Admin Dashboard. Use the sidebar to navigate between different modules:
    
    - 🔧 **Site Configuration**: Manage website settings and features
    - 💡 **Solutions**: Manage tech solutions catalog
    - 📑 **Categories**: Organize solutions by categories
    - 🏷️ **Tags**: Manage solution tags
    - ⭐ **Ratings**: View and moderate solution ratings
    - 💬 **Comments**: Moderate solution comments
    """)
    
    # Quick stats
    st.subheader("Quick Stats")
    stats = load_dashboard_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Total Solutions",
            value=stats["total_solutions"]
        )
    with col2:
        st.metric(
            label="Active Users",
            value=stats["active_users"]
        )
    with col3:
        st.metric(
            label="New Comments",
            value=stats["new_comments"]
        )
    
    # Recent Activity
    st.subheader("Recent Activity")
    try:
        # 获取最近的解决方案更新
        recent_solutions = APIClient.get("solutions", {
            "page": 1,
            "page_size": 5,
            "sort_by": "updated_at",
            "sort_order": "desc"
        })
        
        if recent_solutions and isinstance(recent_solutions, dict):
            solutions = recent_solutions.get("data", {}).get("solutions", [])
            if solutions:
                for solution in solutions:
                    st.text(f"{solution.get('updated_at', '')} - Updated: {solution.get('name', '')}")
            else:
                st.info("No recent activity")
        else:
            st.info("No recent activity data available")
    except Exception as e:
        st.info(f"Failed to load recent activity: {str(e)}")
    
    # Logout button in sidebar
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

if __name__ == "__main__":
    main() 