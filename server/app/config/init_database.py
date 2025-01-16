
import json
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from .database import get_db
from models.m_generic import Country, State, City


async def init_country_states_city(db: AsyncSession):
    data = json.load(open(os.path.join(os.path.dirname(__file__), "../data/country_states_city.json")))
    new_db_data = []

    db_res = await db.execute(select(Country).options(selectinload(Country.states).selectinload(State.cities)))
    countries_db = db_res.scalars().all()

    countries = {country.name: country for country in countries_db}



    states = {f"{state.name}_{country.name}": state for country in countries_db for state in country.states}
    cities = {f"{city.name}_{state.name}": city for country in countries_db for state in country.states for city in state.cities}
    
  
    for country in data:
        if countries.get(country["name"]):
            country_db = countries[country["name"]]
        elif len(country["states"]) > 0:
            country_db = Country(name=country["name"], iso2=country["iso2"], iso3=country["iso3"])
            new_db_data.append(country_db)
            countries[country["name"]] = country_db
        else:
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
    

