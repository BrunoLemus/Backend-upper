# app/api/routes/user_practicante.py
from fastapi import APIRouter, Depends, HTTPException, Form, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.db.models.enums import mesaTrabajoEnum
from app.db.database import get_db
from app.db.models.user_practicante import UserPracticante
from app.schemas.user_practicante import (
    UserPracticanteCreate,
    UserPracticanteResponse,
    UserPracticanteUpdate
)
from app.core.security import create_access_token, verify_password, SECRET_KEY, ALGORITHM

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------
# Obtener practicante actual
# ---------------------------
def get_current_practicante(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")
        username = payload.get("sub")
        tipo = payload.get("tipo")
        sede = payload.get("sede")
        if not user_id or not username or tipo != "practicante" or not sede:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = db.query(UserPracticante).filter(UserPracticante.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ---------------------------
# Endpoints Practicante
# ---------------------------

# Crear practicante
@router.post("/", response_model=UserPracticanteResponse)
def create_practicante(payload: UserPracticanteCreate, db: Session = Depends(get_db)):
    # Verificar si ya existe usuario con mismo nombre
    existing_user = db.query(UserPracticante).filter(UserPracticante.nombre == payload.nombre).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    hashed_password = pwd_context.hash(payload.contrasena)
    user = UserPracticante(
        nombre=payload.nombre,
        contrasena=hashed_password,
        mesa_trabajo=mesaTrabajoEnum(payload.mesa_trabajo)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# Login practicante
@router.post("/login")
def login_practicante(
    nombre: str = Form(...),
    contrasena: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(UserPracticante).filter(UserPracticante.nombre == nombre).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    if not verify_password(contrasena, user.contrasena):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token_data = {
        "id": user.id,
        "sub": user.nombre,
        "tipo": "practicante",
        "sede": "guadalajara"
    }
    token = create_access_token(token_data)
    return{
        "id": user.id,
        "nombre": user.nombre,
        "sede": "guadalajara",
        "token": token
    }

# Ver perfil practicante
@router.get("/me", response_model=UserPracticanteResponse)
def read_practicante_me(current_user: UserPracticante = Depends(get_current_practicante)):
    return current_user

#editar practicante
@router.put("/{practicante_id}")
def update_practicante(practicante_id: int, payload: UserPracticanteUpdate, db: Session = Depends(get_db)):
    # Buscar practicante existente
    user = db.query(UserPracticante).filter(UserPracticante.id == practicante_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar nombre si se envía
    if payload.nombre is not None:
        user.nombre = payload.nombre

    # Actualizar mesa_trabajo (validar Enum)
    if payload.mesa_trabajo is not None:
        try:
            user.mesa_trabajo = mesaTrabajoEnum(payload.mesa_trabajo)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Valor inválido para mesa_trabajo. Debe ser uno de: MESA1, MESA2, ..., MESA10."
            )

    # Actualizar contraseña si se envía
    if payload.contrasena is not None:
        user.contrasena = pwd_context.hash(payload.contrasena)

    db.commit()
    db.refresh(user)

    return {"detail": "Usuario actualizado correctamente", "usuario": user}


# Actualizar perfil
@router.put("/perfil", response_model=UserPracticanteResponse)
def update_practicante_profile(
    payload: UserPracticanteUpdate,
    current_user: UserPracticante = Depends(get_current_practicante),
    db: Session = Depends(get_db)
):
    if payload.nombre:
        current_user.nombre = payload.nombre
    if payload.contrasena:
        current_user.contrasena = pwd_context.hash(payload.contrasena)
    if payload.sede:
        current_user.sede = payload.sede

    db.commit()
    db.refresh(current_user)
    return current_user


# Obtener todos los practicantes
@router.get("/", response_model=List[UserPracticanteResponse])
def get_practicantes(db: Session = Depends(get_db)):
    users = db.query(UserPracticante).all()
    return users


# Eliminar practicante
@router.delete("/{practicante_id}")
def delete_practicante(practicante_id: int, db: Session = Depends(get_db)):
    user = db.query(UserPracticante).filter(UserPracticante.id == practicante_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(user)
    db.commit()
    return {"detail": "Usuario eliminado"}
