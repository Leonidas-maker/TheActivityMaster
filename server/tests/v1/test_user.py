import pytest
from fastapi.testclient import TestClient

from .conftest import *

from main import app


###########################################################################
################################# Default #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(capsys):
    """Fixture that registers a user and returns the user data"""
    with TestClient(app) as client:
        register_user(client, capsys)


###########################################################################
################################## Tests ##################################
###########################################################################
@pytest.mark.dependency(name="test_totp_flow", depends=["test_registered_user"])
def test_change_password(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Change password
        response = client.post(
            "/api/v1/user/me/change_password",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json={"old_password": pytest.test_user_data["password"], "new_password": "NewPassword123"},
        )
        assert response.status_code == status.HTTP_200_OK

        pytest.test_user_data["password"] = "NewPassword123"

        # Logout
        logout(client, tokens)

        # Test login with new password
        tokens = login_email(client, capsys)
        logout(client, tokens)


@pytest.mark.dependency(name="test_totp_flow", depends=["test_registered_user"])
def test_change_address(capsys):
    new_address = {
        "street": "teststreet",
        "postal_code": "testpostal_code",
        "city": "testcity",
        "state": "teststate",
        "country": "Germany",
    }

    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Change address
        response = client.put(
            "/api/v1/user/me/address",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json=new_address,
        )
        assert response.status_code == status.HTTP_200_OK

        # Get user info
        user_response = client.get(
            "/api/v1/user/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert user_response.status_code == status.HTTP_200_OK
        user_data = user_response.json()
        assert user_data["address"] == new_address

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(name="test_totp_flow", depends=["test_registered_user"])
def test_totp_flow(capsys):
    with TestClient(app) as client:
        tokens = login_email(client, capsys)

        # Init TOTP
        init_response = client.post(
            "/api/v1/user/me/totp_register_init",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert init_response.status_code == status.HTTP_200_OK
        totp_data = init_response.json()
        assert "secret" in totp_data
        assert "uri" in totp_data
        pytest.totp_secret = totp_data["secret"]

        # Get TOTP code
        totp = pyotp.TOTP(totp_data["secret"])
        code = totp.now()
        pytest.last_totp_code = code

        # Verify TOTP (using a test code)
        verify_response = client.post(
            f"/api/v1/user/me/totp_register?_2fa_code={code}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert verify_response.status_code == status.HTTP_200_OK
        verify_data = verify_response.json()
        assert verify_data["success"]
        assert len(verify_data["backup_codes"]) == 8

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_registered_user", "test_totp_flow"])
def test_full_totp_flow_remove_totp():
    with TestClient(app) as client:
        # Login
        tokens = login_totp(client)

        # Get user info
        user_response = client.get(
            "/api/v1/user/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert user_response.status_code == status.HTTP_200_OK
        user_data = user_response.json()
        assert user_data["email"] == pytest.test_user_data["email"]

        # Remove TOTP
        totp = pyotp.TOTP(pytest.totp_secret)
        code = totp.now()
        print("\nCode already used, generating new code...", end="")
        while code == pytest.last_totp_code:
            code = totp.now()
            time.sleep(5)
            print(".", end="")
        print()
        pytest.last_totp_code = code

        # Remove TOTP
        response = client.post(
            "/api/v1/user/me/totp_remove",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json={"code": code, "password": pytest.test_user_data["password"]},
        )
        assert response.status_code == status.HTTP_200_OK

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_registered_user"])
def test_remove_user(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Remove user
        response = client.patch(
            "/api/v1/user/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json={"password": pytest.test_user_data["password"]},
        )
        assert response.status_code == status.HTTP_200_OK

        # Test login
        with pytest.raises(AssertionError) as e:
            login_email(client, capsys)

        assert "401 Unauthorized" in str(e.value)
