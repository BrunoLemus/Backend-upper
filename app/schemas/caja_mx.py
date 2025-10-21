from datetime import datetime
from pydantic import BaseModel
from app.db.models.enums import PaqueteriaEnum, TipoEmbalajeEnum
from typing import Optional


class CajaMXBase(BaseModel):
    nombre_user_practicante: Optional[str] = None
    nombre_user_coordinador: Optional[str] = None
    n_facturas: str
    n_cajas: int
    paqueteria: PaqueteriaEnum
    t_embalaje: TipoEmbalajeEnum
    clave_producto: str
    cantidad_piezas: Optional[int] = None
    ancho: float
    largo: float
    alto: float
    peso: float
    peso_volumetrico: Optional[float] = None


class CajaMXCreate(CajaMXBase):
    practicante_id: Optional[int] = None
    coordinador_id: Optional[int] = None


class CajaMXRead(CajaMXBase):
    id: int
    fecha_hora: datetime
    practicante_id: Optional[int] = None
    coordinador_id: Optional[int] = None

    class Config:
        from_attributes = True
