from datetime import datetime
from sqlalchemy.orm import Session

import models, schemas


def get_cities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.City).offset(skip).limit(limit).all()


def get_city(db: Session, type, sort):
    if isinstance(type, str):
        if type == 'ru':
            return db.query(models.City).filter(models.City.ru == sort.title()).first()
        if type == 'en':
            return db.query(models.City).filter(models.City.en == sort.title()).first()
        if type == 'id':
            return db.query(models.City).filter(models.City.id == sort).first()
    else:
        return {
            'status': 'bad filter'
        }


def create_city(db: Session, city: schemas.CityBase):
    db_city = models.City(
        ru=city.ru.title(),
        en=city.en.title(),
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


def delete_city(db: Session, city_id: int):
    item = db.query(models.City).filter(
        models.City.id == city_id
    ).delete()
    db.commit()


def update_city(db: Session, city: schemas.CityBase, id: int):
    item = db.query(models.City).filter(models.City.id == id).first()
    item.ru = city.ru.title()
    item.en = city.en.title()
    db.add(item)
    db.commit()
    db.refresh(item)
    return {
        'status': 'update!'
    }


def add_to_db(db: Session, weather: schemas.WeatherCreate, lst, city_id: int):
    weather_day = lst[0]
    weather_night = lst[1]
    precipitation = lst[2]
    humidity = lst[3]
    wind = lst[4]
    pressure = lst[5]
    db_city = models.Weather(
        datetime=datetime.now(),
        city=city_id,
        weather_day=weather_day,
        weather_night=weather_night,
        precipitation=precipitation,
        humidity=humidity,
        wind=wind,
        pressure=pressure,
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
