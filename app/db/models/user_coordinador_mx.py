from passlib.context import CryptContext


from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from app.db.database import Base


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCoordinadorMX(Base):
    __tablename__ = "user_coordinadores_mx"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    contrasena = Column(String(100), nullable=False)
    codigo_secreto = Column(String(100), nullable=False)
    
    # Relaciones
    cajas_mx = relationship("CajaMX", back_populates="coordinador")        
    tarimas_mx = relationship("TarimaMX", back_populates="coordinador")

