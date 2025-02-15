from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, or_, exists, and_
from sqlalchemy.orm import undefer, joinedload, selectinload, aliased
from typing import List, Tuple, Optional, Union
import uuid

from config.permissions import ClubPermissions
from models import m_club, m_user

from config.permissions import ClubPermissions, DEFAULT_CLUB_ROLES


async def get_permissions(db: AsyncSession, prefix: Optional[str] = None, names: Optional[List[ClubPermissions]] = None) -> List[m_club.Permission]:
    """Get all permissions

    :param db: The database session
    :param prefix: Optional[str]: Filter permissions by prefix
    :param names: Optional[List[str]]: Filter permissions by name
    :return: A list of permissions
    """
    query = select(m_club.Permission).options(undefer(m_club.Permission.description))
    if prefix:
        query = query.filter(m_club.Permission.name.startswith(prefix))
    if names:
        names_str = [name.value for name in names]
        query = query.filter(m_club.Permission.name.in_(names_str))
    res = await db.execute(query)
    return list(res.unique().scalars().all())


###########################################################################
############################# Generic - Roles #############################
###########################################################################
async def get_generic_role_by_name(db: AsyncSession, role_name: str) -> m_user.GenericRole:
    """
    Get a generic role by its name

    :param db: AsyncSession: Database session
    :param role_name: str: Name of the role to search for
    :return: GenericRole: The role
    """
    res = await db.execute(select(m_user.GenericRole).filter(m_user.GenericRole.name == role_name))
    return res.unique().scalar_one_or_none()


async def get_user_generic_roles(
    db: AsyncSession, user_id: uuid.UUID, query_options: list = []
) -> List[m_user.GenericRole]:
    """
    Get the generic roles for a user

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: list[GenericRole]: The generic roles
    """
    res = await db.execute(
        select(m_user.GenericRole)
        .join(m_user.UserRole)
        .filter(m_user.UserRole.user_id == user_id)
        .options(*query_options)
    )
    return list(res.scalars().all())


async def has_user_any_generic_role(db: AsyncSession, user_id: uuid.UUID, roles: List[str]) -> bool:
    """Check if a user has any of the specified generic roles

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to check
    :param roles: List[str]: List of roles to check for
    :return: bool: True if the user has any of the specified roles, otherwise False
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_user.UserRole)
                .join(m_user.GenericRole, m_user.UserRole.role_id == m_user.GenericRole.id)
                .filter(m_user.UserRole.user_id == user_id, m_user.GenericRole.name.in_(roles))
            )
        )
    )
    return bool(res.scalar_one_or_none())


async def is_user_elevated(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """
    Check if a user has elevated permissions

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: bool: If the user has elevated permissions
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_user.UserRole)
                .join(m_user.GenericRole, m_user.UserRole.role_id == m_user.GenericRole.id)
                .filter(m_user.UserRole.user_id == user_id, m_user.GenericRole.name == "Admin")
            )
        )
    )
    return bool(res.scalar_one_or_none())


###########################################################################
################################ Club Role ################################
###########################################################################
async def create_default_club_roles(db: AsyncSession, club_id: uuid.UUID):
    res = await db.execute(select(m_club.ClubRole))
    existing_roles = {role.name: role for role in res.unique().scalars().all()}
    new_roles = []

    for role_name, role_data in DEFAULT_CLUB_ROLES.items():
        if not existing_roles.get(role_name):
            new_role = m_club.ClubRole(
                name=role_name, description=role_data["description"], club_id=club_id, level=role_data["level"]
            )
            new_roles.append(new_role)

    if new_roles:
        db.add_all(new_roles)

    await db.flush()

    res = await db.execute(select(m_club.Permission))
    permissions = {permission.name: permission for permission in res.unique().scalars().all()}
    new_role_permissions = []

    for role in new_roles:
        # If * is in the permissions, add all permissions starting with the defined prefix
        for role_permissions in DEFAULT_CLUB_ROLES[role.name]["permissions"]:
            if "*" in role_permissions:
                prefix = role_permissions.split("*")[0]
                new_role_permissions.extend(
                    [
                        m_club.ClubRolePermission(role_id=role.id, permission_id=permission.id)
                        for permission in permissions.values()
                        if permission.name.startswith(prefix)
                    ]
                )
            else:
                permission = permissions.get(role_permissions)
                if permission:
                    new_role_permissions.append(m_club.ClubRolePermission(role_id=role.id, permission_id=permission.id))

    db.add_all(new_role_permissions)
    await db.flush()


