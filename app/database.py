import mysql.connector
from mysql.connector import Error
from app.config_manager import ConfigManager
import time

class DatabaseManager:
    def __init__(self):
        self.config = ConfigManager()
        self.connection = None
    
    def connect(self, max_retries=5, delay=5):
        for attempt in range(max_retries):
            try:
                db_config = self.config.get_database_config()
                self.connection = mysql.connector.connect(
                    host=db_config['host'],
                    port=db_config['port'],
                    user=db_config['user'],
                    password=db_config['password'],
                    database=db_config['database']
                )
                print("✅ Conexión a MySQL exitosa")
                return self.connection
            except Error as e:
                print(f"⚠️ Intento {attempt + 1}/{max_retries}: Error al conectar a MySQL - {e}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
        return None
    
    def initialize_database(self):
        """Crea las tablas si no existen según la configuración"""
        try:
            cursor = self.connection.cursor()
            
            # Verificar si la base de datos existe, si no, crearla
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.get_database_config()['database']}")
            
            for table_name, table_config in self.config.config['tables'].items():
                columns = []
                for col_name, col_config in table_config['columns'].items():
                    col_def = f"{col_name} {col_config['type']}"
                    
                    if col_config.get('primary_key', False):
                        col_def += " PRIMARY KEY"
                    if col_config.get('auto_increment', False):
                        col_def += " AUTO_INCREMENT"
                    if col_config.get('unique', False):
                        col_def += " UNIQUE"
                    if not col_config.get('nullable', True):
                        col_def += " NOT NULL"
                    if 'default' in col_config:
                        col_def += f" DEFAULT {col_config['default']}"
                    
                    columns.append(col_def)
                
                create_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {', '.join(columns)}
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
                
                cursor.execute(create_table_sql)
                print(f"✅ Tabla {table_name} verificada/creada")
            
            self.connection.commit()
            cursor.close()
            
        except Error as e:
            print(f"❌ Error al inicializar la base de datos: {e}")
            if self.connection:
                self.connection.rollback()
            raise
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Conexión a MySQL cerrada")