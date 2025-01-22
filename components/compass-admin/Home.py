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
        "total_categories": "--"
    }
    
    try:
        # Get total solutions count
        solutions = APIClient.get("solutions", {"skip": 0, "limit": 10})
        if solutions and isinstance(solutions, dict):
            total_solutions = solutions.get("total", "--")
            default_stats["total_solutions"] = total_solutions
            
        # Get total users count
        users = APIClient.get("users", {"skip": 0, "limit": 10})
        if users and isinstance(users, dict):
            total_users = users.get("total", "--")
            default_stats["active_users"] = total_users
            
        # Get total categories count
        categories = APIClient.get("categories", {"skip": 0, "limit": 10})
        if categories and isinstance(categories, dict):
            total_categories = categories.get("total", "--")
            default_stats["total_categories"] = total_categories
            
    except Exception as e:
        st.error(f"Failed to load some statistics: {str(e)}")
        
    return default_stats

def get_current_user():
    """Get current user information from API"""
    try:
        user_info = APIClient.get("users/me")
        if user_info and isinstance(user_info, dict):
            return user_info.get("full_name", "")
    except Exception as e:
        st.error(f"Failed to load user information: {str(e)}")
    return ""

def main():
    if not st.session_state.authenticated:
        login()
        return

    st.title("Tech Compass Admin")
    
    # Welcome message with user's name
    user_name = get_current_user()
    welcome_msg = f"Welcome to Tech Compass Admin, {user_name}! 👋" if user_name else "Welcome to Tech Compass Admin! 👋"
    st.markdown(welcome_msg)
    
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
            label="Total Categories",
            value=stats["total_categories"]
        )
    
    # Recent Activity
    st.subheader("Recent Activity")
    try:
        # Get 10 most recent solution updates
        recent_solutions = APIClient.get("solutions", {
            "skip": 0,
            "limit": 10,
            "sort": "-updated_at"  # Using - for descending order
        })
        
        if recent_solutions and isinstance(recent_solutions, dict):
            solutions = recent_solutions.get("items", [])
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