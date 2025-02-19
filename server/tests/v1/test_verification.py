import pytest
import os
import time

from .conftest import *

from config.settings import DEFAULT_TIMEZONE, VERIFICATION_ID_PATH  # type: ignore

import datetime


###########################################################################
################################# Default #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(test_user, admin_user, capsys):
    test_user.set_capsys(capsys)
    admin_user.set_capsys(capsys)
    test_user.register_user()

    test_user.login_email()
    admin_user.login_email()


###########################################################################
################################## Tests ##################################
###########################################################################
@pytest.mark.dependency(depends=["test_registered_user"])
def test_verification_identity(test_user):
    test_user.submit_identity_verification()


@pytest.mark.dependency(depends=["test_verification_identity"])
def test_verification_identity_status(test_user):
    test_user.get(
        "/api/v1/verification/identity/self",
    )


@pytest.mark.dependency(depends=["test_verification_identity"])
def test_verification_identity_view(test_user, admin_user):

    response = admin_user.get(
        "/api/v1/verification/identity/pending",
    )
    
    verification_id = None
    for verification in response.json():
        if verification["user_id"] == test_user.user_id:
            verification_id = verification["id"]
            break
    assert verification_id, "Verification not found"

    response = admin_user.get(
        f"/api/v1/verification/identity/get/{verification_id}",
    )
    assert response.json()["status"] == "pending"
    assert response.json()["id"] == verification_id

    for i in range(3):
        response = admin_user.get(
            f"/api/v1/verification/identity/get/{verification_id}/image",
            params={"index": i},
        )
        assert response.headers["Content-Type"] == "image/png"


@pytest.mark.dependency(depends=["test_verification_identity_view"])
def test_verification_identity_reject(admin_user, test_user):
    test_user.submit_identity_verification(False)

    admin_user.verify_identity(test_user.user_id, approve=False)

    assert os.path.exists(f"{VERIFICATION_ID_PATH}/{test_user.user_id}") is False

    time.sleep(1.5)

    response = test_user.get(
        "/api/v1/verification/identity/self",
    )
    assert response.json()["status"] == "rejected"


@pytest.mark.dependency(depends=["test_verification_identity_reject"])
def test_verification_identity_approve(admin_user, test_user):
    test_user.submit_identity_verification(False)

    admin_user.verify_identity(test_user.user_id)

    assert os.path.exists(f"{VERIFICATION_ID_PATH}/{test_user.user_id}") is False

    time.sleep(1.5)

    response = test_user.get(
        "/api/v1/verification/identity/self",
    )
    assert response.json()["status"] == "approved"


@pytest.mark.dependency(depends=["test_verification_identity_approve"])
def test_verification_identity_delete(test_user):
    test_user.delete(
        "/api/v1/verification/identity/self",
    )

    response = test_user.get(
        "/api/v1/verification/identity/self",
    )
    assert response.json()["status"] == "rejected"

    assert datetime.datetime.strptime(response.json().get("expires_at"), "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=DEFAULT_TIMEZONE
    ) < datetime.datetime.now(DEFAULT_TIMEZONE) + datetime.timedelta(days=30)
