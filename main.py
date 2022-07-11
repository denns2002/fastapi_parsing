from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Price(BaseModel):
    name: str
    price: float


PRICES_DB = [
    Price(name='test1', price=1000),
    Price(name='test2', price=200),
    Price(name='test3', price=300),
    Price(name='test4', price=400),
    Price(name='test5', price=500),
]


@app.get("/prices")
def read_prices():
    return PRICES_DB


@app.get("/price/{item_id}")
def read_price(item_id: int):
    return PRICES_DB[item_id]


@app.post("/price/create")
def create_price(item: Price):
    PRICES_DB.append(item)
    return {'status': 'create is ok'}


@app.put("/price/{item_id}")
def update_price(item_id: int, item: Price):
    PRICES_DB[item_id] = item
    return {'status': 'put is ok'}


@app.delete("/price/{item_id}")
def update_price(item_id: int, item: Price):
    del PRICES_DB[item_id]
    return {'status': 'delete is ok'}