async def get_club_role(
    db: AsyncSession,
    club_id: uuid.UUID,
    role_name: Optional[str] = None,
    role_id: Optional[int] = None,
    level: Optional[int] = None,
    with_details: bool = False,
) -> Optional[m_club.ClubRole]:
    """
    Get a club role by its name, ID, or level

    :param db: AsyncSession: Database session
    :param club_id: UUID: ID of the club
    :param role_name: Optional[str]: Name of the role to search for
    :param role_id: Optional[int]: ID of the role to search for
    :return: Tuple[ClubRole, int]: The role and its ID
    """

    query = select(m_club.ClubRole).filter(m_club.ClubRole.club_id == club_id)
    if role_name:
        query = query.filter(m_club.ClubRole.name == role_name)
    if role_id:
        query = query.filter(m_club.ClubRole.id == role_id)
    if level:
        query = query.filter(m_club.ClubRole.level == level)
    
    if with_details:
        query = query.options(
            undefer(m_club.ClubRole.description),
            joinedload(m_club.ClubRole.permissions).undefer(m_club.Permission.description),
        )

    res = await db.execute(query)
    return res.unique().scalar_one_or_none()


async def get_club_role_id(
    db: AsyncSession,
    club_id: uuid.UUID,
    role_name: Optional[str] = None,
    level: Optional[int] = None,
) -> Optional[int]:
    """
    Get a club role id by its name or level

    :param db: AsyncSession: Database session
    :param club_id: UUID: ID of the club
    :param role_name: Optional[str]: Name of the role to search for
    :param role_id: Optional[int]: ID of the role to search for
    :return: Tuple[ClubRole, int]: The role and its ID
    """
    conditions = [m_club.ClubRole.club_id == club_id]

    if not role_name and level is None:
        raise ValueError("Role name or level must be provided")

    if role_name:
        conditions.append(m_club.ClubRole.name == role_name)
    if level is not None:
        conditions.append(m_club.ClubRole.level == level)

    query = select(m_club.ClubRole.id).filter(and_(*conditions))
    res = await db.execute(query)

    return res.scalar_one_or_none()


