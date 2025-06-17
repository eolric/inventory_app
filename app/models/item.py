from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base

class Item(Base):
    """Modelo SQLAlchemy para la tabla items"""
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(50), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    cantidad = Column(DECIMAL(10, 2), nullable=False)
    precio_compra = Column(DECIMAL(10, 2), nullable=False)
    precio_venta = Column(DECIMAL(10, 2), nullable=False)
    fecha_creacion = Column(TIMESTAMP, server_default=func.now())
    fecha_actualizacion = Column(
        TIMESTAMP, 
        server_onupdate=func.now(), 
        server_default=func.now()
    )

    def __repr__(self):
        return f"<Item(id={self.id}, nombre='{self.nombre}')>"