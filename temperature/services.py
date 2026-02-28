import asyncio
import httpx

from sqlalchemy.orm import Session
from datetime import datetime

from settings import get_settings
from city.crud import db_read_cities
from city.models import City, Temperature
from temperature.schemas import TemperatureDto
from temperature.crud import db_read_temperatures, db_create_temperature

settings = get_settings()


API_URL = f"https://api.openweathermap.org/data/2.5/weather?&appid={settings.api_key}"


client = httpx.AsyncClient(
    timeout=httpx.Timeout(
        connect=2.0,
        read=10.0,
        write=10.0,
        pool=5.0
    ),
    limits=httpx.Limits(
        max_connections=100,
        max_keepalive_connections=20,
        keepalive_expiry=10.0
    )
)


async def fetch(url: str):
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
    except httpx.RequestError as e:
        raise
    except httpx.HTTPStatusError as e:
        raise


sem = asyncio.Semaphore(20)
async def safe_fetch(url):
    async with sem:
        return await fetch(url)


def service_read_temperatures(
    db: Session
) -> list[TemperatureDto | None]:
    return db_read_temperatures(db=db)


async def fetch_temperature_for_city(city_name: str) -> dict:
    url = f"{API_URL}&q={city_name}&units=metric"
    return await safe_fetch(url)


def _save_temperature_for_city(
    city: City,
    temperature_data: dict,
    db: Session
) -> Temperature:
    try:
        timestamp = temperature_data["dt"]
        date = datetime.utcfromtimestamp(timestamp)
        temperature = temperature_data["main"]["temp"]
    except (KeyError, TypeError, ValueError):
        return
    if city.temperature:
        city.temperature.date_time = date
        city.temperature.temperature = temperature
    else:
        new_temperature = db_create_temperature(
            temprature=Temperature(
                city_id=city.id,
                date_time=date,
                temperature=temperature
            ),
            db=db
        )
        city.temperature = new_temperature
    db.commit()
    db.refresh(city.temperature)


async def service_update_temperatures(
    db: Session
) -> dict:
    cities = db_read_cities(db=db)
    
    cities_tempreture = await asyncio.gather(
        *[fetch_temperature_for_city(city.name) for city in cities],
        return_exceptions=True
    )
    
    for city, temperature_data in zip(cities, cities_tempreture):
        if isinstance(temperature_data, Exception):
            continue
        _save_temperature_for_city(
            city=city,
            temperature_data=temperature_data,
            db=db
        )

    return {"message": "Temperatures updated successfully"}
