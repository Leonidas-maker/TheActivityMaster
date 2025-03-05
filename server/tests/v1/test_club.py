import pytest
import random
from fastapi import status
import os

from .conftest import *

from config.permissions import DEFAULT_CLUB_ROLES, ClubPermissions  # type: ignore

from .testclasses import (
    ClubRole,
    Employee,
    Program,
    SessionCourse,
    SessionEvent,
    get_random_programs,
    get_random_session_courses,
    get_random_session_events,
)

from .enums import ProgramStatusPublic

###########################################################################
################################# Default #################################
###########################################################################
@pytest.mark.dependency()
def test_registered_user(capsys, test_user, admin_user, test_users):
    """Fixture that registers a user and returns the user data"""

    users = [test_user] + test_users
    admin_user.set_capsys(capsys)

    for x, user in enumerate(users):
        user.set_capsys(capsys)
        user.register_user()
        user.login_email()
        if x < len(users) - 1:
            user.submit_identity_verification(False)
            admin_user.verify_identity(user.user_id)
            user.check_identity_verification_status()


###########################################################################
############################### Tests - Club ##############################
###########################################################################
@pytest.mark.dependency(depends=["test_registered_user"])
def test_create_club(test_club):
    test_club.create()


@pytest.mark.dependency(depends=["test_registered_user", "test_create_club"])
def test_get_clubs(test_user, test_club):
    response = test_user.get(
        "/api/v1/clubs",
        params={"page": 1, "page_size": 50},
    )

    assert len(response.json()) > 0, "No clubs found"

    club_found = False
    for club in response.json():
        if club["name"] == test_club.name:
            club_found = True
            break
    assert club_found, "Club not found"


@pytest.mark.dependency(depends=["test_create_club"])
def test_search_clubs(client, test_club):
    response = client.get(
        "/api/v1/clubs/search",
        params={"search_query": test_club.name},
    )
    assert len(response.json()) > 0, "No clubs found"

    club_found = False
    for club in response.json():
        if club["name"] == test_club.name:
            club_found = True
            break
    assert club_found, "Club not found"


@pytest.mark.dependency(depends=["test_create_club"])
def test_get_club(test_club):
    test_club.get()


@pytest.mark.dependency(depends=["test_create_club"])
def test_update_club(test_club):
    test_club.update()


# ###########################################################################
# ############################ Tests - Club Roles ###########################
# ###########################################################################
@pytest.mark.dependency()
def test_get_available_club_permissions(client):
    response = client.get("/api/v1/clubs/permissions")
    assert response.status_code == status.HTTP_200_OK, response.json()
    assert len(response.json()) > 0, "No club permissions found"

    default_permissions = [permission.value for permission in ClubPermissions]

    assert all(permission["name"] in default_permissions for permission in response.json())


@pytest.mark.dependency(depends=["test_get_club"])
def test_check_default_club_roles(test_club):
    test_club.check_default_roles()


@pytest.mark.dependency(depends=["test_get_club", "test_get_available_club_permissions"])
def test_create_club_role(test_club):
    permissions = random.sample([permission.value for permission in ClubPermissions], 2)
    club_role = ClubRole(test_club, "Test Role", permissions, 5, "Test Description")
    club_role.create()
    test_club.roles.append(club_role)


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_update_club_role(test_club):
    club_role = test_club.roles[-1]
    club_role.update()


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_get_club_role(test_club):
    club_role = random.choice(test_club.roles)
    club_role.get()


@pytest.mark.dependency(depends=["test_create_club_role"])
def test_delete_club_role(test_club):
    club_role = test_club.roles.pop()
    club_role.delete(check_deletion=True)


# ###########################################################################
# ############################# Tests - Employee ############################
# ###########################################################################
@pytest.mark.dependency(depends=["test_create_club"])
def test_get_club_employees(test_club):
    test_club.refresh_employees()
    is_owner_present = False
    assert len(test_club.employees) > 0, "No employees found"
    for employee in test_club.employees:
        if employee.role.level == 0:
            is_owner_present = True
            break
    assert is_owner_present, "Owner not found"


