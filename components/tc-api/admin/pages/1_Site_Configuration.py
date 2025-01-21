import streamlit as st
import json
from utils.api import APIClient

st.set_page_config(
    page_title="Site Configuration - Tech Compass Admin",
    page_icon="⚙️",
    layout="wide"
)

def load_site_config():
    """Load current site configuration"""
    response = APIClient.get("site-config")
    if isinstance(response, dict):
        return response
    return None

def save_site_config(config_data):
    """Save site configuration"""
    response = APIClient.put("site-config", config_data)
    if response and isinstance(response, dict):
        st.success("Site configuration updated successfully!")
        return True
    return False

def reset_site_config():
    """Reset site configuration to defaults"""
    response = APIClient.post("site-config/reset")
    if response and isinstance(response, dict):
        st.success("Site configuration reset to defaults!")
        return True
    return False

def main():
    st.title("Site Configuration")
    
    # Load current configuration
    config = load_site_config()
    if not config:
        st.error("Failed to load site configuration")
        if st.button("Initialize Configuration"):
            # Create initial configuration
            initial_config = {
                "site_name": "Tech Compass",
                "site_description": "Tech Solutions Library",
                "welcome_message": "Welcome to Tech Compass",
                "contact_email": "support@techcompass.com",
                "features": {
                    "enable_comments": True,
                    "enable_ratings": True
                },
                "custom_links": [],
                "theme": {
                    "primary_color": "#1f77b4",
                    "secondary_color": "#ff7f0e"
                },
                "meta": {
                    "title": "Tech Compass",
                    "description": "Find and share tech solutions",
                    "keywords": ["tech", "solutions", "library"]
                }
            }
            response = APIClient.post("site-config", initial_config)
            if response:
                st.success("Configuration initialized!")
                st.rerun()
        return

    with st.form("site_config_form"):
        # Basic Information
        st.subheader("Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            site_name = st.text_input(
                "Site Name", 
                value=config.get("site_name", ""),
                help="Name of the site"
            )
        with col2:
            contact_email = st.text_input(
                "Contact Email",
                value=config.get("contact_email", ""),
                help="Contact email for support"
            )
        
        site_description = st.text_area(
            "Site Description",
            value=config.get("site_description", ""),
            help="Description of the site"
        )
        
        welcome_message = st.text_area(
            "Welcome Message",
            value=config.get("welcome_message", ""),
            help="Welcome message shown on homepage"
        )
        
        # Features
        st.subheader("Features")
        features = config.get("features", {})
        col1, col2 = st.columns(2)
        with col1:
            enable_comments = st.checkbox(
                "Enable Comments",
                value=features.get("enable_comments", True)
            )
        with col2:
            enable_ratings = st.checkbox(
                "Enable Ratings",
                value=features.get("enable_ratings", True)
            )
            
        # Theme Configuration
        st.subheader("Theme")
        theme = config.get("theme", {})
        col1, col2 = st.columns(2)
        with col1:
            primary_color = st.color_picker(
                "Primary Color",
                value=theme.get("primary_color", "#1f77b4")
            )
        with col2:
            secondary_color = st.color_picker(
                "Secondary Color",
                value=theme.get("secondary_color", "#ff7f0e")
            )
            
        # Meta Information
        st.subheader("Meta Information")
        meta = config.get("meta", {})
        meta_title = st.text_input(
            "Meta Title",
            value=meta.get("title", ""),
            help="Page title for SEO"
        )
        meta_description = st.text_area(
            "Meta Description",
            value=meta.get("description", ""),
            help="Page description for SEO"
        )
        meta_keywords = st.text_input(
            "Meta Keywords",
            value=", ".join(meta.get("keywords", [])),
            help="Comma-separated keywords for SEO"
        )
        
        # Custom Links
        st.subheader("Custom Navigation Links")
        custom_links = config.get("custom_links", [])
        num_links = len(custom_links)
        new_links = []
        
        for i in range(max(1, num_links)):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                title = st.text_input(
                    "Link Title",
                    value=custom_links[i].get("title", "") if i < num_links else "",
                    key=f"link_title_{i}"
                )
            with col2:
                url = st.text_input(
                    "URL",
                    value=custom_links[i].get("url", "") if i < num_links else "",
                    key=f"link_url_{i}"
                )
            with col3:
                enabled = st.checkbox(
                    "Enabled",
                    value=custom_links[i].get("enabled", True) if i < num_links else True,
                    key=f"link_enabled_{i}"
                )
            if title and url:
                new_links.append({
                    "title": title,
                    "url": url,
                    "enabled": enabled
                })
        
        # Submit buttons
        col1, col2 = st.columns([1, 4])
        with col1:
            reset = st.form_submit_button("Reset to Defaults")
        submit = st.form_submit_button("Save Configuration")
        
        if reset:
            if reset_site_config():
                st.rerun()
        
        if submit:
            # Prepare configuration data
            config_data = {
                "site_name": site_name,
                "site_description": site_description,
                "welcome_message": welcome_message,
                "contact_email": contact_email,
                "features": {
                    "enable_comments": enable_comments,
                    "enable_ratings": enable_ratings
                },
                "theme": {
                    "primary_color": primary_color,
                    "secondary_color": secondary_color
                },
                "meta": {
                    "title": meta_title,
                    "description": meta_description,
                    "keywords": [k.strip() for k in meta_keywords.split(",") if k.strip()]
                },
                "custom_links": new_links
            }
            
            if save_site_config(config_data):
                st.rerun()

if __name__ == "__main__":
    main() 