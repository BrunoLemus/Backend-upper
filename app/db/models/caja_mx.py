from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.models.enums import PaqueteriaEnum, TipoEmbalajeEnum

class CajaMX(Base):
    __tablename__ = "cajas_mx"

    id = Column(Integer, primary_key=True, index=True)
    coordinador_id = Column(Integer, ForeignKey("user_coordinadores_mx.id"), nullable=True)
    practicante_id = Column(Integer, ForeignKey("user_practicantes_mx.id"), nullable=True)

    nombre_user_practicante = Column(String(255), nullable=True)
    nombre_user_coordinador = Column(String(255), nullable=True)
    n_facturas = Column(String(50), nullable=False)
    n_cajas = Column(Integer, nullable=False)
    paqueteria = Column(Enum(PaqueteriaEnum), nullable=False)
    t_embalaje = Column(Enum(TipoEmbalajeEnum), nullable=False)
    clave_producto = Column(String(50), nullable=False)
    cantidad_piezas = Column(Integer, nullable=True)
    ancho = Column(Float, nullable=True)
    largo = Column(Float, nullable=True)
    alto = Column(Float, nullable=True)
    peso = Column(Float, nullable=True)
    peso_volumetrico = Column(Float, nullable=True)
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones ORM
    coordinador = relationship("UserCoordinadorMX", back_populates="cajas_mx")
    practicante = relationship("UserPracticanteMX", back_populates="cajas_mx")
