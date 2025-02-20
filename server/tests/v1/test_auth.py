import pytest
from .conftest import *
from fastapi import status

###########################################################################
################################## Normal #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(test_user, capsys):
    """Fixture that registers a user and returns the user data"""
    test_user.set_capsys(capsys)
    test_user.register_user()


@pytest.mark.dependency(depends=["test_registered_user"])
def test_full_email_flow(test_user, capsys):
    test_user.set_capsys(capsys)
    test_user.login_email()


@pytest.mark.dependency(depends=["test_registered_user"])
def test_reset_password(client, test_user, capsys):
    test_user.set_capsys(capsys)

    # Get email reset token
    response = client.post(
        f"/api/v1/auth/forgot-password?ident={test_user.username}",
        headers={"application-id": test_user.application_id},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    security_token = get_security_token(test_user.capsys)

    # Change password
    response = client.post(
        "/api/v1/auth/reset-password",
        headers={"Authorization": f"Bearer {security_token}", "application-id": test_user.application_id},
        json={"password": "newpassword"},
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    test_user.logout()
    test_user.password = "newpassword"
    test_user.login_email()


###########################################################################
################################# Invalids ################################
###########################################################################
def test_user_registration_invalid_email(client):
    response = client.post(
        "/api/v1/user/register",
        json={"email": "invalid-email", "password": "password123", "first_name": "Test", "last_name": "User"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_missing_header(client, test_user): 
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": test_user.username,
            "email": test_user.email,
            "password": test_user.password,
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_invalid_credentials(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        headers={"application-id": test_user.application_id},
        json={"ident": "wrong@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
