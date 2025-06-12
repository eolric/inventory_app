from app.database import DatabaseManager
from app.schemas import ItemBase, ItemResponse
from fastapi import HTTPException
import mysql.connector

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
            return await self.get_item(item_id)  # Retorna el item creado con sus fechas automáticas
        except mysql.connector.Error as e:
            connection.rollback()
            if "Duplicate entry" in str(e):
                raise HTTPException(status_code=400, detail="El código del item ya existe")
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()

    async def get_item(self, item_id: int) -> ItemResponse:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, codigo, nombre, cantidad, precio_compra, precio_venta,
                       fecha_creacion, fecha_actualizacion
                FROM items WHERE id = %s
            """, (item_id,))
            item = cursor.fetchone()
            if not item:
                raise HTTPException(status_code=404, detail="Item no encontrado")
            return item
        except mysql.connector.Error as e:
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()

    async def update_item(self, item_id: int, item: ItemBase) -> ItemResponse:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                UPDATE items 
                SET codigo = %s, nombre = %s, cantidad = %s, 
                    precio_compra = %s, precio_venta = %s
                WHERE id = %s
            """, (item.codigo, item.nombre, item.cantidad, 
                  item.precio_compra, item.precio_venta, item_id))
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item no encontrado")
            return await self.get_item(item_id)  # Retorna el item actualizado
        except mysql.connector.Error as e:
            connection.rollback()
            if "Duplicate entry" in str(e):
                raise HTTPException(status_code=400, detail="El código del item ya existe")
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()

    async def delete_item(self, item_id: int) -> dict:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
            connection.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item no encontrado")
            return {"message": "Item eliminado correctamente"}
        except mysql.connector.Error as e:
            connection.rollback()
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()

    async def get_all_items(self) -> list[ItemResponse]:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id, codigo, nombre, cantidad, precio_compra, precio_venta,
                       fecha_creacion, fecha_actualizacion
                FROM items
            """)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()