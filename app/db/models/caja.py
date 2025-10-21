from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.models.enums import PaqueteriaEnum, TipoEmbalajeEnum


class Caja(Base):
    __tablename__ = "cajas"

    id = Column(Integer, primary_key=True, index=True)

    # Relaciones con usuarios
    coordinador_id = Column(Integer, ForeignKey("user_coordinadores.id"), nullable=True)
    practicante_id = Column(Integer, ForeignKey("user_practicantes.id"), nullable=True)

    # Campos solicitados
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

    # Fecha y hora de creación/registro
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones ORM
    coordinador = relationship("UserCoordinador", back_populates="cajas")
    practicante = relationship("UserPracticante", back_populates="cajas")
