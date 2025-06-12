from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import json
import mysql.connector
from mysql.connector import Error

# Cargar configuración
with open('/app/config.json') as config_file:
    config = json.load(config_file)

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo Pydantic para los items
class Item(BaseModel):
    codigo: str
    nombre: str
    cantidad: float
    precio_compra: float
    precio_venta: float

# Conexión a la base de datos
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=config['database']['host'],
            database=config['database']['database'],
            user=config['database']['user'],
            password=config['database']['password']
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.on_event("startup")
async def startup():
    # Crear la tabla si no existe
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    codigo VARCHAR(50) UNIQUE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    cantidad DECIMAL(10,2) NOT NULL,
                    precio_compra DECIMAL(10,2) NOT NULL,
                    precio_venta DECIMAL(10,2) NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

@app.get("/items/", response_model=List[Item])
async def read_items():
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT codigo, nombre, cantidad, precio_compra, precio_venta FROM items")
        items = cursor.fetchall()
        return items
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    connection = get_db_connection()
    if not connection:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO items (codigo, nombre, cantidad, precio_compra, precio_venta)
            VALUES (%s, %s, %s, %s, %s)
        """, (item.codigo, item.nombre, item.cantidad, item.precio_compra, item.precio_venta))
        connection.commit()
        return item
    except Error as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()