import mysql.connector
from mysql.connector import Error, pooling
from app.config_manager import ConfigManager
import contextlib
from typing import Optional

class DatabaseManager:
    _pool = None
    
    @classmethod
    def initialize_pool(cls):
        if cls._pool is None:
            config = ConfigManager().get_database_config()
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="inventario_pool",
                pool_size=5,
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
    
    @contextlib.contextmanager
    def get_connection(self):
        self.initialize_pool()
        conn = self._pool.get_connection()
        try:
            yield conn
        finally:
            conn.close()
    
    @contextlib.contextmanager
    def get_cursor(self, dictionary=True):
        with self.get_connection() as conn:
            cursor = conn.cursor(dictionary=dictionary)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def initialize_database(self):
        """Crea las tablas si no existen según la configuración"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        codigo VARCHAR(50) UNIQUE NOT NULL,
                        nombre VARCHAR(100) NOT NULL,
                        cantidad DECIMAL(10, 2) NOT NULL,
                        precio_compra DECIMAL(10, 2) NOT NULL,
                        precio_venta DECIMAL(10, 2) NOT NULL,
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
                conn.commit()
            except Error as e:
                conn.rollback()
                raise