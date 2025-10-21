# app/db/models/tarima.py
import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.models.enums import PaqueteriaEnum

class TipoEmbalajeEnum(int, enum.Enum):
    TIPO1 = 1
    TIPO2 = 2
    TIPO3 = 3

class Tarima(Base):
    __tablename__ = "tarimas"
    #relaciones con usuarios
    
    id = Column(Integer, primary_key=True, index=True)
     
    coordinador_id = Column(Integer, ForeignKey("user_coordinadores.id"), nullable=True)
    practicante_id = Column(Integer, ForeignKey("user_practicantes.id"), nullable=True)

    # Campos solicitados
    nombre_user_practicante = Column(String(255), nullable=True)
    nombre_user_coordinador = Column(String(255), nullable=True)
    numero_facturas = Column(String(50), nullable=False)
    numero_tarimas = Column(Integer, nullable=False)
    tipo_embalaje = Column(Enum(TipoEmbalajeEnum), nullable=False)
    paqueteria = Column(Enum(PaqueteriaEnum), nullable=False)
    clave_producto = Column(String(50), nullable=False)
    cantidad_piezas = Column(Integer, nullable=True)
    ancho = Column(Float, default=0)
    largo = Column(Float, default=0)
    alto = Column(Float, default=0)
    peso = Column(Float, default=0)
    peso_volumetrico = Column(Float, default=0)
    
    # Fecha y hora de creación/registro
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())
    # Relaciones con usuarios
   

    # Relaciones ORM
    coordinador = relationship("UserCoordinador", back_populates="tarimas")
    practicante = relationship("UserPracticante", back_populates="tarimas")
