import streamlit as st
import requests
from utils.auth import check_auth, login

# Page configuration
st.set_page_config(
    page_title="Tech Compass Admin",
    page_icon="🧭",
    layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def main():
    if not st.session_state.authenticated:
        login()
        return

    st.title("Tech Compass Admin")
    st.sidebar.title("Navigation")
    
    # Main navigation
    page = st.sidebar.selectbox(
        "Select Module",
        [
            "Site Configuration",
            "Solutions",
            "Categories",
            "Tags",
            "Ratings",
            "Comments"
        ]
    )
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()
    
    # Display current page
    if page == "Site Configuration":
        st.header("Site Configuration")
        # Site configuration content will be added here
        
    elif page == "Solutions":
        st.header("Solutions Management")
        # Solutions management content will be added here
        
    elif page == "Categories":
        st.header("Categories Management")
        # Categories management content will be added here
        
    elif page == "Tags":
        st.header("Tags Management")
        # Tags management content will be added here
        
    elif page == "Ratings":
        st.header("Ratings Management")
        # Ratings management content will be added here
        
    elif page == "Comments":
        st.header("Comments Management")
        # Comments management content will be added here

if __name__ == "__main__":
    main() 