import json
import os
from typing import Dict, Any

class ConfigManager:
    _instance = None
    
    def __new__(cls, config_path: str = 'config.json'):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance
    
    def _load_config(self, config_path: str):
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            
            # Sobrescribir con variables de entorno si existen
            db_config = self.config['database']
            db_config['host'] = os.getenv('DB_HOST', db_config['host'])
            db_config['port'] = int(os.getenv('DB_PORT', db_config['port']))
            db_config['user'] = os.getenv('DB_USER', db_config['user'])
            db_config['password'] = os.getenv('DB_PASSWORD', db_config['password'])
            db_config['database'] = os.getenv('DB_NAME', db_config['database'])
            
        except FileNotFoundError:
            raise Exception(f"Archivo de configuración {config_path} no encontrado")
        except json.JSONDecodeError:
            raise Exception(f"Error al parsear el archivo de configuración {config_path}")
        except KeyError as e:
            raise Exception(f"Configuración incompleta: falta la clave {str(e)}")
    
    def get_database_config(self) -> Dict[str, Any]:
        return self.config.get('database', {})
    
    def get_table_config(self, table_name: str) -> Dict[str, Any]:
        return self.config.get('tables', {}).get(table_name, {})
    
    def get_table_columns(self, table_name: str) -> Dict[str, Any]:
        table_config = self.get_table_config(table_name)
        return table_config.get('columns', {})