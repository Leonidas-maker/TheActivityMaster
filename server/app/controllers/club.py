from fastapi import HTTPException
import uuid
from typing import List, Union, Optional, Tuple

from config.settings import DEBUG, DEFAULT_TIMEZONE
from config.permissions import ClubPermissions

from models import m_user, m_club
from schemas import s_club, s_generic, s_role

from crud import (
    verification as verification_crud,
    club as club_crud,
    user as user_crud,
    role as role_crud,
)

from core.generic import EndpointContext
import core.security as core_security


async def create_club(
    ep_context: EndpointContext, token_details: core_security.TokenDetails, club_create: s_club.ClubCreate
) -> s_club.Club:
    """Create a club

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_create: The data to create a new club
    :raises HTTPException: If the user identity is not verified
    :return: The created club object
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    user_id = token_details.user_id

    if not await verification_crud.is_user_identity_verified(db, user_id) and not await role_crud.is_user_elevated(
        db, user_id
    ):
        raise HTTPException(status_code=403, detail="User identity not verified")

    if await club_crud.club_exists(db, club_create.name):
        raise HTTPException(status_code=400, detail="Club name already exists")

    club = await club_crud.create_club(db, user_id, club_create)

    audit_log.club_created(user_id, club.id)

    response = s_club.Club.model_validate(club)
    await db.commit()
    return response


async def get_club(
    ep_context: EndpointContext,
    club_id: uuid.UUID,
) -> m_user.Club:
    """Get a club by ID

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club to get
    :raises HTTPException: If the user is not a member of the club
    :return: The club with the given ID
    """
    db = ep_context.db
    club = await club_crud.get_club_with_owners(db, club_id)

    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return club


async def update_club(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    club_update: s_club.ClubUpdate,
) -> s_club.Club:
    """Update a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club to update
    :param club_update: The data to update a club
    :return: The updated club object
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    user_id = token_details.user_id

    club = await club_crud.get_club(db, club_id, with_details=True)

    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    if club_update.name and await club_crud.club_exists(db, club_update.name):
        raise HTTPException(status_code=400, detail="Club name already exists")

    try:
        details = await club_crud.update_club(db, club, club_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    audit_log.club_updated(user_id, club_id, details)

    response = s_club.Club.model_validate(club)
    await db.commit()
    return response


###########################################################################
################################ Club Role ################################
###########################################################################
async def create_club_role(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    club_role_create: s_role.ClubRoleCreate,
) -> s_role.ClubRole:
    """Add a role to a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param club_role: The role to add to the club
    :return: The added club role
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if len(club_role_create.permissions) == 0:
        raise HTTPException(status_code=400, detail="Please provide permissions")

    if await role_crud.club_role_exists(db, club_id, club_role_create.name, club_role_create.level):
        raise HTTPException(status_code=400, detail="Role name or level already exists")

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, level=club_role_create.level):
        raise HTTPException(status_code=403, detail="User has higher or equal level than role")

    permissions = await role_crud.get_permissions(db, names=club_role_create.permissions)
    if len(permissions) != len(club_role_create.permissions):
        raise HTTPException(status_code=400, detail="Invalid permissions")

    new_role = await role_crud.add_club_role(
        db, club_id, club_role_create.name, club_role_create.description, club_role_create.level, permissions
    )

    audit_log.club_role_added(issuer_id, club_id, new_role.id)

    response = s_role.ClubRole.model_validate(new_role)

    await db.commit()
    return response


async def update_club_role(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_id: int,
    club_role_update: s_role.ClubRoleUpdate,
) -> s_role.ClubRole:
    """Update a role in a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param role_id: The ID of the role to update
    :param club_role: The updated role data
    :return: The updated club role
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    club_role = await role_crud.get_club_role(db, club_id, role_id=role_id, with_details=True)

    if not club_role:
        raise HTTPException(status_code=404, detail="Role not found")

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, level=club_role.level):
        raise HTTPException(status_code=403, detail="User has higher or equal level than role")

    try:
        details = await role_crud.update_club_role(db, club_role, club_role_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    audit_log.club_role_updated(issuer_id, club_role.club_id, club_role.id, details)

    result = s_role.ClubRole.model_validate(club_role)
    await db.commit()
    return result


async def delete_club_role(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_id: int,
) -> None:
    """Delete a role from a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param role_id: The ID of the role to delete
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id):
        raise HTTPException(status_code=403, detail="User has higher or equal level than role")

    user_club_roles = await role_crud.get_user_club_roles(db, club_id, role_id)

    if user_club_roles:
        raise HTTPException(status_code=403, detail="Role is assigned to users")

    await role_crud.delete_club_role(db, club_id, role_id)
    audit_log.club_role_deleted(issuer_id, club_id, role_id)

    await db.commit()


###########################################################################
################################# Employee ################################
###########################################################################
async def add_employee(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_assignment: s_club.UserClubRoleAssignment,
) -> None:
    """Assign a user to a club role

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param level: The level of the role
    :param user_id: The ID of the user to assign the role to
    :return: The assigned user club role
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    club_role = await role_crud.get_club_role(db, club_id, level=role_assignment.level)

    if not club_role:
        raise HTTPException(status_code=404, detail="Role not found")

    user = await user_crud.get_user_by_ident(db, role_assignment.user_ident)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if issuer_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot assign role to self")

    if await role_crud.is_user_employee_of_club(db, user.id, club_id):
        raise HTTPException(
            status_code=403,
            detail="User is already an employee of the club. Please use the put method to update the role",
        )

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, level=club_role.level):
        raise HTTPException(status_code=403, detail="User or Role has higher or equal level than issuer")

    await role_crud.add_employee(db, club_id, club_role.id, user.id)
    audit_log.club_employee_added(token_details.user_id, club_id, user.id, club_role.id)

    await db.commit()