async def club_role_exists(db: AsyncSession, club_id: uuid.UUID, role_name: str, level: int) -> bool:
    """
    Check if a role with the given name and level exists in a club

    :param db: AsyncSession: Database session
    :param club_id: UUID: ID of the club
    :param role_name: str: Name of the role
    :param level: int: Level of the role
    :return: bool: True if the role exists, otherwise False
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.ClubRole)
                .filter(
                    m_club.ClubRole.club_id == club_id,
                    m_club.ClubRole.name == role_name,
                    m_club.ClubRole.level == level,
                )
            )
        )
    )
    return bool(res.scalar_one_or_none())


async def get_club_roles(db: AsyncSession, club_id: uuid.UUID) -> List[m_club.ClubRole]:
    """Get all roles for a club

    :param db: The database session
    :param club_id: The ID of the club to get roles for
    :return: A list of roles
    """
    res = await db.execute(
        select(m_club.ClubRole)
        .filter(m_club.ClubRole.club_id == club_id)
        .options(
            undefer(m_club.ClubRole.description),
            joinedload(m_club.ClubRole.permissions).undefer(m_club.Permission.description),
        )
    )
    return list(res.unique().scalars().all())


async def get_club_role_members(db: AsyncSession, club_id: uuid.UUID, role_id: int) -> List[m_user.User]:
    """Get the members of a club role

    :param db: The database session
    :param club_id: The ID of the club
    :param role_id: The ID of the role
    :return: The members of the role
    """
    res = await db.execute(
        select(m_user.User)
        .join(m_club.UserClubRole)
        .join(m_club.ClubRole)
        .filter(m_club.ClubRole.club_id == club_id, m_club.ClubRole.id == role_id)
    )
    return list(res.unique().scalars().all())


async def add_club_role(
    db: AsyncSession, club_id: uuid.UUID, name: str, description: str, level: int, permissions: List[m_club.Permission]
) -> m_club.ClubRole:
    """Add a role to a club

    :param db: The database session
    :param club_id: The ID of the club
    :param name: The name of the role
    :param description: The description of the role
    :param level: The level of the role
    :return: The added role
    """
    db_role = m_club.ClubRole(name=name, description=description, level=level, club_id=club_id, permissions=permissions)
    db.add(db_role)
    await db.flush()
    return db_role


async def delete_club_role(db: AsyncSession, club_id: uuid.UUID, role_id: int):
    """Delete a role from a club

    :param db: The database session
    :param club_id: The ID of the club
    :param role_id: The ID of the role to delete
    :return: None
    """
    await db.execute(delete(m_club.ClubRolePermission).where(m_club.ClubRolePermission.role_id == role_id))

    await db.execute(
        delete(m_club.ClubRole).where(m_club.ClubRole.id == role_id).where(m_club.ClubRole.club_id == club_id)
    )


async def get_user_club_roles(db: AsyncSession, club_id: uuid.UUID, club_role_id: int) -> List[m_club.UserClubRole]:
    """Get the roles for a user with each description.

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: tuple: (generic_roles, club_roles)
    """
    res = await db.execute(
        select(m_user.UserClubRole)
        .join(m_club.ClubRole)
        .filter(m_club.ClubRole.club_id == club_id, m_user.UserClubRole.club_role_id == club_role_id)
    )
    return list(res.unique().scalars().all())


# ======================================================== #
# ======================= Employee ======================= #
# ======================================================== #
async def add_employee(
    db: AsyncSession, club_id: uuid.UUID, club_role_id: int, user_id: uuid.UUID
) -> m_club.UserClubRole:
    """Assign a club role to a user

    :param db: The database session
    :param club_id: The ID of the club
    :param club_role_id: The ID of the role to assign
    :param user_id: The ID of the user to assign the role to
    :return: The UserClubRole association
    """
    db_user_club_role = m_club.UserClubRole(club_role_id=club_role_id, user_id=user_id)
    db.add(db_user_club_role)
    await db.flush()
    return db_user_club_role


async def update_employee(db: AsyncSession, club_id: uuid.UUID, user_id: uuid.UUID, role_id: int) -> int:
    """Update a user's role in a club

    :param db: The database session
    :param club_id: The ID of the club
    :param user_id: The ID of the user to update
    :param role_id: The ID of the new role
    :return: None
    """
    result = await db.execute(select(m_club.UserClubRole).where(m_club.UserClubRole.user_id == user_id))
    user_club_role = result.unique().scalar_one_or_none()

    if user_club_role is None:
        raise ValueError("User does not have a role in this club.")

    old_role_id = user_club_role.club_role_id
    user_club_role.club_role_id = role_id
    await db.flush()
    return old_role_id


async def remove_employee(db: AsyncSession, club_id: uuid.UUID, user_id: uuid.UUID):
    """Remove a user from a club role

    :param db: The database session
    :param club_id: The ID of the club
    :param user_id: The ID of the user to remove the role from
    :return: None
    """
    await db.execute(
        delete(m_club.UserClubRole)
        .where(m_club.UserClubRole.user_id == user_id)
        .where(m_club.UserClubRole.club_role_id == m_club.ClubRole.id)
        .where(m_club.ClubRole.club_id == club_id)
        .execution_options(is_delete_using=True)
    )


# ======================================================== #
# ========================= User ========================= #
# ======================================================== #
async def is_user_employee_of_club(db: AsyncSession, user_id: uuid.UUID, club_id: uuid.UUID) -> bool:
    """
    Check if a user already has a role in a specific club.

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to check
    :param club_id: UUID: ID of the club to check for role
    :return: bool: True if the user has a role in the club, otherwise False
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.UserClubRole)
                .join(m_club.UserClubRole.club_role)
                .filter(m_club.UserClubRole.user_id == user_id, m_club.ClubRole.club_id == club_id)
            )
        )
    )
    return bool(res.scalar_one_or_none())


