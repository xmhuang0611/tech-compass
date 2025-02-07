import os
import streamlit as st
import requests
from typing import Optional

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api")


def login() -> None:
    """Display login form and handle authentication"""

    st.markdown(
        "<h1 style='text-align: center;'>Tech Compass Admin</h1>",
        unsafe_allow_html=True,
    )
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form", clear_on_submit=True):
            st.markdown("### Sign In")
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input(
                "Password", type="password", placeholder="Enter your password"
            )
            submitted = st.form_submit_button("Login", use_container_width=True)

            if submitted and username and password:
                if check_auth(username, password):
                    st.success("Login successful!")
                    st.session_state.authenticated = True
                    st.rerun()


def check_auth(username: str, password: str) -> bool:
    """Verify user credentials against the API and check if user is superuser"""
    try:
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "",
            "username": username,
            "password": password,
            "scope": "",
            "client_id": "",
            "client_secret": "",
        }

        response = requests.post(
            f"{API_BASE_URL}/auth/login", data=data, headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("access_token"):
                # Store the token temporarily
                token = data["access_token"]
                
                # Check if user is superuser
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                }
                user_response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
                
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    if user_data.get("success") and user_data.get("data", {}).get("is_superuser"):
                        st.session_state.token = token
                        return True
                    else:
                        st.error("Access denied. Only superusers can access the admin panel.")
                        return False
                else:
                    st.error("Failed to verify user permissions")
                    return False
            else:
                st.error("Invalid response format from server")
        elif response.status_code == 422:
            st.error("Invalid request format. Please check your input.")
        elif response.status_code == 401:
            st.error("Invalid credentials")
        else:
            st.error("Authentication failed. Please try again.")

        return False
    except Exception as e:
        st.error("Authentication failed. Please try again later.")
        return False


def get_auth_header() -> Optional[dict]:
    """Get the authorization header for API requests"""
    if "token" not in st.session_state:
        return None

    return {
        "Authorization": f"Bearer {st.session_state.token}",
        "Accept": "application/json",
    }
