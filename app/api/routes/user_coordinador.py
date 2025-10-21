# routers/user_coordinador.py
from fastapi import APIRouter, Depends, HTTPException, Form, Header, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.db.database import get_db
from app.db.models.user_coordinador import UserCoordinador
from app.schemas.user_coordinador import UserCoordinadorCreate, UserCoordinadorResponse, UserCoordinadorUpdate
from app.services.user_coordinador import SECRET_CODE
from app.core.security import create_access_token, verify_password, SECRET_KEY, ALGORITHM

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------
# Función para obtener el coordinador actual
# ---------------------------
def get_current_coordinator(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        username = payload.get("sub")
        tipo = payload.get("tipo")
        sede = payload.get("sede")
        if not user_id or not username or tipo != "coordinador" or not sede:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    user = db.query(UserCoordinador).filter(UserCoordinador.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ---------------------------
# Endpoints Coordinador
# ---------------------------

# Crear coordinador
@router.post("/", response_model=UserCoordinadorResponse)
def create_coordinador(payload: UserCoordinadorCreate, db: Session = Depends(get_db)):
    if payload.codigo_secreto != SECRET_CODE:
        raise HTTPException(status_code=403, detail="Código secreto incorrecto")
    
    hashed_password = pwd_context.hash(payload.contrasena)
    user = UserCoordinador(
        nombre=payload.nombre,
        contrasena=hashed_password,
        codigo_secreto=payload.codigo_secreto
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Login coordinador
@router.post("/login")
def login_coordinador(
    nombre: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(UserCoordinador).filter(UserCoordinador.nombre == nombre).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    if not verify_password(contrasena, user.contrasena):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    token_data = {
        "id": user.id,
        "sub": user.nombre,
        "tipo": "coordinador",
        "sede": "guadalajara"
    }
    token = create_access_token(token_data)
    
    return {
        "nombre": user.nombre,
        "id": user.id,
        "sede": "guadalajara",
        "codigo_secreto": user.codigo_secreto,
        "token": token
    }


# Ver perfil
@router.get("/me", response_model=UserCoordinadorResponse)
def get_me(current_user: UserCoordinador = Depends(get_current_coordinator)):
    return current_user


# Actualizar perfil
@router.put("/perfil", response_model=UserCoordinadorResponse)
def update_perfil_coordinador(
    payload: UserCoordinadorUpdate,
    current_user: UserCoordinador = Depends(get_current_coordinator),
    db: Session = Depends(get_db)
):
    if payload.nombre:
        current_user.nombre = payload.nombre
    if payload.contrasena:
        current_user.contrasena = pwd_context.hash(payload.contrasena)
    db.commit()
    db.refresh(current_user)
    return current_user


# Listar todos los coordinadores
@router.get("/", response_model=List[UserCoordinadorResponse])
def get_all_coordinadores(db: Session = Depends(get_db)):
    return db.query(UserCoordinador).all()


# Eliminar coordinador por ID
@router.delete("/{coordinador_id}")
def delete_coordinador(coordinador_id: int, db: Session = Depends(get_db)):
    user = db.query(UserCoordinador).filter(UserCoordinador.id == coordinador_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Coordinador no encontrado")
    db.delete(user)
    db.commit()
    return {"detail": "Coordinador eliminado"}
