import pytest
from datetime import datetime
import re
from urllib.parse import urlencode
from fastapi.testclient import TestClient

from .testclasses import TestUser, AdminUser

from main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def test_user(client):
    user = TestUser(client)
    yield user
    user.logout()


@pytest.fixture(scope="module")
def admin_user(client):
    user = AdminUser(client)
    yield user
    user.logout()


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


timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")


# ======================================================== #
# ========================= Club ========================= #
# ======================================================== #
pytest.club_data = {
    "name": f"Test Club {timestamp}",
    "description": "Test Description",
    "address": {
        "street": "123 Test St",
        "city": "Test City",
        "state": "TS",
        "postal_code": "12345",
        "country": "Germany",
    },
}
pytest.club_id = None

pytest.club_role_data = {"level": 5, "name": "Test Role", "description": "Test Description", "permissions": []}
