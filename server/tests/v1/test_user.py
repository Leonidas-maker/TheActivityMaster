import pytest
import pyotp
import time
from fastapi import status

from .conftest import *

from main import app # type: ignore


###########################################################################
################################# Default #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(test_user, capsys):
    test_user.set_capsys(capsys)
    test_user.register_user()
    test_user.login_email()


###########################################################################
################################## Tests ##################################
###########################################################################
@pytest.mark.dependency(depends=["test_registered_user"])
def test_change_password(test_user, capsys):
    test_user.set_capsys(capsys)
    test_user.post(
        "/api/v1/user/me/change_password",
        json={"old_password": test_user.password, "new_password": test_user.password + "1"},
    )

    test_user.password = test_user.password + "1"
    test_user.logout()
    test_user.login_email()


@pytest.mark.dependency(depends=["test_registered_user"])
def test_change_username(test_user):
    new_username = f"new{test_user.username}"
    test_user.put(
        "/api/v1/user/me/username",
        json={"new_username": new_username, "password": test_user.password},
    )

    details = test_user.get_details()
    test_user.username = details["username"]
    assert test_user.username == new_username


@pytest.mark.dependency(depends=["test_registered_user"])
def test_change_email(test_user, capsys):
    test_user.set_capsys(capsys)
    new_email = f"new{test_user.email}"
    response = test_user.put(
        "/api/v1/user/me/email",
        json={"new_email": new_email, "password": test_user.password},
    )

    details = test_user.get_details()
    test_user.email = details["email"]
    assert test_user.email == new_email

    test_user.verify_email()


@pytest.mark.dependency(depends=["test_registered_user"])
def test_change_profile(test_user):
    new_address = {
        "street": "teststreet",
        "postal_code": "testpostal_code",
        "city": "testcity",
        "state": "teststate",
        "country": "Germany",
    }
    test_user.put(
        "/api/v1/user/me",
        json={"address": new_address, "first_name": "NewTest", "last_name": "NewUser"},
    )

    details = test_user.get_details()
    assert details["address"] == new_address
    assert details["first_name"] == "NewTest"
    assert details["last_name"] == "NewUser"


@pytest.mark.dependency(depends=["test_registered_user"])
def test_change_user_newsletter(test_user):
    test_user.put(
        "/api/v1/user/me/newsletter",
        params={"newsletter_subscribe": True},
    )
    details = test_user.get_details()
    assert details["is_newsletter_subscribed"] == True


@pytest.mark.dependency(name="test_totp_flow", depends=["test_registered_user"])
def test_totp_flow(test_user):
    init_response = test_user.post(
        "/api/v1/user/me/totp_register_init",
    )
    totp_data = init_response.json()
    assert "secret" in totp_data
    assert "uri" in totp_data
    test_user.totp_secret = totp_data["secret"]

    # Get TOTP code
    totp = pyotp.TOTP(totp_data["secret"])
    code = totp.now()
    test_user.last_totp_code = code

    # Verify TOTP (using a test code)
    verify_response = test_user.post(
        f"/api/v1/user/me/totp_register?_2fa_code={code}",
    )
    verify_data = verify_response.json()
    assert verify_data["success"]
    assert len(verify_data["backup_codes"]) == 8

    test_user.logout()


@pytest.mark.dependency(depends=["test_registered_user", "test_totp_flow"])
def test_full_totp_flow_remove_totp(test_user):
    test_user.login_totp()

    details = test_user.get_details()
    assert details["email"] == test_user.email

    # Remove TOTP
    totp = pyotp.TOTP(test_user.totp_secret)
    code = totp.now()
    print("\nCode already used, generating new code...", end="")
    while code == test_user.last_totp_code:
        code = totp.now()
        time.sleep(5)
        print(".", end="")
    print()
    test_user.last_totp_code = code

    test_user.post(
        "/api/v1/user/me/totp_remove",
        json={"code": code, "password": test_user.password},
    )


@pytest.mark.dependency(depends=["test_registered_user"])
def test_remove_user(test_user, capsys):
    test_user.set_capsys(capsys)
    test_user.patch(
        "/api/v1/user/me",
        json={"password": test_user.password},
    )

    # Test login
    test_user.tokens = None
    response = test_user.client.post(
        "/api/v1/auth/login",
        headers={"application-id": test_user.application_id},
        json={"ident": test_user.username, "password": test_user.password
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()
