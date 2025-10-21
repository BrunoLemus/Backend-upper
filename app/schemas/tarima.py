# app/schemas/tarima_schemas.py
from pydantic import BaseModel
from typing import Optional
from app.db.models.tarima import TipoEmbalajeEnum
from app.db.models.enums import PaqueteriaEnum
from datetime import datetime

class TarimaBase(BaseModel):
    nombre_user_practicante: Optional[str] = None
    nombre_user_coordinador: Optional[str] = None
    numero_facturas: str
    numero_tarimas: int
    tipo_embalaje: TipoEmbalajeEnum
    paqueteria: PaqueteriaEnum
    clave_producto: str
    cantidad_piezas: Optional[int] = 0
    ancho: Optional[float] = 0
    largo: Optional[float] = 0
    alto: Optional[float] = 0
    peso: Optional[float] = 0
    peso_volumetrico: Optional[float] = 0

class TarimaCreate(TarimaBase):
    practicante_id: Optional[int] = None
    coordinador_id: Optional[int] = None
    
class TarimaRead(TarimaBase):
    id: int
    fecha_hora: datetime
    practicante_id: Optional[int] = None
    coordinador_id: Optional[int] = None

    class Config:
        from_attributes = True