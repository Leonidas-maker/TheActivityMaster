import pytest
from .conftest import *
from fastapi import status
from fastapi.testclient import TestClient
import pyotp

from main import app


###########################################################################
################################## Normal #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user():
    """Fixture that registers a user and returns the user data"""
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/user/register",
            json={**pytest.test_user_data, "address": None}
        )
        assert response.status_code == 200

@pytest.mark.dependency(depends=["test_registered_user"])
def test_full_email_flow(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)
        
        # Get user info
        user_response = client.get(
            "/api/v1/user/user/me",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "application-id": pytest.application_id
            }
        )
        assert user_response.status_code == status.HTTP_200_OK
        user_data = user_response.json()
        assert user_data["email"] == pytest.test_user_data["email"]

        # Logout
        logout(client, tokens)        

@pytest.mark.dependency(name="test_totp_flow", depends=["test_registered_user"])
def test_totp_flow(capsys):
    with TestClient(app) as client:
        tokens = login_email(client, capsys)

        # Init TOTP
        init_response = client.post(
            "/api/v1/user/totp_register_init",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "application-id": pytest.application_id
            }
        )
        assert init_response.status_code == status.HTTP_200_OK
        totp_data = init_response.json()
        assert "secret" in totp_data
        assert "uri" in totp_data
        pytest.totp_secret = totp_data["secret"]
        
        # Get TOTP code
        totp = pyotp.TOTP(totp_data["secret"])
        
        # Verify TOTP (using a test code)
        verify_response = client.post(
            f"/api/v1/user/totp_register?_2fa_code={totp.now()}",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "application-id": pytest.application_id
            }
        )
        assert verify_response.status_code == status.HTTP_200_OK
        verify_data = verify_response.json()
        assert verify_data["success"]
        assert len(verify_data["backup_codes"]) == 8

        # Logout
        logout(client, tokens)

@pytest.mark.dependency(depends=["test_registered_user", "test_totp_flow"])
def test_full_totp_flow(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_totp(client)
        
        # Get user info
        user_response = client.get(
            "/api/v1/user/user/me",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "application-id": pytest.application_id
            }
        )
        assert user_response.status_code == status.HTTP_200_OK
        user_data = user_response.json()
        assert user_data["email"] == pytest.test_user_data["email"]

        # Logout
        logout(client, tokens)


###########################################################################
################################# Invalids ################################
###########################################################################
def test_user_registration_invalid_email():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/user/register",
            json={
                "email": "invalid-email",
                "password": "password123",
                "first_name": "Test",
                "last_name": "User"
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_login_missing_header():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": pytest.test_user_data["email"],
                "password": pytest.test_user_data["password"]
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_invalid_credentials():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            headers={"application-id": pytest.application_id},
            json={"email": "wrong@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED