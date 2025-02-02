from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from models import m_generic
from schemas import s_generic


async def get_create_address(db: AsyncSession, new_address: s_generic.Address) -> m_generic.Address:
    """Get or create an address sqlalchemy object

    :param db: The database session
    :param new_address: The new address pydantic object
    :raises ValueError: If the country is not found
    :return: The address sqlalchemy object
    """
    res = await db.execute(
        select(m_generic.Address)
        .join(m_generic.PostalCode)
        .join(m_generic.City)
        .join(m_generic.State)
        .join(m_generic.Country)
        .filter(
            m_generic.Address.street == new_address.street,
            m_generic.PostalCode.code == new_address.postal_code,
            m_generic.City.name == new_address.city,
            m_generic.State.name == new_address.state,
            m_generic.Country.name == new_address.country,
        )
    )
    address = res.unique().scalar_one_or_none()

    if address:
        return address

    res = await db.execute(
        select(m_generic.PostalCode)
        .join(m_generic.City)
        .join(m_generic.State)
        .join(m_generic.Country)
        .filter(
            m_generic.PostalCode.code == new_address.postal_code,
            m_generic.City.name == new_address.city,
            m_generic.State.name == new_address.state,
            m_generic.Country.name == new_address.country,
        )
    )
    postal_code = res.unique().scalar_one_or_none()

    if not postal_code:
        res = await db.execute(
            select(m_generic.City)
            .join(m_generic.State)
            .join(m_generic.Country)
            .filter(
                m_generic.City.name == new_address.city,
                m_generic.State.name == new_address.state,
                m_generic.Country.name == new_address.country,
            )
        )
        city = res.unique().scalar_one_or_none()

        if not city:
            res = await db.execute(
                select(m_generic.State)
                .join(m_generic.Country)
                .filter(m_generic.State.name == new_address.state, m_generic.Country.name == new_address.country)
            )
            state = res.unique().scalar_one_or_none()

            if not state:
                res = await db.execute(
                    select(m_generic.Country).where(m_generic.Country.name == new_address.country)
                )
                country = res.unique().scalar_one_or_none()

                if not country:
                    raise ValueError("Country not found")

                state = m_generic.State(name=new_address.state, country=country)
                db.add(state)

            city = m_generic.City(name=new_address.city, state=state)
            db.add(city)

        postal_code = m_generic.PostalCode(code=new_address.postal_code, city=city)
        db.add(postal_code)

    address = m_generic.Address(street=new_address.street, postal_code=postal_code)

    db.add(address)
    return address

async def delete_address(db: AsyncSession, address_id: int) -> bool:
    """Delete an address

    :param db: The database session
    :param address_id: The address ID
    :return: True if the address was deleted, False otherwise
    """
    res = await db.execute(delete(m_generic.Address).where(m_generic.Address.id == address_id))
    if not res.rowcount:
        return False
    return True