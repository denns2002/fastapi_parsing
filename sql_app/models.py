from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Numeric
from sqlalchemy.orm import relationship

from database import Base


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    city = Column(Integer, ForeignKey('city.id'))
    weather_day = Column(Numeric(10))
    weather_night = Column(Numeric(10))
    precipitation = Column(Numeric(10))
    humidity = Column(Numeric(10))
    wind = Column(Numeric(10))
    pressure = Column(Numeric(10))

    def __repr__(self):
        return f'{self.datetime} | {self.city} | {self.weather_day} | {self.weather_night} | '  \
               f'{self.precipitation} | {self.humidity} | {self.wind} | {self.pressure}'


class City(Base):
    __tablename__ = 'city'

    id = Column(Integer, primary_key=True)
    ru = Column(String)
    en = Column(String)

    def __repr__(self):
        return f'{self.id} | {self.ru} | {self.en}'
