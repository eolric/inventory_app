from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9-]+$")
    nombre: str = Field(..., min_length=3, max_length=100)
    cantidad: float = Field(..., gt=0)
    precio_compra: float = Field(..., gt=0)
    precio_venta: float = Field(..., gt=0)

    @field_validator('precio_venta')
    def precio_venta_mayor_que_compra(cls, v, values):
        if 'precio_compra' in values.data and v <= values.data['precio_compra']:
            raise ValueError("El precio de venta debe ser mayor al de compra")
        return v

class ItemResponse(ItemBase):
    id: int
    fecha_creacion: Optional[datetime]  # Cambiado a datetime
    fecha_actualizacion: Optional[datetime]  # Cambiado a datetime