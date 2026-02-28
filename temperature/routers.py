from sqlalchemy.orm import Session
from fastapi import APIRouter
from fastapi.params import Depends

from dependencies import get_db
from temperature.schemas import TemperatureDto
from temperature.services import (
    service_read_temperatures,
    service_update_temperatures,
    service_read_temperature
)


temperature_router = APIRouter(
    prefix="/temperatures",
    tags=["temperatures"]
)


@temperature_router.get("/", response_model=list[TemperatureDto | None])
def get_temperatures(
    db: Session = Depends(get_db)
):
    return service_read_temperatures(db=db)


@temperature_router.post("/update/", response_model=dict)
async def update_temperatures(
    db: Session = Depends(get_db)
):
    return await service_update_temperatures(db=db)

@temperature_router.get("/{city_id}/", response_model=TemperatureDto)
def get_temperature(
    city_id: int,
    db: Session = Depends(get_db)
):
    return service_read_temperature(
        city_id=city_id,
        db=db
    )
