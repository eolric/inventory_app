from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import secrets
from pathlib import Path
from app.core.database import engine, Base, get_db
from app.api.v1.routers.items import router as items_router
from app.services.item_service import ItemService

app = FastAPI(
    title="Sistema de Inventario",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuración de sesión
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    session_cookie="inventario_session",
    max_age=3600
)

# Configuración de archivos estáticos y templates
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Inicialización de la base de datos
@app.on_event("startup")
async def startup_db():
    from app.models.item import Item  # noqa: F401
    Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(items_router, prefix="")

# Rutas para el frontend
@app.get("/")
async def list_items(request: Request, db: Session = Depends(get_db)):
    item_service = ItemService(db)
    items = await item_service.get_all_items()
    return templates.TemplateResponse("items/list.html", {
        "request": request, 
        "title": "Listar Items",
        "items": items
    })

@app.get("/items/create")
async def create_item_form(request: Request):
    return templates.TemplateResponse("items/create.html", {
        "request": request,
        "title": "Crear Nuevo Ítem",
        "back_url": "/"
    })

@app.get("/items/edit/{item_id}")
async def edit_item_form(request: Request, item_id: int, db: Session = Depends(get_db)):
    item_service = ItemService(db)
    try:
        item = await item_service.get_item(item_id)
        return templates.TemplateResponse("items/edit.html", {
            "request": request,
            "item": item,
            "title": "Editar Ítem",
            "back_url": "/"
        })
    except HTTPException as e:
        request.session["flash"] = {"type": "danger", "message": e.detail}
        return RedirectResponse(url="/", status_code=303)

@app.get("/items/search")
async def search_items_form(request: Request, q: str = None):
    return templates.TemplateResponse("items/search.html", {
        "request": request,
        "title": "Buscar Ítems", 
        "back_url": "/",
        "search_term": q
    })