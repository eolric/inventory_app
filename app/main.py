from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import DatabaseManager
from app.services.item_service import ItemService
from app.schemas import ItemBase, ItemResponse, ItemUpdate
from typing import List


app = FastAPI()

# Configuración para servir archivos estáticos y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Inicialización de la base de datos al arrancar
@app.on_event("startup")
async def startup_db():
    max_retries = 5
    delay = 5
    db_manager = DatabaseManager()
    
    for attempt in range(max_retries):
        try:
            connection = db_manager.connect()
            if connection:
                db_manager.initialize_database()
                db_manager.close()
                print("✅ Base de datos inicializada correctamente")
                return
        except Exception as e:
            print(f"⚠️ Intento {attempt + 1}/{max_retries}: Error al inicializar DB - {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    
    print("❌ No se pudo inicializar la base de datos después de varios intentos")

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

# Nuevas rutas para el frontend
@app.get("/")
async def list_items(request: Request):
    items = await item_service.get_all_items()
    return templates.TemplateResponse("items/list.html", {"request": request, "items": items})

@app.get("/items/create")
async def create_item_form(request: Request):
    return templates.TemplateResponse("items/create.html", {"request": request})

@app.get("/items/search")
async def search_items_form(request: Request, q: str = None):
    if q:
        items = await item_service.search_items(q)
        return templates.TemplateResponse("items/search.html", {"request": request, "items": items, "search_term": q})
    return templates.TemplateResponse("items/search.html", {"request": request})