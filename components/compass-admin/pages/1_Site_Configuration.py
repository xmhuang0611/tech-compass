import streamlit as st
from utils.auth import login
from utils.api import APIClient
import json

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
        if response and isinstance(response, dict) and response.get('status_code') == 200:
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

def is_valid_json(text):
    """Validate if text is a valid JSON object"""
    try:
        json_obj = json.loads(text)
        return isinstance(json_obj, dict)
    except:
        return False

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
        features_json = st.text_area(
            "Features (JSON)",
            value=json.dumps(current_config.get("features", {}), indent=2),
            help="Features configuration in JSON format"
        )
        
        # Theme Settings
        st.write("Theme Settings")
        theme_json = st.text_area(
            "Theme (JSON)",
            value=json.dumps(current_config.get("theme", {}), indent=2),
            help="Theme settings in JSON format"
        )
        
        # Meta Information
        st.write("Meta Information")
        meta_json = st.text_area(
            "Meta (JSON)",
            value=json.dumps(current_config.get("meta", {}), indent=2),
            help="Meta information in JSON format"
        )

        # Custom Links
        st.write("Custom Links")
        custom_links_json = st.text_area(
            "Custom Links (JSON)",
            value=json.dumps(current_config.get("custom_links", []), indent=2),
            help="Custom links configuration in JSON format"
        )
        
        # Submit button
        submitted = st.form_submit_button("Save Changes")
        
        if submitted:
            # Validate JSON inputs
            validation_error = False
            if not is_valid_json(features_json):
                st.error("Features configuration is not a valid JSON object")
                validation_error = True
            if not is_valid_json(theme_json):
                st.error("Theme settings is not a valid JSON object")
                validation_error = True
            if not is_valid_json(meta_json):
                st.error("Meta information is not a valid JSON object")
                validation_error = True
            try:
                custom_links = json.loads(custom_links_json)
                if not isinstance(custom_links, list):
                    st.error("Custom links must be a JSON array")
                    validation_error = True
            except:
                st.error("Custom links is not a valid JSON array")
                validation_error = True
            
            if not validation_error:
                # Prepare update data
                update_data = {
                    "site_name": site_name,
                    "site_description": site_description,
                    "welcome_message": welcome_message,
                    "contact_email": contact_email,
                    "features": json.loads(features_json),
                    "custom_links": json.loads(custom_links_json),
                    "theme": json.loads(theme_json),
                    "meta": json.loads(meta_json)
                }
                
                # Save configuration
                if save_site_config(update_data):
                    st.rerun()  # Refresh the page to show updated values

if __name__ == "__main__":
    main() 