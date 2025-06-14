from app.database import DatabaseManager
from app.schemas import ItemBase, ItemResponse, ItemUpdate
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
                FROM items
                WHERE id = %s
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

    async def search_items(self, search_term: str) -> list[ItemResponse]:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            search_pattern = f"%{search_term}%"
            cursor.execute("""
                SELECT id, codigo, nombre, cantidad, precio_compra, precio_venta,
                    fecha_creacion, fecha_actualizacion
                FROM items
                WHERE codigo LIKE %s OR nombre LIKE %s
                ORDER BY nombre
            """, (search_pattern, search_pattern))
            items = cursor.fetchall()
            if not items:
                raise HTTPException(
                    status_code=404,
                    detail="No se encontraron items con ese término de búsqueda"
                )
            return items
        except mysql.connector.Error as e:
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()

    async def search_items_with_ids(self, search_term: str) -> list[dict]:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            search_pattern = f"%{search_term}%"
            cursor.execute("""
                SELECT id, codigo, nombre 
                FROM items
                WHERE codigo LIKE %s OR nombre LIKE %s
                ORDER BY nombre
            """, (search_pattern, search_pattern))
            items = cursor.fetchall()
            if not items:
                raise HTTPException(
                    status_code=404,
                    detail="No se encontraron items con ese término de búsqueda"
                )
            return items
        except mysql.connector.Error as e:
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()

    async def update_item(self, item_id: int, item_update: ItemUpdate) -> ItemResponse:
        connection = self.db.connect()
        cursor = connection.cursor(dictionary=True)
        try:
            # Primero obtenemos el item actual
            cursor.execute("""
                SELECT codigo, nombre, cantidad, precio_compra, precio_venta
                FROM items WHERE id = %s
            """, (item_id,))
            current_item = cursor.fetchone()
            if not current_item:
                raise HTTPException(status_code=404, detail="Item no encontrado")

            # Combinamos los valores actuales con las actualizaciones
            updated_values = {
                'codigo': item_update.codigo if item_update.codigo is not None else current_item['codigo'],
                'nombre': item_update.nombre if item_update.nombre is not None else current_item['nombre'],
                'cantidad': item_update.cantidad if item_update.cantidad is not None else current_item['cantidad'],
                'precio_compra': item_update.precio_compra if item_update.precio_compra is not None else current_item['precio_compra'],
                'precio_venta': item_update.precio_venta if item_update.precio_venta is not None else current_item['precio_venta'],
            }

            # Validación adicional para precio_venta > precio_compra
            if updated_values['precio_venta'] <= updated_values['precio_compra']:
                raise HTTPException(
                    status_code=400,
                    detail="El precio de venta debe ser mayor al de compra"
                )

            cursor.execute("""
                UPDATE items 
                SET codigo = %s, nombre = %s, cantidad = %s, 
                    precio_compra = %s, precio_venta = %s
                WHERE id = %s
            """, (
                updated_values['codigo'],
                updated_values['nombre'],
                updated_values['cantidad'],
                updated_values['precio_compra'],
                updated_values['precio_venta'],
                item_id
            ))
            
            connection.commit()
            return await self.get_item(item_id)
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
            items = cursor.fetchall()
            return items
        except mysql.connector.Error as e:
            raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
        finally:
            cursor.close()
            connection.close()