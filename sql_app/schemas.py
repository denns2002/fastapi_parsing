from typing import Union

from pydantic import BaseModel


class WeatherBase(BaseModel):
    city: int
    weather_day: int
    weather_night: int
    precipitation: int
    humidity: int
    wind: int
    pressure: int


class WeatherCreate(WeatherBase):
    datetime: str


class Weather(WeatherBase):
    id: int

    class Config:
        orm_mode = True


class CityBase(BaseModel):
    ru: str
    en: str

    class Config:
        orm_mode = True


class City(CityBase):
    id: int

    class Config:
        orm_mode = True
