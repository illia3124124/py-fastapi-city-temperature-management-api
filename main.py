from fastapi import FastAPI

from city.routers import city_router
from temperature.routers import tempreture_router

app = FastAPI()

app.include_router(router=city_router)
app.include_router(router=tempreture_router)
