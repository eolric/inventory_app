from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from app.models.item import Item
from app.schemas.items import ItemBase, ItemResponse, ItemUpdate
from app.services.item_service import ItemService
from app.core.database import get_db

router = APIRouter(
    prefix="/api/v1/items",
    tags=["items"]
)

@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    request: Request,
    codigo: str = Form(...),
    nombre: str = Form(...),
    cantidad: float = Form(...),
    precio_compra: float = Form(...),
    precio_venta: float = Form(...),
    db: Session = Depends(get_db)
):
    item_service = ItemService(db)
    try:
        item_data = ItemBase(
            codigo=codigo,
            nombre=nombre,
            cantidad=cantidad,
            precio_compra=precio_compra,
            precio_venta=precio_venta
        )
        item = await item_service.create_item(item_data)
        request.session['flash'] = {'type': 'success', 'message': 'Ítem creado correctamente'}
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    except HTTPException as e:
        request.session['flash'] = {'type': 'danger', 'message': e.detail}
        return RedirectResponse(url="/items/create", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/", response_model=List[ItemResponse])
async def read_items(
    search: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    item_service = ItemService(db)
    if search:
        return await item_service.search_items(search)
    return await item_service.get_all_items(skip=skip, limit=limit)

# Otras rutas similares para update, delete, etc.