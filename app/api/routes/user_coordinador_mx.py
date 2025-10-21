# routers/user_coordinador_mx.py
from fastapi import APIRouter, Depends, HTTPException, Form, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.db.database import get_db
from app.db.models.user_coordinador_mx import UserCoordinadorMX
from app.schemas.user_coordinador_mx import UserCoordinadorMXCreate, UserCoordinadorMXUpdate, UserCoordinadorMXResponse
from app.services.user_coordinador import SECRET_CODE
from app.core.security import create_access_token, verify_password, SECRET_KEY, ALGORITHM

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------
# Función para obtener el coordinador MX actual
# ---------------------------
def get_current_coordinator_mx(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        username = payload.get("sub")
        tipo = payload.get("tipo")
        if not user_id or not username or tipo != "coordinador":
            raise HTTPException(status_code=401, detail="Token inválido o expirado")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    user = db.query(UserCoordinadorMX).filter(UserCoordinadorMX.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ---------------------------
# Endpoints Coordinador MX
# ---------------------------

# Crear coordinador MX
@router.post("/", response_model=UserCoordinadorMXResponse)
def create_coordinador_mx(payload: UserCoordinadorMXCreate, db: Session = Depends(get_db)):
    if payload.codigo_secreto != SECRET_CODE:
        raise HTTPException(status_code=403, detail="Código secreto incorrecto")
    
    hashed_password = pwd_context.hash(payload.contrasena)
    user = UserCoordinadorMX(
        nombre=payload.nombre,
        contrasena=hashed_password,
        codigo_secreto=payload.codigo_secreto
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Login coordinador MX
@router.post("/login")
def login_coordinador_mx(
    nombre: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(UserCoordinadorMX).filter(UserCoordinadorMX.nombre == nombre).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    if not verify_password(contrasena, user.contrasena):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    token_data = {
        "id": user.id,
        "sub": user.nombre,
        "tipo": "coordinador",
        "sede": "mexico"
    }
    token = create_access_token(token_data)
    
    return {
        "nombre": user.nombre,
        "id": user.id,
        "sede": "mexico",
        "codigo_secreto": user.codigo_secreto,
        "token": token
    }


# Ver perfil
@router.get("/me", response_model=UserCoordinadorMXResponse)
def get_me_mx(current_user: UserCoordinadorMX = Depends(get_current_coordinator_mx)):
    return current_user


# Actualizar perfil
@router.put("/perfil", response_model=UserCoordinadorMXResponse)
def update_perfil_coordinador_mx(
    payload: UserCoordinadorMXUpdate,
    current_user: UserCoordinadorMX = Depends(get_current_coordinator_mx),
    db: Session = Depends(get_db)
):
    if payload.nombre:
        current_user.nombre = payload.nombre
    if payload.contrasena:
        current_user.contrasena = pwd_context.hash(payload.contrasena)
    db.commit()
    db.refresh(current_user)
    return current_user


# Listar todos los coordinadores MX
@router.get("/", response_model=List[UserCoordinadorMXResponse])
def get_all_coordinadores_mx(db: Session = Depends(get_db)):
    return db.query(UserCoordinadorMX).all()


# Eliminar coordinador MX por ID
@router.delete("/{coordinador_id}")
def delete_coordinador_mx(coordinador_id: int, db: Session = Depends(get_db)):
    user = db.query(UserCoordinadorMX).filter(UserCoordinadorMX.id == coordinador_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Coordinador no encontrado")
    db.delete(user)
    db.commit()
    return {"detail": "Coordinador eliminado"}
