from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import secrets

# Importa engine y Base desde el mismo módulo
from app.core.database import engine, Base
from app.api.v1.routers import items as items_router

app = FastAPI(title="Sistema de Inventario", version="1.0.0")

# Configuración de sesión
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),
    session_cookie="inventario_session",
    max_age=3600
)

# Archivos estáticos y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Inicialización de la base de datos
@app.on_event("startup")
async def startup_db():
    # Asegúrate de que todos los modelos estén importados primero
    from app.models.item import Item  # noqa: F401
    Base.metadata.create_all(bind=engine)

# Incluir routers
app.include_router(items_router.router, prefix="")

# Rutas para el frontend
@app.get("/")
async def list_items(request: Request):
    return templates.TemplateResponse("items/list.html", {"request": request})