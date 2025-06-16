from fastapi import FastAPI, HTTPException, Depends, Request, status, Form
from typing import Annotated
from pydantic import Field
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
import secrets
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import DatabaseManager
from app.services.item_service import ItemService
from app.schemas import ItemBase, ItemResponse, ItemUpdate
from typing import List


app = FastAPI()

# Configuración el SessionMiddleware (debe estar antes de tus rutas)
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),  # Clave secreta para firmar las cookies
    session_cookie="inventario_session",
    max_age=3600  # 1 hora en segundos
)
# # Para producción
# app.add_middleware(
#     SessionMiddleware,
#     secret_key=os.getenv("SECRET_KEY"),  # Usa una variable de entorno
#     session_cookie="inventario_session",
#     https_only=True,  # Solo envía cookies sobre HTTPS
#     same_site="lax"
# )

# # Middleware para redirigir a HTTPS
# app.add_middleware(HTTPSRedirectMiddleware)

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

# @app.post("/items/", response_model=ItemResponse, status_code=201)
# async def create_item(item: ItemBase):
#     return await item_service.create_item(item)

@app.post("/items/", response_model=ItemResponse, status_code=201)
async def create_item(request: Request, 
                      codigo: Annotated[str, Form(..., min_length=3, max_length=50)],
                      nombre: Annotated[str, Form(..., min_length=3, max_length=50)],
                      cantidad: Annotated[float, Form(..., gt=0)],
                      precio_compra: Annotated[float, Form(..., gt=0)],
                      precio_venta: Annotated[float, Form(..., gt=0)],
):
    try:
        item_data = {
           "codigo": codigo,
            "nombre": nombre,
            "cantidad": cantidad,
            "precio_compra": precio_compra,
            "precio_venta": precio_venta
        }
        created_item = await item_service.create_item(ItemBase(**item_data))
        request.session['flash'] = {'success': 'Ítem creado correctamente'}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException as e:
        request.session['flash'] = {'danger': e.detail}
        return RedirectResponse(url="/items/create", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/items/", response_model=List[ItemResponse])
async def read_items():
    return await item_service.get_all_items()

@app.get("/items/search/", response_model=List[ItemResponse])
async def search_items(search_term: str):
    return await item_service.search_items(search_term)

# @app.put("/items/{item_id}", response_model=ItemResponse)
# async def update_item(item_id: int, item: ItemUpdate):
#     return await item_service.update_item(item_id, item)

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(request: Request, item_id: int, item: ItemUpdate):
    try:
        updated_item = await item_service.update_item(item_id, item)
        request.session['flash'] = {'success': 'Ítem actualizado correctamente'}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException as e:
        request.session['flash'] = {'danger': e.detail}
        return RedirectResponse(url=f"/items/edit/{item_id}", status_code=status.HTTP_303_SEE_OTHER)

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

@app.get("/items/edit/{item_id}")
async def edit_item_form(request: Request, item_id: int):
    try:
        item = await item_service.get_item(item_id)
        return templates.TemplateResponse("items/edit.html", {"request": request, "item": item})
    except HTTPException as e:
        request.session['flash'] = {'danger': e.detail}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/items/{item_id}")
async def update_item_form(request: Request, item_id: int):
    form_data = await request.form()
    try:
        item_update = ItemUpdate(
            codigo=form_data.get("codigo"),
            nombre=form_data.get("nombre"),
            cantidad=float(form_data.get("cantidad")),
            precio_compra=float(form_data.get("precio_compra")),
            precio_venta=float(form_data.get("precio_venta"))
        )
        updated_item = await item_service.update_item(item_id, item_update)
        request.session['flash'] = {'success': 'Ítem actualizado correctamente'}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException as e:
        request.session['flash'] = {'danger': e.detail}
        return RedirectResponse(url=f"/items/edit/{item_id}", status_code=status.HTTP_303_SEE_OTHER)
    
@app.post("/api/items/{item_id}")
async def delete_item_form(request: Request, item_id: int):
    try:
        await item_service.delete_item(item_id)
        request.session['flash'] = {'success': 'Ítem eliminado correctamente'}
    except HTTPException as e:
        request.session['flash'] = {'danger': e.detail}
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)