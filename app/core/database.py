from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.config_manager import ConfigManager

config = ConfigManager().get_database_config()

SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{config['user']}:{config['password']}@"
    f"{config['host']}:{config['port']}/{config['database']}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta es la definición clave que debe exportarse
Base = declarative_base()

def get_db():
    """Proveedor de dependencia para sesiones de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()