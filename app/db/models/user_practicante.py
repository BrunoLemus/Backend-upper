# app/db/models/user_practicante.py
import enum
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from app.db.database import Base
from app.db.models.enums import mesaTrabajoEnum

# 🔹 Contexto para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔹 Modelo UserPracticante
class UserPracticante(Base):
    __tablename__ = "user_practicantes"

    # 🔹 Campos principales
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    contrasena = Column(String(100), nullable=False)  # almacenar hash
    mesa_trabajo = Column(Enum(mesaTrabajoEnum, native_enum=False), nullable=False)

    # 🔹 Relaciones
    cajas = relationship("Caja", back_populates="practicante")
    tarimas = relationship("Tarima", back_populates="practicante")

  