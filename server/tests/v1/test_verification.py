import pytest
from fastapi.testclient import TestClient
import os

from .conftest import *

from config.settings import DEFAULT_TIMEZONE, VERIFICATION_ID_PATH
from main import app

import datetime

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
@pytest.mark.dependency(depends=["test_registered_user"])
def test_verification_identity(capsys):
    with TestClient(app) as client:
        tokens = login_email(client, capsys)
        submit_identity_verification(client, tokens, True)
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_verification_identity"])
def test_verification_identity_status(capsys):
    with TestClient(app) as client:
        tokens = login_email(client, capsys)

        response = client.get(
            "/api/v1/verification/identity/self",
            headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        logout(client, tokens)


@pytest.mark.dependency(depends=["test_verification_identity"])
def test_verification_identity_view(capsys):
    with TestClient(app) as client:
        tokens = login_admin_email(client, capsys)

        response = client.get(
            "/api/v1/verification/identity/pending",
            headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK
        verification_id = response.json()[0]["id"]

        response = client.get(
            f"/api/v1/verification/identity/get/{verification_id}",
            headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens['access_token']}"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "pending"
        assert response.json()["id"] == verification_id

        for i in range(3):
            response = client.get(
                f"/api/v1/verification/identity/get/{verification_id}/image",
                params={"index": i},
                headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens['access_token']}"},
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.headers["Content-Type"] == "image/png"

        logout(client, tokens)


@pytest.mark.dependency(depends=["test_verification_identity"])
def test_verification_identity_reject(capsys):
    with TestClient(app) as client:
        tokens_client = login_email(client, capsys)
        submit_identity_verification(client, tokens_client, False)

        tokens_admin = login_admin_email(client, capsys)

        response = client.get(
            "/api/v1/verification/identity/pending",
            headers={
                "application-id": pytest.application_id,
                "Authorization": f"Bearer {tokens_admin['access_token']}",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        verification_id = response.json()[0]["id"]
        user_id = response.json()[0]["user_id"]

        response = client.post(
            f"/api/v1/verification/identity/reject",
            headers={
                "application-id": pytest.application_id,
                "Authorization": f"Bearer {tokens_admin['access_token']}",
            },
            json={"identity_verification_id": verification_id, "reason": "YourMomStinks"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert os.path.exists(f"{VERIFICATION_ID_PATH}/{user_id}") is False

        logout(client, tokens_admin)

        response = client.get(
            "/api/v1/verification/identity/self",
            headers={
                "application-id": pytest.application_id,
                "Authorization": f"Bearer {tokens_client['access_token']}",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "rejected"

        logout(client, tokens_client)


@pytest.mark.dependency(depends=["test_verification_identity"])
def test_verification_identity_approve(capsys):
    with TestClient(app) as client:
        tokens_user = login_email(client, capsys)
        submit_identity_verification(client, tokens_user, False)

        tokens_admin = login_admin_email(client, capsys)

        response = client.get(
            "/api/v1/verification/identity/pending",
            headers={
                "application-id": pytest.application_id,
                "Authorization": f"Bearer {tokens_admin['access_token']}",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        verification_id = response.json()[0]["id"]
        user_id = response.json()[0]["user_id"]

        response = client.post(
            f"/api/v1/verification/identity/approve",
            params={"verification_id": verification_id},
            headers={
                "application-id": pytest.application_id,
                "Authorization": f"Bearer {tokens_admin['access_token']}",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert os.path.exists(f"{VERIFICATION_ID_PATH}/{user_id}") is False

        logout(client, tokens_admin)

        response = client.get(
            "/api/v1/verification/identity/self",
            headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens_user['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "approved"

        logout(client, tokens_user)


@pytest.mark.dependency(depends=["test_verification_identity_approve"])
def test_verification_identity_delete(capsys):
    with TestClient(app) as client:
        tokens = login_email(client, capsys)

        response = client.delete(
            "/api/v1/verification/identity/self",
            headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK

        response = client.get(
            "/api/v1/verification/identity/self",
            headers={"application-id": pytest.application_id, "Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "rejected"

        assert datetime.datetime.strptime(response.json().get("expires_at"), "%Y-%m-%dT%H:%M:%S").replace(
            tzinfo=DEFAULT_TIMEZONE
        ) < datetime.datetime.now(DEFAULT_TIMEZONE) + datetime.timedelta(days=30)

        logout(client, tokens)
