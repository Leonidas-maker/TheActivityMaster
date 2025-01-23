import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import enum
from typing import Dict

from models.m_generic import Country, State, City
from models.m_user import User, GenericRole
from config.settings import SYSTEM_USER_ID


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
            "name": "GlobalInstructor",
            "description": "Can create and manage courses across all clubs but has no control over club-specific roles or memberships.",
        },
        {
            "name": "Student",
            "description": "Can browse and book courses offered by any club and manage their own profile and bookings.",
        },
        {
            "name": "ClubAdmin",
            "description": "Can manage one or more clubs, including approving courses, managing members, and overseeing bookings for those clubs.",
        },
        {
            "name": "ClubEmployee",
            "description": "Can manage bookings, courses, and members for a specific club but cannot create or manage clubs themselves",
        },
        {
            "name": "SupportStaff",
            "description": "Handles customer support for app-related queries and can view and assist with bookings across clubs.",
        },
        {
            "name": "Guest",
            "description": "Limited access to browse courses and view club offerings but cannot make bookings or interact with specific club features.",
        },
    ]

    res = await db.execute(select(GenericRole))
    existing_roles = {role.name: role for role in res.scalars().all()}
    new_roles = []

    for role in generic_roles:
        if not existing_roles.get(role["name"]):
            new_roles.append(GenericRole(**role))

    if new_roles:
        db.add_all(new_roles)


async def create_system_user(db: AsyncSession):
    res = await db.execute(select(User).where(User.id == SYSTEM_USER_ID))

    if not res.scalars().first():
        user = User(
            id=SYSTEM_USER_ID,
            first_name="System",
            last_name="User",
            email="system@localhost",
            password="SYSTEM",
            is_system=True,
        )
        res = await db.execute(select(GenericRole).where(GenericRole.name == "SystemUser"))
        role = res.scalar_one()
        user.generic_roles.append(role)
        db.add(user)


async def init_users(db: AsyncSession):
    await create_generic_roles(db)
    await db.flush()
    await create_system_user(db)
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
