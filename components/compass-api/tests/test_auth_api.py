import pytest
import httpx
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.core.config import settings
from app.routers.auth import router as auth_router

# Create test app
app = FastAPI()
app.include_router(auth_router, prefix="/auth")
client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_settings():
    """Fixture to control auth server settings"""
    with patch('app.core.security.settings') as mock_settings:
        # Set default test settings
        mock_settings.JWT_SECRET_KEY = "test_secret_key"
        mock_settings.JWT_ALGORITHM = "HS256"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        yield mock_settings

def test_login_dev_mode(mock_settings):
    """Test login in development mode (AUTH_SERVER_ENABLED=False)"""
    # Configure mock settings for dev mode
    mock_settings.AUTH_SERVER_ENABLED = False
    mock_settings.JWT_SECRET_KEY = "test_secret_key"
    mock_settings.JWT_ALGORITHM = "HS256"
    mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Test credentials (in dev mode, any credentials should work)
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser",
            "password": "testpass"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_auth_server_success(mock_settings):
    """Test successful login with external auth server"""
    # Configure mock settings for auth server mode
    mock_settings.AUTH_SERVER_ENABLED = True
    mock_settings.AUTH_SERVER_URL = "http://auth-server.test"
    mock_settings.JWT_SECRET_KEY = "test_secret_key"
    mock_settings.JWT_ALGORITHM = "HS256"
    mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # Mock successful auth server response
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 200

        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "testpass"
            }
        )

        # Verify auth server was called correctly
        mock_post.assert_called_once_with(
            "http://auth-server.test/verify",
            json={"username": "testuser", "password": "testpass"},
            timeout=5.0
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_auth_server_failure(mock_settings):
    """Test failed login with external auth server"""
    # Configure mock settings for auth server mode
    mock_settings.AUTH_SERVER_ENABLED = True
    mock_settings.AUTH_SERVER_URL = "http://auth-server.test"

    # Mock failed auth server response
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status_code = 401

        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpass"
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Incorrect username or password"

@pytest.mark.asyncio
async def test_login_auth_server_unreachable(mock_settings):
    """Test behavior when auth server is unreachable"""
    # Configure mock settings for auth server mode
    mock_settings.AUTH_SERVER_ENABLED = True
    mock_settings.AUTH_SERVER_URL = "http://auth-server.test"

    # Mock auth server connection error
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.RequestError("Connection failed")

        response = client.post(
            "/auth/login",
            data={
                "username": "testuser",
                "password": "testpass"
            }
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Incorrect username or password"

def test_login_invalid_request():
    """Test login with missing credentials"""
    response = client.post("/auth/login", data={})
    assert response.status_code == 422  # Validation error 