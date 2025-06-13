from fastapi import FastAPI, HTTPException, Depends
from app.services.item_service import ItemService
from app.schemas import ItemBase, ItemResponse, ItemUpdate
from typing import List

app = FastAPI()
item_service = ItemService()

@app.post("/items/", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemBase):
    return await item_service.create_item(item)

@app.get("/items/", response_model=List[ItemResponse])
async def read_items():
    return await item_service.get_all_items()

@app.get("/items/search/", response_model=List[ItemResponse])
async def search_items(search_term: str):
    return await item_service.search_items(search_term)

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(item_id: int, item: ItemUpdate):
    return await item_service.update_item(item_id, item)

@app.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int):
    await item_service.delete_item(item_id)
    return  # No content (204)
