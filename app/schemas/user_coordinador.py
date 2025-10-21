from pydantic import BaseModel

class UserCoordinadorBase(BaseModel):
    nombre: str
    codigo_secreto: str

class UserCoordinadorCreate(UserCoordinadorBase):
    
    contrasena: str


class UserCoordinadorLogin(BaseModel):
    nombre: str
    contrasena: str
    
class UserCoordinadorUpdate(BaseModel):
    nombre: str | None = None
    contrasena: str | None = None
    codigo_secreto: str
    
     
class UserCoordinadorResponse(UserCoordinadorBase):
    id: int
    nombre: str
    token: str | None = None

    model_config = {
        "from_attributes": True
    }