async def get_user_club_role(
    db: AsyncSession, user_id: uuid.UUID, club_id: uuid.UUID, query_options: list = []
) -> m_club.ClubRole:
    """
    Get the club role for a user

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :param club_id: UUID: ID of the club to search for
    :return: ClubRole: The club role
    """
    res = await db.execute(
        select(m_user.ClubRole)
        .join(m_user.UserClubRole)
        .filter(m_user.UserClubRole.user_id == user_id, m_user.ClubRole.club_id == club_id)
        .options(*query_options)
    )
    return res.unique().scalar_one_or_none()


async def has_user_any_club_permission(
    db: AsyncSession, user_id: uuid.UUID, club_id: uuid.UUID, permission: List[ClubPermissions]
) -> bool:
    """
    Check if a user has any permissions for a specific club.

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to check
    :param club_id: UUID: ID of the club to check permissions against
    :param permission: List[ClubPermissions]: List of permissions to check for
    :return: bool: True if the user has any of the specified permissions in the club, otherwise False
    """
    res = await db.execute(
        select(
            exists(
                select(1)
                .select_from(m_club.UserClubRole)
                .join(m_club.UserClubRole.club_role)
                .join(m_club.ClubRole.permissions)
                .filter(
                    m_club.UserClubRole.user_id == user_id,
                    m_club.ClubRole.club_id == club_id,
                    m_club.Permission.name.in_([perm.value for perm in permission]),
                )
            )
        )
    )

    return bool(res.scalar_one_or_none())


async def has_user_higher_club_level(
    db: AsyncSession,
    from_user_id: uuid.UUID,
    club_id: uuid.UUID,
    to_user_id: Optional[uuid.UUID] = None,
    level: Optional[int] = None,
) -> bool:
    """
    Checks if a user (from_user) has higher permissions in a specific club.

    If a `to_user_id` is provided, it verifies whether the from_user has a lower (i.e. superior)
    level than the to_user. If a `level` is provided, then the from_user's level must be less than or equal to this value.

    :param db: AsyncSession: Database session
    :param from_user_id: UUID: ID of the user whose permissions are being checked
    :param club_id: UUID: ID of the club
    :param to_user_id: Optional[UUID]: ID of the user to compare against
    :param level: Optional[int]: Maximum permissible level for the from_user
    :return: bool: True if all specified conditions are met, otherwise False
    """
    # Aliases for the from_user
    from_role = aliased(m_club.ClubRole)
    from_user_role = aliased(m_club.UserClubRole)

    # Base query: from_user_role joined with its ClubRole entry
    query = select(1).select_from(from_user_role).join(from_role, from_user_role.club_role_id == from_role.id)

    # Base filter: from_user and club
    conditions = [from_user_role.user_id == from_user_id, from_role.club_id == club_id]

    # If a to_user is specified, extend the query for comparison
    if to_user_id is not None:
        to_user_role = aliased(m_club.UserClubRole)
        to_role = aliased(m_club.ClubRole)
        # First, join to the target user's role
        query = query.join(to_user_role, to_user_role.user_id == to_user_id).join(
            to_role, to_user_role.club_role_id == to_role.id
        )
        conditions.append(to_role.club_id == from_role.club_id)
        conditions.append(from_role.level < to_role.level)

    # If a level is specified, the from_user's level must be less than or equal to it
    if level is not None:
        conditions.append(from_role.level < level)

    query = query.filter(and_(*conditions))

    result = await db.execute(select(exists(query)))
    return bool(result.scalar_one_or_none())


###########################################################################
################################ Sonstiges ################################
###########################################################################
async def get_user_with_roles(db: AsyncSession, user_id: uuid.UUID) -> m_user.User:
    """
    Get the roles for a user with each description.

    :param db: AsyncSession: Database session
    :param user_id: UUID: ID of the user to search for
    :return: tuple: (generic_roles, club_roles)
    """
    query_options = [
        joinedload(m_user.User.generic_roles).options(undefer(m_user.GenericRole.description)),
        joinedload(m_user.User.club_roles)
        .joinedload(m_club.UserClubRole.club_role)
        .options(undefer(m_club.ClubRole.description)),
        joinedload(m_user.User.club_roles)
        .joinedload(m_club.UserClubRole.club_role)
        .joinedload(m_club.ClubRole.permissions)
        .options(undefer(m_club.Permission.description)),
    ]

    res = await db.execute(select(m_user.User).filter(m_user.User.id == user_id).options(*query_options))
    user = res.unique().scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    return user
