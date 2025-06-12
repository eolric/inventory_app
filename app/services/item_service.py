from ..database import DatabaseManager
from ..models.item_model import Item
from ..schemas import ItemBase, ItemResponse
from fastapi import HTTPException

class ItemService:
    def __init__(self):
        self.db = DatabaseManager()

    async def create_item(self, item: ItemBase) -> ItemResponse:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                INSERT INTO items (codigo, nombre, cantidad, precio_compra, precio_venta)
                VALUES (%s, %s, %s, %s, %s)
            """, (item.codigo, item.nombre, item.cantidad, item.precio_compra, item.precio_venta))
            connection.commit()
            item_id = cursor.lastrowid
            return await self.get_item(item_id)
        except mysql.connector.Error as e:
            connection.rollback()
            raise HTTPException(status_code=400, detail=f"Error al crear item: {e}")
        finally:
            cursor.close()
            connection.close()

    async def get_item(self, item_id: int) -> ItemResponse:
        # Implementar (similar a create_item)
        pass

    async def update_item(self, item_id: int, item: ItemBase) -> ItemResponse:
        # Implementar
        pass

    async def delete_item(self, item_id: int) -> dict:
        # Implementar
        pass