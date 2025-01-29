import pytest
from datetime import datetime
from fastapi import status
import uuid
import re
import pyotp

###########################################################################
################################# Helpers #################################
###########################################################################
def get_email_code(capsys):
    # Standard-IO abfangen
    captured = capsys.readouterr()

    # Code mit Regex extrahieren (Beispiel: "Email code: 850626")
    match = re.search(r"Email code:\s*(\d+)", captured.out)
    assert match, "Bestätigungscode nicht gefunden!"

    code = match.group(1)  # Den gefundenen Code speichern
    return code

###########################################################################
############################ Standart Auth Flow ###########################
###########################################################################
def login_email(client, capsys) -> dict:
    login_response = client.post(
        "/api/v1/auth/login",
        headers={"application-id": pytest.application_id},
        json={"email": pytest.test_user_data["email"], "password": pytest.test_user_data["password"]},
    )
    assert login_response.status_code == status.HTTP_200_OK
    security_token = login_response.json()["security_token"]

    code = get_email_code(capsys)

    # Verify 2FA- Email
    verify_response = client.post(
        "/api/v1/auth/verify-code-2fa",
        headers={"Authorization": f"Bearer {security_token}", "application-id": pytest.application_id},
        json={"code": code, "is_totp": False},
    )
    assert verify_response.status_code == status.HTTP_200_OK
    tokens = verify_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    return tokens


def login_totp(client) -> dict:
    login_response = client.post(
        "/api/v1/auth/login",
        headers={"application-id": pytest.application_id},
        json={"email": pytest.test_user_data["email"], "password": pytest.test_user_data["password"]},
    )
    assert login_response.status_code == status.HTTP_200_OK
    security_token = login_response.json()["security_token"]

    totp = pyotp.TOTP(pytest.totp_secret)
    # Verify 2FA- TOTP
    verify_response = client.post(
        "/api/v1/auth/verify-code-2fa",
        headers={"Authorization": f"Bearer {security_token}", "application-id": pytest.application_id},
        json={"code": totp.now(), "is_totp": True},
    )
    assert verify_response.status_code == status.HTTP_200_OK
    tokens = verify_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    return tokens

def logout(client, tokens):
    logout_response = client.delete(
            "/api/v1/auth/logout",
            headers={
                "Authorization": f"Bearer {tokens['access_token']}",
                "application-id": pytest.application_id
            }
        )
    assert logout_response.status_code == status.HTTP_200_OK

timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")

pytest.test_user_data = {
    "email": f"test.user+{timestamp}@example.com",
    "password": "securepassword123",
    "first_name": "Test",
    "last_name": "User",
}
pytest.totp_secret = None
pytest.application_id = uuid.uuid4().hex
