# type: ignore
# import pytest
from fastapi.testclient import TestClient
import random

from .conftest import *

from main import app
from config.permissions import DEFAULT_CLUB_ROLES


###########################################################################
################################# Default #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(capsys):
    """Fixture that registers a user and returns the user data"""
    with TestClient(app) as client:
        register_user(client, capsys)

        tokens = login_email(client, capsys)
        submit_identity_verification(client, tokens, False)
        verify_identity(client, capsys)
        check_identity_verification_status(client, tokens)
        logout(client, tokens)


###########################################################################
############################### Tests - Club ##############################
###########################################################################
@pytest.mark.dependency(depends=["test_registered_user"])
def test_create_club(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Create club
        response = client.post(
            "/api/v1/clubs",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json=pytest.club_data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == pytest.club_data["name"], "Club not created"
        pytest.club_id = response.json()["id"]

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_registered_user", "test_create_club"])
def test_get_clubs(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Get clubs
        response = client.get(
            "/api/v1/clubs",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            params={"page": 1, "page_size": 50},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0, "No clubs found"

        club_found = False
        for club in response.json():
            if club["name"] == pytest.club_data["name"]:
                club_found = True
                break
        assert club_found, "Club not found"

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_create_club"])
def test_search_clubs(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Search clubs
        response = client.get(
            "/api/v1/clubs/search",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            params={"query": pytest.club_data["name"]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0, "No clubs found"

        club_found = False
        for club in response.json():
            if club["name"] == pytest.club_data["name"]:
                club_found = True
                break
        assert club_found, "Club not found"

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_create_club"])
def test_get_club(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Get club
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == pytest.club_data["name"], "Expected club not found"

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_create_club"])
def test_update_club(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Update club
        response = client.put(
            f"/api/v1/clubs/{pytest.club_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json={"name": "Updated" + pytest.club_data["name"]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == "Updated" + pytest.club_data["name"], "Club not updated"
        pytest.club_data["name"] = response.json()["name"]

        # Logout
        logout(client, tokens)


###########################################################################
############################ Tests - Club Roles ###########################
###########################################################################
@pytest.mark.dependency()
def test_get_available_club_permissions(capsys):
    with TestClient(app) as client:
        # Get available club permissions
        response = client.get("/api/v1/clubs/permissions")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0, "No club permissions found"

        pytest.club_role_permissions = [permission["name"] for permission in response.json()]
        pytest.club_role_data["permissions"] = random.sample(pytest.club_role_permissions, 3)


@pytest.mark.dependency(depends=["test_get_club"])
def test_check_default_club_roles(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Get club roles
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/roles/all",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) > 0, "No club roles found"

        correct_roles = 0

        for role in response.json():
            if not role["name"] in DEFAULT_CLUB_ROLES.keys():
                assert False, "Unexpected club role found"
            else:
                correct_roles += 1

        assert correct_roles == len(DEFAULT_CLUB_ROLES.keys()), "Not all roles found"

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_get_club", "test_get_available_club_permissions"])
def test_create_club_role(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Create club role
        response = client.post(
            f"/api/v1/clubs/{pytest.club_id}/roles",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json=pytest.club_role_data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == pytest.club_role_data["name"], "Club role not created"

        # Check if role was created
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/roles/{response.json()['id']}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == pytest.club_role_data["name"], "Expected role not found"
        assert response.json()["level"] == pytest.club_role_data["level"], "Expected role level not found"
        assert response.json()["description"] == pytest.club_role_data["description"]
        assert all(
            permission["name"] in pytest.club_role_data["permissions"] for permission in response.json()["permissions"]
        ), "Expected permissions not found"
        
        pytest.club_role_id = response.json()["id"]
       
        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_update_club_role(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        new_permissions = random.sample(pytest.club_role_permissions, 2)

        new_role_data = {
            "level": 6,
            "name": "Updated" + pytest.club_role_data["name"],
            "description": "Updated Test Role Description",
            "permissions": new_permissions,
        }

        # Update club role
        response = client.put(
            f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json=new_role_data,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["level"] == new_role_data["level"], "Role level not updated"
        assert response.json()["name"] == new_role_data["name"], "Role name not updated"
        assert response.json()["description"] == new_role_data["description"], "Role description not updated"
        assert all(
            permission["name"] in new_permissions for permission in response.json()["permissions"]
        ), "Permissions not updated"

        pytest.club_role_data = new_role_data

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_get_club_role(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Get club role
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["name"] == pytest.club_role_data["name"], "Expected role not found"
        assert response.json()["level"] == pytest.club_role_data["level"], "Expected role level not found"
        assert (
            response.json()["description"] == pytest.club_role_data["description"]
        ), "Expected role description not found"
        assert all(
            permission["name"] in pytest.club_role_data["permissions"] for permission in response.json()["permissions"]
        ), "Expected permissions not found"
        # Logout
        logout(client, tokens)

@pytest.mark.dependency(depends=["test_create_club_role"])
def test_delete_club_role(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Delete club role
        response = client.delete(
            f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_200_OK

        # Check if role was deleted
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, "Role not deleted"

        # Logout
        logout(client, tokens)


###########################################################################
############################# Tests - Employee ############################
###########################################################################
@pytest.mark.dependency(depends=["test_create_club"])
def test_get_club_employees(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Get employees
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/employees/all",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
        )
        assert response.status_code == status.HTTP_200_OK

        employees = []
        for role in response.json().values():
            employees.extend(role)
        
        assert len(employees) > 0, "No employees found"

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_create_club"])
def test_create_employee(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        employee_details = get_admin_user_details(client, capsys)

        # Create employee
        response = client.post(
            f"/api/v1/clubs/{pytest.club_id}/employees",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json={"user_ident": employee_details["email"], "level": 1},
        )
        assert response.status_code == status.HTTP_200_OK

        # Check if employee was created
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/employees",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            params={"user_id": employee_details["id"]},
        )
        assert response.status_code == status.HTTP_200_OK, "Employee not created"
        assert response.json()["role_level"] == 1, "Employee has wrong level"

        pytest.employee_id = employee_details["id"]

        # Logout
        logout(client, tokens)


@pytest.mark.dependency(depends=["test_create_employee"])
def test_update_employee(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Update employee
        response = client.put(
            f"/api/v1/clubs/{pytest.club_id}/employees",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            json={"user_id": pytest.employee_id, "level": 2},
        )
        assert response.status_code == status.HTTP_200_OK

        # Check if employee was updated
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/employees",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            params={"user_id": pytest.employee_id},
        )
        assert response.status_code == status.HTTP_200_OK, "Employee not updated"
        assert response.json()["role_level"] == 2, "Employee has wrong level"

        # Logout
        logout(client, tokens)

@pytest.mark.dependency(depends=["test_create_employee"])
def test_delete_employee(capsys):
    with TestClient(app) as client:
        # Login
        tokens = login_email(client, capsys)

        # Delete employee
        response = client.delete(
            f"/api/v1/clubs/{pytest.club_id}/employees",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            params={"user_id": pytest.employee_id},
        )
        assert response.status_code == status.HTTP_200_OK

        # Check if employee was deleted
        response = client.get(
            f"/api/v1/clubs/{pytest.club_id}/employees",
            headers={"Authorization": f"Bearer {tokens['access_token']}", "application-id": pytest.application_id},
            params={"user_id": pytest.employee_id},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, "Employee not deleted"

        # Logout
        logout(client, tokens)