from fastapi import APIRouter, Depends, HTTPException, Request, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.item import Item
from app.schemas.items import ItemBase, ItemResponse, ItemUpdate
from app.services.item_service import ItemService
from app.core.database import get_db
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/items/", response_model=ItemResponse)
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
        await item_service.create_item(item_data)
        request.session["flash"] = {"type": "success", "message": "Ítem creado correctamente"}
        return RedirectResponse(url="/", status_code=303)
    except HTTPException as e:
        request.session["flash"] = {"type": "danger", "message": e.detail}
        return RedirectResponse(url="/items/create", status_code=303)

@router.get("/items/", response_model=List[ItemResponse])
async def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    item_service = ItemService(db)
    return await item_service.get_all_items(skip=skip, limit=limit)

@router.get("/items/search", response_class=HTMLResponse)
async def search_items(
    request: Request,
    q: Optional[str] = Query(None, min_length=1),
    db: Session = Depends(get_db)
):
    item_service = ItemService(db)
    items = []
    
    if q:
        items = await item_service.search_items(q)
    
    return templates.TemplateResponse(
        "items/search.html",
        {
            "request": request,
            "items": items,
            "search_term": q,
            "title": "Resultados de Búsqueda",
            "back_url": "/"
        }
    )

@router.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    request: Request,
    item_id: int,
    codigo: str = Form(None),
    nombre: str = Form(None),
    cantidad: float = Form(None),
    precio_compra: float = Form(None),
    precio_venta: float = Form(None),
    db: Session = Depends(get_db)
):
    item_service = ItemService(db)
    try:
        item_update = ItemUpdate(
            codigo=codigo,
            nombre=nombre,
            cantidad=cantidad,
            precio_compra=precio_compra,
            precio_venta=precio_venta
        )
        await item_service.update_item(item_id, item_update)
        request.session["flash"] = {"type": "success", "message": "Ítem actualizado correctamente"}
        return RedirectResponse(url="/", status_code=303)
    except HTTPException as e:
        request.session["flash"] = {"type": "danger", "message": e.detail}
        return RedirectResponse(url=f"/items/edit/{item_id}", status_code=303)

@router.post("/api/items/{item_id}")
async def delete_item_form(
    request: Request,
    item_id: int,
    db: Session = Depends(get_db)
):
    item_service = ItemService(db)
    try:
        await item_service.delete_item(item_id)
        request.session["flash"] = {"type": "success", "message": "Ítem eliminado correctamente"}
    except HTTPException as e:
        request.session["flash"] = {"type": "danger", "message": e.detail}
    return RedirectResponse(url="/", status_code=303)

@router.post("/items/{item_id}")
async def update_item_form(
    request: Request,
    item_id: int,
    codigo: str = Form(None),
    nombre: str = Form(None),
    cantidad: float = Form(None),
    precio_compra: float = Form(None),
    precio_venta: float = Form(None),
    db: Session = Depends(get_db)
):
    item_service = ItemService(db)
    try:
        item_update = ItemUpdate(
            codigo=codigo,
            nombre=nombre,
            cantidad=cantidad,
            precio_compra=precio_compra,
            precio_venta=precio_venta
        )
        await item_service.update_item(item_id, item_update)
        request.session["flash"] = {"type": "success", "message": "Ítem actualizado correctamente"}
        return RedirectResponse(url="/", status_code=303)
    except HTTPException as e:
        request.session["flash"] = {"type": "danger", "message": e.detail}
        return RedirectResponse(url=f"/items/edit/{item_id}", status_code=303)