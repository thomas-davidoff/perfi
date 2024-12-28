from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from config import get_settings, get_db
import uvicorn


app = FastAPI()


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


if __name__ == "__main__":
    api_settings = get_settings()
    uvicorn.run(
        "main:app",
        host=api_settings.APP_HOST,
        port=int(api_settings.APP_PORT),
        reload=True,
    )
