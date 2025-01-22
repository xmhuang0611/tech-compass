import streamlit as st
from utils.auth import login
from utils.api import APIClient

# Page configuration
st.set_page_config(
    page_title="Site Configuration - Tech Compass Admin",
    page_icon="🔧",
    layout="wide"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "config_saved" not in st.session_state:
    st.session_state.config_saved = False

# Check authentication
if not st.session_state.authenticated:
    login()
    st.stop()

def load_site_config():
    """Load current site configuration"""
    try:
        response = APIClient.get("site-config")
        if response and isinstance(response, dict):
            return response.get("data", {})
    except Exception as e:
        st.error(f"Failed to load site configuration: {str(e)}")
    return {}

def save_site_config(config_data):
    """Save site configuration"""
    try:
        response = APIClient.put("site-config", config_data)
        if response:
            st.session_state.config_saved = True
            return True
    except Exception as e:
        st.error(f"Failed to update site configuration: {str(e)}")
    return False

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
    st.title("🔧 Site Configuration")
    
    # Show success message if config was just saved
    if st.session_state.config_saved:
        st.success("Site configuration updated successfully!")
        st.session_state.config_saved = False
    
    # Load current configuration
    current_config = load_site_config()
    
    # Create form for editing
    with st.form("site_config_form"):
        # Basic Information
        st.subheader("Basic Information")
        site_name = st.text_input(
            "Site Name",
            value=current_config.get("site_name", ""),
            help="The name of your site"
        )
        site_description = st.text_area(
            "Site Description",
            value=current_config.get("site_description", ""),
            help="A brief description of your site"
        )
        welcome_message = st.text_area(
            "Welcome Message",
            value=current_config.get("welcome_message", ""),
            help="Welcome message displayed to users"
        )
        contact_email = st.text_input(
            "Contact Email",
            value=current_config.get("contact_email", ""),
            help="Primary contact email address"
        )
        
        # Advanced Settings
        st.subheader("Advanced Settings")
        
        # Features Configuration
        st.write("Features Configuration")
        features = current_config.get("features", {})
        new_features = {}
        
        # Display existing features and allow adding new ones
        for key, value in features.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                new_key = st.text_input("Key", value=key, key=f"feature_key_{key}")
            with col2:
                if isinstance(value, bool):
                    new_value = st.checkbox("Value", value=value, key=f"feature_value_{key}")
                else:
                    new_value = st.text_input("Value", value=str(value), key=f"feature_value_{key}")
            if new_key:
                new_features[new_key] = new_value
        
        # Add new feature
        st.write("Add New Feature")
        col1, col2 = st.columns([1, 2])
        with col1:
            new_feature_key = st.text_input("Key", key="new_feature_key")
        with col2:
            new_feature_value = st.text_input("Value", key="new_feature_value")
        if new_feature_key and new_feature_value:
            # Try to convert string "true"/"false" to boolean
            if new_feature_value.lower() == "true":
                new_feature_value = True
            elif new_feature_value.lower() == "false":
                new_feature_value = False
            new_features[new_feature_key] = new_feature_value
            
        # Theme Settings
        st.write("Theme Settings")
        theme = current_config.get("theme", {})
        new_theme = {}
        
        # Display existing theme settings and allow adding new ones
        for key, value in theme.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                new_key = st.text_input("Key", value=key, key=f"theme_key_{key}")
            with col2:
                new_value = st.text_input("Value", value=str(value), key=f"theme_value_{key}")
            if new_key:
                new_theme[new_key] = new_value
        
        # Add new theme setting
        st.write("Add New Theme Setting")
        col1, col2 = st.columns([1, 2])
        with col1:
            new_theme_key = st.text_input("Key", key="new_theme_key")
        with col2:
            new_theme_value = st.text_input("Value", key="new_theme_value")
        if new_theme_key and new_theme_value:
            new_theme[new_theme_key] = new_theme_value
            
        # Meta Information
        st.write("Meta Information")
        meta = current_config.get("meta", {})
        new_meta = {}
        
        # Display existing meta information and allow adding new ones
        for key, value in meta.items():
            col1, col2 = st.columns([1, 2])
            with col1:
                new_key = st.text_input("Key", value=key, key=f"meta_key_{key}")
            with col2:
                new_value = st.text_input("Value", value=str(value), key=f"meta_value_{key}")
            if new_key:
                new_meta[new_key] = new_value
        
        # Add new meta information
        st.write("Add New Meta Information")
        col1, col2 = st.columns([1, 2])
        with col1:
            new_meta_key = st.text_input("Key", key="new_meta_key")
        with col2:
            new_meta_value = st.text_input("Value", key="new_meta_value")
        if new_meta_key and new_meta_value:
            new_meta[new_meta_key] = new_meta_value
        
        # Submit button
        submitted = st.form_submit_button("Save Changes")
        
        if submitted:
            # Prepare update data
            update_data = {
                "site_name": site_name,
                "site_description": site_description,
                "welcome_message": welcome_message,
                "contact_email": contact_email,
                "features": new_features,
                "custom_links": current_config.get("custom_links", []),
                "theme": new_theme,
                "meta": new_meta
            }
            
            # Save configuration
            if save_site_config(update_data):
                st.rerun()  # Refresh the page to show updated values

if __name__ == "__main__":
    main() 