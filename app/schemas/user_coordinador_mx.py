from pydantic import BaseModel
from typing import Optional

class UserCoordinadorMXBase(BaseModel):
    nombre: str
    codigo_secreto: str

class UserCoordinadorMXCreate(UserCoordinadorMXBase):
    contrasena: str

class UserCoordinadorMXLogin(BaseModel):
    nombre: str
    contrasena: str

class UserCoordinadorMXUpdate(BaseModel):
    nombre: Optional[str] = None
    contrasena: Optional[str] = None
    codigo_secreto: str

class UserCoordinadorMXResponse(UserCoordinadorMXBase):
    id: int
    token: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
