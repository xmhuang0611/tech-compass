import streamlit as st

from utils.api import APIClient
from utils.common import (
    initialize_page,
    format_datetime,
    show_error_message,
)


def load_dashboard_stats():
    """Load dashboard statistics from API"""
    default_stats = {
        "total_solutions": "--",
        "active_users": "--",
        "total_categories": "--",
        "total_tags": "--",
        "total_comments": "--",
        "total_ratings": "--",
    }

    try:
        # Get total solutions count
        solutions = APIClient.get("solutions/", {"skip": 0, "limit": 10})
        if solutions and isinstance(solutions, dict):
            total_solutions = solutions.get("total", "--")
            default_stats["total_solutions"] = total_solutions

        # Get total users count
        users = APIClient.get("users/", {"skip": 0, "limit": 10})
        if users and isinstance(users, dict):
            total_users = users.get("total", "--")
            default_stats["active_users"] = total_users

        # Get total categories count
        categories = APIClient.get("categories/", {"skip": 0, "limit": 10})
        if categories and isinstance(categories, dict):
            total_categories = categories.get("total", "--")
            default_stats["total_categories"] = total_categories

        # Get total tags count
        tags = APIClient.get("tags/", {"skip": 0, "limit": 10})
        if tags and isinstance(tags, dict):
            total_tags = tags.get("total", "--")
            default_stats["total_tags"] = total_tags

        # Get total comments count
        comments = APIClient.get("comments/", {"skip": 0, "limit": 10})
        if comments and isinstance(comments, dict):
            total_comments = comments.get("total", "--")
            default_stats["total_comments"] = total_comments

        # Get total ratings count
        ratings = APIClient.get("ratings/", {"skip": 0, "limit": 10})
        if ratings and isinstance(ratings, dict):
            total_ratings = ratings.get("total", "--")
            default_stats["total_ratings"] = total_ratings

    except Exception as e:
        show_error_message(f"Failed to load some statistics: {str(e)}")

    return default_stats


def get_current_user():
    """Get current user information from API"""
    try:
        user_info = APIClient.get("users/me/")
        if user_info and user_info.get("status_code") == 200:
            return user_info.get("data", {}).get("full_name", "")
    except Exception as e:
        show_error_message(f"Failed to load user information: {str(e)}")
    return ""


def main():
    # Initialize page with common settings
    initialize_page("Home", "🧭", {})

    st.title("Tech Compass Admin")

    # Welcome message with user's name
    user_name = get_current_user()
    welcome_msg = (
        f"Welcome to Tech Compass Admin, {user_name}! 👋"
        if user_name
        else "Welcome to Tech Compass Admin! 👋"
    )
    st.markdown(welcome_msg)

    # Quick stats
    st.subheader("Quick Stats")
    stats = load_dashboard_stats()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Solutions", value=stats["total_solutions"])
    with col2:
        st.metric(label="Active Users", value=stats["active_users"])
    with col3:
        st.metric(label="Total Categories", value=stats["total_categories"])

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label="Total Tags", value=stats["total_tags"])
    with col5:
        st.metric(label="Total Comments", value=stats["total_comments"])
    with col6:
        st.metric(label="Total Ratings", value=stats["total_ratings"])

    # Recent Activity
    st.subheader("Recent Activity")
    try:
        # Get 10 most recent solution updates
        recent_solutions = APIClient.get(
            "solutions/",
            {
                "skip": 0,
                "limit": 10,
                "sort": "-updated_at",  # Using - for descending order
            },
        )

        if recent_solutions and isinstance(recent_solutions, dict):
            solutions = recent_solutions.get("data", [])
            if solutions:
                for solution in solutions:
                    st.text(
                        f"{format_datetime(solution.get('updated_at', ''))} - Updated: {solution.get('name', '')}"
                    )
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
