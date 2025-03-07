import pytest
from datetime import datetime
import re
from urllib.parse import urlencode
from fastapi.testclient import TestClient
import random   
import os

from .testclasses import TestUser, AdminUser, Club



def pytest_sessionstart(session):
    os.environ["TESTING"] = "True"


@pytest.fixture(scope="module")
def client():
    from main import app # type: ignore
    with TestClient(app) as c:
        yield c


# Create a test user
@pytest.fixture(scope="module")
def test_user(client):
    user = TestUser(client)
    yield user
    user.logout()

# Create two test users
@pytest.fixture(scope="module")
def test_users(client):
    user1 = TestUser(client)
    user2 = TestUser(client)
    yield [user1, user2]
    user1.logout()
    user2.logout()

# Login as an admin user
@pytest.fixture(scope="module")
def admin_user(client):
    user = AdminUser(client)
    yield user
    user.logout()

# Create a club
@pytest.fixture(scope="module")
def test_club(test_user):
    club = Club(test_user)
    yield club

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

def get_security_token(capsys):
    # Capture standard output
    captured = capsys.readouterr()

    # Define the regex pattern to extract security_token
    pattern = r"security_token=([\w\.-]+)"

    # Search for the pattern in captured output
    match = re.search(pattern, captured.out)
    assert match, "Authentication token not found!"

    # Extracted components
    security_token = match.groups()[0]

    return security_token

def get_random_role(club: Club):
    role = random.choice(club.roles)
    while role.level == 0:
        role = random.choice(club.roles)
    return role

