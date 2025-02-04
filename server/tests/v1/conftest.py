import pytest
from datetime import datetime
from fastapi import status
import uuid
import re
import pyotp
from urllib.parse import urlencode
import time
from pathlib import Path

from pytest_dependency import DependencyManager


###########################################################################
################################# Helpers #################################
###########################################################################
def register_user(client, capsys):
    response = client.post("/api/v1/user/register", json={**pytest.test_user_data, "address": None})
    if response.status_code == 400 and "already exists" in response.json()["detail"]:
        return

    assert response.status_code == 200

    querry = get_verify_token(capsys)

    response = client.post(
        f"/api/v1/verification/verify_email?{querry}",
    )
    assert response.status_code == 200


def get_email_code(capsys):
    captured = capsys.readouterr()

    match = re.search(r"Email code:\s*(\d+)", captured.out)
    assert match, "Bestätigungscode nicht gefunden!"

    code = match.group(1)
    return code


###########################################################################
############################### Verification ##############################
###########################################################################
def get_verify_token(capsys):
    # Capture standard output
    captured = capsys.readouterr()

    # Define the regex pattern to extract user_uuid, expires, and signature
    pattern = r"user_id=([\w-]+)&expires=(\d+)&signature=([\w-]+)"

    # Search for the pattern in captured output
    match = re.search(pattern, captured.out)
    assert match, "Authentication token not found!"

    # Extracted components
    user_id, expires, signature = match.groups()

    return urlencode({"user_id": user_id, "expires": expires, "signature": signature})


def submit_identity_verification(client, tokens, check_status=True):
    image_files_path = Path(__file__).parent / "test_files" / "img" / "identity"

    images = []
    file_handlers = []
    for file in image_files_path.iterdir():
        f = open(file, "rb")
        file_handlers.append(f)
        images.append(("image_files", (file.name, f, "image/png")))

    response = client.post(
        "/api/v1/verification/identity/submit_identity_verification",
        headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens['access_token']}"},
        data={
            "id_card_mrz": "dadhbwahdbahb",
            "first_name": "Test",
            "last_name": "User",
            "date_of_birth": "01.01.2025",
        },
        files=images,  # Pass files using the files parameter
    )

    if check_status:
        assert response.status_code == status.HTTP_200_OK

    # Close all file handles after the request
    for f in file_handlers:
        f.close()


###########################################################################
############################ Standart Auth Flow ###########################
###########################################################################
def login_email(client, capsys) -> dict:
    login_response = client.post(
        "/api/v1/auth/login",
        headers={"application-id": pytest.application_id},
        json={"ident": pytest.test_user_data["email"], "password": pytest.test_user_data["password"]},
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


def login_admin_email(client, capsys) -> dict:
    login_response = client.post(
        "/api/v1/auth/login",
        headers={"application-id": pytest.application_id},
        json={"ident": "admin@localhost", "password": "ADMIN_ADMIN"},
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
        json={"ident": pytest.test_user_data["username"], "password": pytest.test_user_data["password"]},
    )
    assert login_response.status_code == status.HTTP_200_OK
    security_token = login_response.json()["security_token"]

    totp = pyotp.TOTP(pytest.totp_secret)
    code = totp.now()
    print("\nCode already used, generating new code...", end="")
    while code == pytest.last_totp_code:
        code = totp.now()
        time.sleep(5)
        print(".", end="")
    print()

    pytest.last_totp_code = code

    # Verify 2FA- TOTP
    verify_response = client.post(
        "/api/v1/auth/verify-code-2fa",
        headers={"Authorization": f"Bearer {security_token}", "application-id": pytest.application_id},
        json={"code": code, "is_totp": True},
    )
    assert verify_response.status_code == status.HTTP_200_OK
    tokens = verify_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    return tokens


def logout(client, tokens):
    logout_response = client.delete(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
    )
    assert logout_response.status_code == status.HTTP_200_OK


timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")

pytest.test_user_data = {
    "username": f"testuser{timestamp}",
    "email": f"test.user+{timestamp}@example.com",
    "password": "securepassword123",
    "first_name": "Test",
    "last_name": "User",
}
pytest.totp_secret = None
pytest.application_id = uuid.uuid4().hex
pytest.last_totp_code = None
