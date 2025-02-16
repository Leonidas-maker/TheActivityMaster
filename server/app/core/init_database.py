import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists, or_, and_
from sqlalchemy.orm import selectinload
import enum
from typing import Dict

from models.m_generic import Country, State, City
from models.m_user import User, GenericRole
from models.m_club import ClubRole, Permission, ClubRolePermission
from config.settings import SYSTEM_USER_ID
from config.permissions import ClubPermissions

import core.security as security_core


async def create_generic_roles(db: AsyncSession):
    generic_roles = [
        {
            "name": "SystemUser",
            "description": "Represents the system itself, used for automated processes, background jobs, and system-level actions.",
        },
        {
            "name": "Admin",
            "description": "Has full system-wide access, including managing users, clubs, courses, and bookings across the entire app.",
        },
        {
            "name": "Verifier",
            "description": "Can verify user identity and club information.",
        },
        {
            "name": "Club",
            "description": "Can manage clubs, courses, and bookings within their own club. Depends on the ClubRole for specific permissions.",
        },
        {
            "name": "NotEmailVerified",
            "description": "User has not yet verified their email address.",
        },
    ]

    res = await db.execute(select(GenericRole))
    existing_roles = {role.name: role for role in res.unique().scalars().all()}
    new_roles = []

    for role in generic_roles:
        if not existing_roles.get(role["name"]):
            new_roles.append(GenericRole(**role))

    if new_roles:
        db.add_all(new_roles)


#! Currently only used for club roles - generic roles will be added later
async def create_permissions(db: AsyncSession):
    permissions = [
        {
            "name": ClubPermissions.READ_CLUB_CONFIDANTIAL_DATA.value,
            "description": "Allows reading club confidential data (e.g. financials).",
        },
        {"name": ClubPermissions.READ_CLUB_DATA.value, "description": "Allows reading club data."},
        {"name": ClubPermissions.MODIFY_CLUB_DATA.value, "description": "Allows writing or modifying club data."},
        {"name": ClubPermissions.DELETE_CLUB_DATA.value, "description": "Allows deleting club data."},
        {"name": ClubPermissions.READ_ROLES.value, "description": "Allows reading club roles."},
        {"name": ClubPermissions.MODIFY_ROLES.value, "description": "Allows modifying club roles."},
        {"name": ClubPermissions.DELETE_ROLES.value, "description": "Allows deleting club roles."},
        {"name": ClubPermissions.READ_EMPLOYEES.value, "description": "Allows reading club employees."},
        {"name": ClubPermissions.MODIFY_EMPLOYEES.value, "description": "Allows modifying club employees."},
        {"name": ClubPermissions.DELETE_EMPLOYEES.value, "description": "Allows deleting club employees."},
        {"name": ClubPermissions.READ_PROGRAMS.value, "description": "Allows reading club programs."},
        {"name": ClubPermissions.MODIFY_PROGRAMS.value, "description": "Allows modifying club programs."},
        {"name": ClubPermissions.DELETE_PROGRAMS.value, "description": "Allows deleting club programs."},
        {"name": ClubPermissions.READ_MEMBERSHIPS.value, "description": "Allows reading club memberships."},
        {"name": ClubPermissions.MODIFY_MEMBERSHIPS.value, "description": "Allows modifying club memberships."},
        {"name": ClubPermissions.DELETE_MEMBERSHIPS.value, "description": "Allows deleting club memberships."},
        {"name": ClubPermissions.READ_BOOKINGS.value, "description": "Allows reading club bookings."},
    ]

    if len(permissions) != len(ClubPermissions):
        raise RuntimeError("Number of permissions does not match number of ClubPermissions")

    res = await db.execute(select(Permission))
    existing_permissions = {permission.name: permission for permission in res.unique().scalars().all()}
    new_permissions = []

    for permission in permissions:
        if not existing_permissions.get(permission["name"]):
            new_permissions.append(Permission(**permission))

    if new_permissions:
        db.add_all(new_permissions)

async def create_system_user(db: AsyncSession):
    res = await db.execute(select(User).where(User.id == SYSTEM_USER_ID))

    if not res.scalars().first():
        user = User(
            id=SYSTEM_USER_ID,
            username="system",
            first_name="System",
            last_name="User",
            email="system@localhost",
            password="SYSTEM",
            is_system=True,
        )
        res = await db.execute(select(GenericRole).where(GenericRole.name == "SystemUser"))
        role = res.unique().scalar_one()
        user.generic_roles.append(role)
        db.add(user)


async def create_admin_user(db: AsyncSession):
    res = await db.execute(
        select(exists(select(1).select_from(User).join(User.generic_roles).where(GenericRole.name == "Admin"))
    ))

    if not res.scalars().first():
        user = User(
            username="admin",
            first_name="Admin",
            last_name="User",
            email="admin@localhost.de",
            password=security_core.hash_password("ADMIN_ADMIN"),
        )
        res = await db.execute(select(GenericRole).where(GenericRole.name == "Admin"))
        role = res.unique().scalar_one()
        user.generic_roles.append(role)
        db.add(user)


async def init_users(db: AsyncSession):
    await create_permissions(db)
    await db.flush()
    await create_generic_roles(db)
    await db.flush()
    await create_system_user(db)
    await db.flush()
    await create_admin_user(db)
    await db.commit()


class init_country_states_city_mode(enum.Enum):
    country_state_city = 1
    country_state = 2
    country = 3


async def init_country_states_city(
    db: AsyncSession, mode: init_country_states_city_mode = init_country_states_city_mode.country_state_city
):
    file_path = os.path.join(os.path.dirname(__file__), "../data/country_states_city.json")
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    db_res = await db.execute(select(Country).options(selectinload(Country.states).selectinload(State.cities)))
    countries_db = db_res.scalars().all()

    countries = {country.name: country for country in countries_db}

    states = {}
    cities = {}

    if mode == init_country_states_city_mode.country_state:
        states: Dict[str, State] = {
            f"{state.name}_{country.name}": state for country in countries_db for state in country.states
        }
    if mode == init_country_states_city_mode.country_state_city:
        cities = {
            f"{city.name}_{state.name}": city
            for country in countries_db
            for state in country.states
            for city in state.cities
        }

    new_db_data = []

    for country in data:
        if countries.get(country["name"]):
            country_db = countries[country["name"]]
        elif len(country["states"]) > 0:
            country_db = Country(name=country["name"], iso2=country["iso2"], iso3=country["iso3"])
            new_db_data.append(country_db)
            countries[country["name"]] = country_db
        else:
            continue

        if mode == init_country_states_city_mode.country:
            continue

        for state in country["states"]:
            state_key = f"{state['name']}_{country['name']}"
            if states.get(state_key):
                state_db = states[state_key]
            elif len(state["cities"]) > 0:
                state_db = State(name=state["name"], country=country_db)
                new_db_data.append(state_db)
                states[state_key] = state_db
            else:
                continue

            if mode == init_country_states_city_mode.country_state:
                continue

            for city in state["cities"]:
                city_key = f"{city['name']}_{state['name']}"
                if cities.get(city_key):
                    city_db = cities[city_key]
                else:
                    city_db = City(name=city["name"], state=state_db)
                    new_db_data.append(city_db)
                    cities[city_key] = city_db

    if new_db_data:
        db.add_all(new_db_data)
        await db.commit()
