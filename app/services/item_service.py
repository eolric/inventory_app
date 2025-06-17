from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from functools import wraps
from typing import List

from app.models.item import Item
from app.schemas.items import ItemBase, ItemResponse, ItemUpdate

def handle_db_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except IntegrityError as e:
            if "Duplicate entry" in str(e.orig):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El código del item ya existe"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error de integridad en la base de datos"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en la base de datos: {str(e)}"
            )
    return wrapper

class ItemService:
    def __init__(self, db: Session):
        self.db = db
    
    @handle_db_errors
    async def create_item(self, item: ItemBase) -> ItemResponse:
        db_item = Item(**item.model_dump())
        self.db.add(db_item)
        self.db.commit()
        self.db.refresh(db_item)
        return db_item
    
    @handle_db_errors
    async def get_item(self, item_id: int) -> ItemResponse:
        if not (item := self.db.query(Item).filter(Item.id == item_id).first()):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item no encontrado"
            )
        return item
    
    @handle_db_errors
    async def search_items(self, search_term: str) -> List[ItemResponse]:
        return self.db.query(Item).filter(
            (Item.codigo.ilike(f"%{search_term}%")) | 
            (Item.nombre.ilike(f"%{search_term}%"))
        ).order_by(Item.nombre).all()
    
    # Resto de métodos implementados de manera similar...