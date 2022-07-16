from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from database import SessionLocal, engine

import crud, models, schemas, weather_parsing

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=500,
        content={"message": 'IT WORKED!' + str(exc)},
    )


@app.get("/cities/", response_model=list[schemas.CityBase])
def all_read_cities(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cities = crud.get_cities(db, skip=skip, limit=limit)
    return cities


@app.post("/cities/", response_model=schemas.CityBase)
def add_city(city: schemas.CityBase, db: Session = Depends(get_db)):
    '''
    Добавить город в базу City
    '''
    db_city = crud.get_city(db, type='en', sort=city.en)
    id = db_city
    if db_city and db_city.en == city.en.title():
        raise HTTPException(status_code=400, detail="Has")
    return crud.create_city(db=db, city=city)


@app.get("/cities/{type}/{sort}", response_model=schemas.CityBase)
def get_city(type, sort,  db: Session = Depends(get_db)):
    '''
    Сортировка по столбцу данных: \n
    type: ru / en / id \n
    sort: Москва / Moscow / 1
    '''
    db_city = crud.get_city(db, type=type, sort=sort)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@app.delete("/cities/{type}/{sort}", response_model=schemas.City)
def delete_city(type, sort, db: Session = Depends(get_db)):
    '''
    Удалить данные о городе, сортируя по столбцам \n
    type: ru / en / id \n
    sort: Москва / Moscow / 1
    '''
    db_city = crud.get_city(db, type=type, sort=sort)
    id = db_city.id
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    crud.delete_city(db, id)
    return {
        'status': 'update!'
    }


@app.put("/cities/{type}/{sort}", response_model=schemas.City)
def update_city(type, sort, db: Session = Depends(get_db)):
    '''
    Обновить данные о городе, сортируя по столбцам \n
    type: ru / en / id \n
    sort: Москва / Moscow / 1
    '''
    city = schemas.CityBase
    db_city = crud.get_city(db, type=type, sort=sort)
    id = db_city.id
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    res = crud.update_city(db=db, city=city, id=id)
    return res


@app.post("/cities/weather/", response_model=schemas.WeatherCreate)
def weather_today(weather: schemas.WeatherCreate,
                  db: Session = Depends(get_db,),
                  skip: int = 0, limit: int = 100):
    '''
    Парсит города и заносит в бд: \n
    температуру днем и ночью \n
    вероятность осадков \n
    влажность \n
    скорость ветра \n
    давление
    '''

    headers = {
        "user-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0"
    }

    cities = crud.get_cities(db, skip=skip, limit=limit)

    urls = {
        'yandex': 'https://yandex.ru/pogoda/',
        'google': 'https://www.google.com/search?q=weather+',
        'gismeteo': 'https://www.gismeteo.ru/search/',
    }

    for city in cities:
        # lst_yandex = weather_parsing.yandex(city.en, urls)
        lst_google = weather_parsing.google(city.en, headers, urls)
        lst_gismeteo = weather_parsing.gismeteo(city.en, headers, urls)
        res = [0 for _ in range(6)]

        if all([lst_google, lst_gismeteo]):
            for g, gm, result in zip(lst_google, lst_gismeteo, res):
                el = 0
                n = 0
                # if y is not None:
                #     el += y
                #     n += 1
                if g is not None:
                    el += g
                    n += 1
                if gm is not None:
                    el += gm
                    n += 1

                res[res.index(result)] = round(el / n)
            crud.add_to_db(db=db, weather=weather, lst=res, city_id=city.id)
        else:
            print('Какие-то из сервисов не отвечают!')
            raise HTTPException(detail="nope")

    return {
        'status': 'ok'
    }
