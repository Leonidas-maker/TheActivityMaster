import pytest
from .conftest import *
from fastapi import status
from fastapi.testclient import TestClient
import pyotp
import time

from main import app


###########################################################################
################################## Normal #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(capsys):
    """Fixture that registers a user and returns the user data"""
    with TestClient(app) as client:
        register_user(client, capsys)


@pytest.mark.dependency(depends=["test_registered_user"])
def test_full_email_flow(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Get user info
        user_response = client.get(
            "/api/v1/user/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert user_response.status_code == status.HTTP_200_OK
        user_data = user_response.json()
        assert user_data["email"] == pytest.test_user_data["email"]

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_registered_user"])
def test_reset_password(capsys):
    with TestClient(app) as client:
        # Get email reset token
        response = client.post(
            f"/api/v1/auth/forgot-password?ident={pytest.test_user_data['username']}",
        )
        assert response.status_code == status.HTTP_200_OK

        querry = get_verify_token(capsys)

        # Reset password
        response = client.post(
            f"/api/v1/auth/reset-password/init?{querry}",
            headers={"application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("security_token") is not None
        security_token = response.json()["security_token"]

        # Change password
        response = client.post(
            "/api/v1/auth/reset-password",
            headers={"Authorization": f"Bearer {security_token}", "application-id": pytest.application_id},
            json={"password": "newpassword"},
        )
        assert response.status_code == status.HTTP_200_OK

        pytest.test_user_data["password"] = "newpassword"

        # Test login with new password
        tokens = login_email(client, capsys)

        # Logout
        logout(client, tokens)


###########################################################################
################################# Invalids ################################
###########################################################################
def test_user_registration_invalid_email():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/user/register",
            json={"email": "invalid-email", "password": "password123", "first_name": "Test", "last_name": "User"},
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_missing_header():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": pytest.test_user_data["email"],
                "email": pytest.test_user_data["email"],
                "password": pytest.test_user_data["password"],
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_invalid_credentials():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            headers={"application-id": pytest.application_id},
            json={"ident": "wrong@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
