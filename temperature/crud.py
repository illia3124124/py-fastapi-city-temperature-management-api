from sqlalchemy import select
from sqlalchemy.orm import Session

from city.models import Temperature


def db_read_temperatures(
    db: Session
) -> list[Temperature | None]:
    return db.execute(select(Temperature)).scalars().all()


def db_create_temperature(
    temprature:Temperature,
    db: Session,
) -> Temperature:
    new_temperature = Temperature(
        city_id=temprature.city_id,
        date_time=temprature.date_time,
        temperature=temprature.temperature
    )
    db.add(new_temperature)
    db.commit()
    db.refresh(new_temperature)
    return new_temperature
