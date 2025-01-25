import requests
from typing import Optional, Dict, Any
import streamlit as st
from .auth import get_auth_header, API_BASE_URL

class APIClient:
    @staticmethod
    def _handle_response(response: requests.Response) -> Dict[str, Any]:
        """Handle API response and show appropriate messages"""
        result = {"status_code": response.status_code}
        
        if response.status_code == 401:
            st.error("Session expired. Please login again.")
            st.session_state.authenticated = False
            st.rerun()
            
        try:
            if response.content:
                result.update(response.json())
            return result
        except Exception as e:
            st.error(f"Error parsing response: {str(e)}")
            return {
                "status_code": response.status_code,
                "status": "error",
                "error": {"message": str(e)}
            }

    @staticmethod
    def get(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request to API"""
        headers = get_auth_header()
        if not headers:
            return {
                "status_code": 401,
                "status": "error",
                "error": {"message": "Not authenticated"}
            }
            
        try:
            response = requests.get(
                f"{API_BASE_URL}/{endpoint.lstrip('/')}",
                headers=headers,
                params=params
            )
            return APIClient._handle_response(response)
        except Exception as e:
            st.error(f"API request failed: {str(e)}")
            return {
                "status_code": 500,
                "status": "error",
                "error": {"message": str(e)}
            }

    @staticmethod
    def post(endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make POST request to API"""
        headers = get_auth_header()
        if not headers:
            return {
                "status_code": 401,
                "status": "error",
                "error": {"message": "Not authenticated"}
            }
            
        try:
            response = requests.post(
                f"{API_BASE_URL}/{endpoint.lstrip('/')}",
                headers=headers,
                json=data
            )
            return APIClient._handle_response(response)
        except Exception as e:
            st.error(f"API request failed: {str(e)}")
            return {
                "status_code": 500,
                "status": "error",
                "error": {"message": str(e)}
            }

    @staticmethod
    def put(endpoint: str, data: Dict) -> Dict[str, Any]:
        """Make PUT request to API"""
        headers = get_auth_header()
        if not headers:
            return {
                "status_code": 401,
                "status": "error",
                "error": {"message": "Not authenticated"}
            }
            
        try:
            response = requests.put(
                f"{API_BASE_URL}/{endpoint.lstrip('/')}",
                headers=headers,
                json=data
            )
            return APIClient._handle_response(response)
        except Exception as e:
            st.error(f"API request failed: {str(e)}")
            return {
                "status_code": 500,
                "status": "error",
                "error": {"message": str(e)}
            }

    @staticmethod
    def delete(endpoint: str) -> Dict[str, Any]:
        """Make DELETE request to API"""
        headers = get_auth_header()
        if not headers:
            return {
                "status_code": 401,
                "status": "error",
                "error": {"message": "Not authenticated"}
            }
            
        try:
            response = requests.delete(
                f"{API_BASE_URL}/{endpoint.lstrip('/')}",
                headers=headers
            )
            return APIClient._handle_response(response)
        except Exception as e:
            st.error(f"API request failed: {str(e)}")
            return {
                "status_code": 500,
                "status": "error",
                "error": {"message": str(e)}
            } 