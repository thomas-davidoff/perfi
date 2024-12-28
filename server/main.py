from typing import Union
from fastapi import FastAPI
from functools import lru_cache
from pydantic import BaseModel

app = FastAPI()

from config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings.load_settings()


api_settings = get_settings()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}