@pytest.mark.dependency(depends=["test_create_club"])
def test_create_employee(test_club, test_users):
    role_to_assign = get_random_role(test_club)
    employee_user = test_users[0]
    employee = Employee(employee_user.email, test_club, role_to_assign, employee_user)
    employee.create()


@pytest.mark.dependency(depends=["test_create_employee"])
def test_update_employee(test_club):
    employee = test_club.employees[-1]
    club_role = get_random_role(test_club)
    employee.update(club_role)


@pytest.mark.dependency(depends=["test_create_employee"])
def test_delete_employee(test_club):
    employee = test_club.employees.pop()
    employee.delete(check_deletion=True)


###########################################################################
############################ Program Offerings ############################
###########################################################################
@pytest.mark.dependency(depends=["test_create_club"])
def test_create_all_program_offering_types(test_club):
    """This tests program and session creation"""
    programs = get_random_programs(test_club, 2, 15)

    for program in programs:
        program.create()


@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_draft_get_program_offering(test_club):
    program = random.choice(test_club.programs)
    program.get()


@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_complete_update_draft_program_offering(test_club):
    """This tests program update and price_type change"""
    for program in test_club.programs:
        program.update()


@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_delete_draft_program_offering(test_club):
    program = test_club.programs.pop()
    # TODO Change - Force delete is not implemented yet
    program.delete(force_delete=False, check_deletion=True)


@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_create_session_event(test_club):
    """This tests session creation"""
    program = test_club.programs[0]
    session = get_random_session_events(program, 1)[0]
    session.create()


@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_create_session_course(test_club):
    """This tests session creation"""
    program = test_club.programs[0]
    session = get_random_session_courses(program, 1)[0]
    session.create()

@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_get_session(test_club):
    program = random.choice(test_club.programs)
    session = random.choice(program.session_courses + program.session_events)
    session.get()

@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_complete_update_draft_session(test_club):
    program = random.choice(test_club.programs)
    for session in program.session_courses + program.session_events:
        session.randomize()
        session.update()

@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_delete_session(test_club):
    program = random.choice(test_club.programs)
    session = random.choice(program.session_courses + program.session_events)
    session.delete(check_deletion=True)

@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_reschedule_session(test_club):
    program = random.choice(test_club.programs)
    session: SessionCourse = random.choice(program.session_courses)
    session.reschedule_occurrence()

@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_cancel_session(test_club):
    program = random.choice(test_club.programs)
    session: SessionCourse = random.choice(program.session_courses)
    session.cancel_occurrence()

@pytest.mark.dependency(depends=["test_cancel_session"])
def test_reinstate_session(test_club):
    program = random.choice(test_club.programs)
    session: SessionCourse = random.choice(program.session_courses)
    occurrence_id = session.cancel_occurrence(check=False)
    session.reinstate_occurrence(occurrence_id)

@pytest.mark.dependency(depends=["test_create_all_program_offering_types", "test_create_employee"])
def test_assign_trainer_to_program(test_club, test_users):
    """Test assigning and getting trainers for a program"""
    program = test_club.programs[0]
    trainer = test_users[0]
    manager_role = next(role for role in test_club.roles if role.level == 1)

    employee = Employee(trainer.email, test_club, manager_role, trainer)
    employee.create()

    program.assign_trainer(trainer.user_id)

@pytest.mark.dependency(depends=["test_assign_trainer_to_program"])
def test_unassign_trainer_from_program(test_club, test_users):
    program = test_club.programs[0]    
    program.unassign_trainer(test_users[0].user_id)


@pytest.mark.dependency(depends=["test_create_all_program_offering_types"])
def test_update_program_status_error(test_club):
    response = test_club.programs[0].update_status(ProgramStatusPublic.ACTIVE, check=False)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()

@pytest.mark.dependency(depends=["test_create_club"])
def test_club_update_stripe(admin_user, test_club):
    admin_user.put(
        f"/api/v1/clubs/{test_club.club_id}/stripe",
        json={"stripe_account_id": f"acct_{os.urandom(16).hex()}"},
    )

@pytest.mark.dependency(depends=["test_create_all_program_offering_types", "test_club_update_stripe"])
def test_update_program_status(test_club):
    test_club.programs[0].update_status(ProgramStatusPublic.ACTIVE)