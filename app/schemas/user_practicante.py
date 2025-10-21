# app/db/schemas/user_practicante.py
from pydantic import BaseModel, Field
from app.db.models.enums import mesaTrabajoEnum

# 🔹 Base común para todos los esquemas
class UserPracticanteBase(BaseModel):
    nombre: str
    mesa_trabajo: mesaTrabajoEnum  # ahora obligatorio para crear y opcional para actualizar

# 🔹 Esquema para crear usuario (incluye contraseña)
class UserPracticanteCreate(UserPracticanteBase):
    contrasena: str = Field(..., min_length=6)  # obligatoria al crear
    
# 🔹 Esquema para actualizar usuario (opcional)
class UserPracticanteUpdate(BaseModel):
    nombre: str | None = None
    mesa_trabajo: mesaTrabajoEnum 
    contrasena: str | None = Field(None, min_length=6)

# 🔹 Esquema interno que incluye ID y contraseña (para la DB)
class UserPracticanteInDB(UserPracticanteBase):
    id: int
    contrasena: str  # hash de la contraseña

    class Config:
        from_attributes = True

# 🔹 Esquema de respuesta al cliente (sin contraseña)
class UserPracticanteResponse(BaseModel):
    id: int
    nombre: str
    mesa_trabajo: mesaTrabajoEnum

    class Config:
        from_attributes = True