async def update_employee(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    role_assignment: s_club.UserClubRoleChange,
) -> None:
    """Update a user's role in a club

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param level: The level of the role
    :param user_id: The ID of the user to update the role for
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if not await role_crud.is_user_employee_of_club(db, role_assignment.user_id, club_id):
        raise HTTPException(status_code=403, detail="User is not an employee of the club")

    club_role_id = await role_crud.get_club_role_id(db, club_id, level=role_assignment.level)

    if not club_role_id:
        raise HTTPException(status_code=404, detail="Role not found")

    if not await role_crud.has_user_higher_club_level(
        db, issuer_id, club_id, to_user_id=role_assignment.user_id, level=role_assignment.level
    ):
        raise HTTPException(status_code=403, detail="User or Role has higher or equal level than issuer")

    old_club_role_id = await role_crud.update_employee(db, club_id, role_assignment.user_id, club_role_id)
    audit_log.club_employee_updated(issuer_id, club_id, role_assignment.user_id, old_club_role_id, club_role_id)

    await db.commit()


async def remove_employee(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Remove a user from a club role

    :param ep_context: The endpoint context containing database and logger
    :param club_id: The ID of the club
    :param level: The level of the role
    :param user_id: The ID of the user to remove the role from
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if issuer_id == user_id:
        raise HTTPException(status_code=400, detail="Cannot remove role from self")

    if not await role_crud.is_user_employee_of_club(db, issuer_id, club_id):
        raise HTTPException(status_code=403, detail="User is not an employee of the club")

    if not await role_crud.has_user_higher_club_level(db, issuer_id, club_id, user_id):
        raise HTTPException(status_code=403, detail="Cannot remove role from user with higher level")

    await role_crud.remove_employee(db, club_id, user_id)
    audit_log.club_employee_removed(issuer_id, club_id, user_id, 0)
    await db.commit()


###########################################################################
################################# Program #################################
###########################################################################
async def create_program(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    new_program: s_club.ProgramCreate,
) -> s_club.Program:
    """Create a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program: The details of the program to create
    :return: The created program
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    if new_program.pricing_model == m_club.PriceType.PACKAGE and any(
        [session.price for session in new_program.sessions]
    ):
        raise HTTPException(status_code=400, detail="No session should have a price if the pricing model is 'package'.")

    if new_program.pricing_model == m_club.PriceType.PER_SESSION and not all(
        [session.price for session in new_program.sessions]
    ):
        raise HTTPException(
            status_code=400, detail="Each session must have a price if the pricing model is 'per_session'."
        )

    if await club_crud.program_exists(db, club_id, new_program.name):
        raise HTTPException(status_code=400, detail="Program name already exists")

    try:
        program = await club_crud.create_program(db, club_id, new_program)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    details = f"Sessions: {', '.join([str(session.id) for session in program.sessions])}"
    audit_log.program_created(issuer_id, club_id, program.id, details)

    s_program = s_club.Program.model_validate(program)

    await db.commit()
    return s_program


async def get_program(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
) -> m_club.Program:
    """Get a program by ID depending on the user's permissions

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program to get
    :return: The program with the given ID
    """
    db = ep_context.db
    user_id = token_details.user_id

    if await club_crud.could_user_read_private_program(db, user_id, club_id, program_id):
        program = await club_crud.get_program(db, club_id, program_id, with_details=True)
    else:
        program = await club_crud.get_program(
            db, club_id, program_id, with_details=True, status=m_club.ProgramStatus.ACTIVE
        )

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program


async def update_program(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    program_update: s_club.ProgramUpdate,
) -> s_club.Program:
    """Update a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program to update
    :param program_update: The data to update the program with
    :return: The updated program
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    program = await club_crud.get_program(db, club_id, program_id, with_details=True)

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    try:
        details = await club_crud.update_program(db, program, program_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    audit_log.program_updated(issuer_id, program.club_id, program.id, details)

    s_program = s_club.Program.model_validate(program)

    await db.commit()
    return s_program


async def delete_program(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
) -> None:
    """Delete a program

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program to delete
    :return: None
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    program = await club_crud.get_program(db, club_id, program_id)

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    # TODO: Check if program sessions are booked
    # * We need a param to force delete the program and cancel all bookings -> init refund process
    # * If not force delete, set the last session date of each session to the last booked date
    # await club_crud.delete_program(db, program_id)
    # audit_log.program_deleted(issuer_id, club_id, program_id)

    # await db.commit()


###########################################################################
################################# Session #################################
###########################################################################
async def create_session(
    ep_context: EndpointContext,
    token_details: core_security.TokenDetails,
    club_id: uuid.UUID,
    program_id: uuid.UUID,
    new_session: s_club.SessionCreate,
) -> s_club.Session:
    """Create a session

    :param ep_context: The endpoint context containing database and logger
    :param token_details: The token details of the authenticated user
    :param club_id: The ID of the club
    :param program_id: The ID of the program
    :param session: The details of the session to create
    :return: The created session
    """
    db = ep_context.db
    audit_log = ep_context.audit_logger
    issuer_id = token_details.user_id

    program = await club_crud.get_program(db, club_id, program_id, with_details=True)

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")  

    if await club_crud.session_exists(db, program_id, new_session):
        raise HTTPException(status_code=400, detail="Session name already exists")

    try:
        session = await club_crud.create_session(db, program_id, new_session)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    details = f"Program: {program_id}"
    audit_log.session_created(issuer_id, club_id, session.id, details)

    s_session = s_club.Session.model_validate(session)

    await db.commit()
    return s_session
