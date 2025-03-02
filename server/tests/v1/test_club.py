# type: ignore
import pytest
import random
from fastapi import status

from .conftest import *

from main import app
from config.permissions import DEFAULT_CLUB_ROLES


###########################################################################
################################# Default #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(capsys, test_user, admin_user):
    """Fixture that registers a user and returns the user data"""
    test_user.set_capsys(capsys)
    admin_user.set_capsys(capsys)
    test_user.register_user()

    test_user.login_email()
    test_user.submit_identity_verification(False)
    admin_user.verify_identity(test_user.user_id)
    test_user.check_identity_verification_status()


###########################################################################
############################### Tests - Club ##############################
###########################################################################
@pytest.mark.dependency(depends=["test_registered_user"])
def test_create_club(test_user):
    response = test_user.post(
        "/api/v1/clubs",
        json=pytest.club_data,
    )
    assert response.json()["name"] == pytest.club_data["name"], "Club not created"
    pytest.club_id = response.json()["id"]


@pytest.mark.dependency(depends=["test_registered_user", "test_create_club"])
def test_get_clubs(test_user):
    response = test_user.get(
        "/api/v1/clubs",
        params={"page": 1, "page_size": 50},
    )
    assert len(response.json()) > 0, "No clubs found"

    club_found = False
    for club in response.json():
        if club["name"] == pytest.club_data["name"]:
            club_found = True
            break
    assert club_found, "Club not found"


@pytest.mark.dependency(depends=["test_create_club"])
def test_search_clubs(client):
    response = client.get(
        "/api/v1/clubs/search",
        params={"search_query": pytest.club_data["name"]},
    )
    assert len(response.json()) > 0, "No clubs found"

    club_found = False
    for club in response.json():
        if club["name"] == pytest.club_data["name"]:
            club_found = True
            break
    assert club_found, "Club not found"


@pytest.mark.dependency(depends=["test_create_club"])
def test_get_club(test_user):
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}",
    )
    assert response.json()["name"] == pytest.club_data["name"], "Expected club not found"


@pytest.mark.dependency(depends=["test_create_club"])
def test_update_club(test_user):
    response = test_user.put(
        f"/api/v1/clubs/{pytest.club_id}",
        json={"name": "Updated" + pytest.club_data["name"]},
    )
    assert response.json()["name"] == "Updated" + pytest.club_data["name"], "Club not updated"
    pytest.club_data["name"] = response.json()["name"]


###########################################################################
############################ Tests - Club Roles ###########################
###########################################################################
@pytest.mark.dependency()
def test_get_available_club_permissions(client):
    response = client.get("/api/v1/clubs/permissions")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()) > 0, "No club permissions found"

    pytest.club_role_permissions = [permission["name"] for permission in response.json()]
    pytest.club_role_data["permissions"] = random.sample(pytest.club_role_permissions, 3)


@pytest.mark.dependency(depends=["test_get_club"])
def test_check_default_club_roles(test_user):
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/roles/all",
    )
    assert len(response.json()) > 0, "No club roles found"

    correct_roles = 0

    for role in response.json():
        if not role["name"] in DEFAULT_CLUB_ROLES.keys():
            assert False, "Unexpected club role found"
        else:
            correct_roles += 1

    assert correct_roles == len(DEFAULT_CLUB_ROLES.keys()), "Not all roles found"


@pytest.mark.dependency(depends=["test_get_club", "test_get_available_club_permissions"])
def test_create_club_role(test_user):
    # Create club role
    response = test_user.post(
        f"/api/v1/clubs/{pytest.club_id}/roles",
        json=pytest.club_role_data,
    )
    assert response.json()["name"] == pytest.club_role_data["name"], "Club role not created"

    # Check if role was created
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/roles/{response.json()['id']}",
    )
    assert response.json()["name"] == pytest.club_role_data["name"], "Expected role not found"
    assert response.json()["level"] == pytest.club_role_data["level"], "Expected role level not found"
    assert response.json()["description"] == pytest.club_role_data["description"]
    assert all(
        permission["name"] in pytest.club_role_data["permissions"] for permission in response.json()["permissions"]
    ), "Expected permissions not found"

    pytest.club_role_id = response.json()["id"]


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_update_club_role(test_user):
    new_permissions = random.sample(pytest.club_role_permissions, 2)

    new_role_data = {
        "level": 6,
        "name": "Updated" + pytest.club_role_data["name"],
        "description": "Updated Test Role Description",
        "permissions": new_permissions,
    }

    response = test_user.put(
        f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}",
        json=new_role_data,
    )

    assert response.json()["level"] == new_role_data["level"], "Role level not updated"
    assert response.json()["name"] == new_role_data["name"], "Role name not updated"
    assert response.json()["description"] == new_role_data["description"], "Role description not updated"
    assert all(
        permission["name"] in new_permissions for permission in response.json()["permissions"]
    ), "Permissions not updated"

    pytest.club_role_data = new_role_data


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_get_club_role(test_user):
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}",
    )
    assert response.json()["name"] == pytest.club_role_data["name"], "Expected role not found"
    assert response.json()["level"] == pytest.club_role_data["level"], "Expected role level not found"
    assert response.json()["description"] == pytest.club_role_data["description"], "Expected role description not found"
    assert all(
        permission["name"] in pytest.club_role_data["permissions"] for permission in response.json()["permissions"]
    ), "Expected permissions not found"


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_delete_club_role(test_user):
    response = test_user.delete(
        f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}",
    )

    # Check if role was deleted
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/roles/{pytest.club_role_id}", check_status=False,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, "Role not deleted"


###########################################################################
############################# Tests - Employee ############################
###########################################################################
@pytest.mark.dependency(depends=["test_create_club"])
def test_get_club_employees(test_user):
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/employees/all",
    )
    assert response.status_code == status.HTTP_200_OK, response.json()

    employees = []
    for role in response.json().values():
        employees.extend(role)

    assert len(employees) > 0, "No employees found"


@pytest.mark.dependency(depends=["test_create_club"])
def test_create_employee(test_user, admin_user):
    employee_details = admin_user.get_details()

    # Create employee
    response = test_user.post(
        f"/api/v1/clubs/{pytest.club_id}/employees",
        json={"user_ident": employee_details["email"], "level": 1},
    )

    # Check if employee was created
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/employees",
        params={"user_id": employee_details["id"]},
    )
    assert response.json()["role_level"] == 1, "Employee has wrong level"

    pytest.employee_id = employee_details["id"]


@pytest.mark.dependency(depends=["test_create_employee"])
def test_update_employee(test_user):
    response = test_user.put(
        f"/api/v1/clubs/{pytest.club_id}/employees",
        json={"user_id": pytest.employee_id, "level": 2},
    )

    # Check if employee was updated
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/employees",
        params={"user_id": pytest.employee_id},
    )
    assert response.json()["role_level"] == 2, "Employee has wrong level"


@pytest.mark.dependency(depends=["test_create_employee"])
def test_delete_employee(test_user):
    response = test_user.delete(
        f"/api/v1/clubs/{pytest.club_id}/employees",
        params={"user_id": pytest.employee_id},
    )

    # Check if employee was deleted
    response = test_user.get(
        f"/api/v1/clubs/{pytest.club_id}/employees",
        params={"user_id": pytest.employee_id}, check_status=False,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND, "Employee not deleted"