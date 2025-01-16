from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import m_generic
from schemas import s_generic


async def create_address(db: AsyncSession, address: s_generic.Address):

    postal_code = await db.execute(select(m_generic.PostalCode).where(m_generic.PostalCode.code == address.postal_code))
    postal_code = postal_code.scalar_one_or_none()

    if not postal_code:
        city = await db.execute(select(m_generic.City).where(m_generic.City.name == address.city))
        city = city.scalar_one_or_none()

        if not city:
            state = await db.execute(select(m_generic.State).where(m_generic.State.name == address.state))
            state = state.scalar_one_or_none()

            if not state:
                country = await db.execute(select(m_generic.Country).where(m_generic.Country.name == address.country))
                country = country.scalar_one_or_none()

                if not country:
                    country = m_generic.Country(name=address.country)
                    db.add(country)

                state = m_generic.State(name=address.state, country=country)
                db.add(state)

            city = m_generic.City(name=address.city, state=state)
            db.add(city)

        postal_code = m_generic.PostalCode(code=address.postal_code, city=city)
        db.add(postal_code)

    address = m_generic.Address(street=address.street, postal_code=postal_code)
    db.add(address)
    await db.commit()
    return address
