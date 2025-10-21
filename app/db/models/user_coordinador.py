
from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship



class UserCoordinador(Base):
    __tablename__ = "user_coordinadores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    contrasena = Column(String(100), nullable=False)
    codigo_secreto = Column(String(100), nullable=False)
    
    cajas = relationship("Caja", back_populates="coordinador")
    tarimas = relationship("Tarima", back_populates="coordinador")