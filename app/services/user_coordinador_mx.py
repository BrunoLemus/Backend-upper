from sqlalchemy.orm import Session
from app.db.models.user_coordinador_mx import UserCoordinadorMX
from app.schemas.user_coordinador_mx import UserCoordinadorMXCreate, UserCoordinadorMXUpdate
from typing import List, Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_CODE = "UPPER"  # Cambia por tu código real

# -----------------------------
# CREAR COORDINADOR MX
# -----------------------------
def create_user_coordinador_mx(db: Session, payload: UserCoordinadorMXCreate) -> UserCoordinadorMX:
    if payload.codigo_secreto != SECRET_CODE:
        raise ValueError("Código secreto incorrecto")
    
    hashed_password = pwd_context.hash(payload.contrasena)
    db_user = UserCoordinadorMX(
        nombre=payload.nombre,
        contrasena=hashed_password,
        codigo_secreto=payload.codigo_secreto
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# -----------------------------
# OBTENER TODOS LOS COORDINADORES MX
# -----------------------------
def get_user_coordinadores_mx(db: Session, skip: int = 0, limit: int = 100) -> List[UserCoordinadorMX]:
    return db.query(UserCoordinadorMX).offset(skip).limit(limit).all()

# -----------------------------
# OBTENER COORDINADOR MX POR ID
# -----------------------------
def get_user_coordinador_mx_by_id(db: Session, id: int) -> Optional[UserCoordinadorMX]:
    return db.query(UserCoordinadorMX).filter(UserCoordinadorMX.id == id).first()

# -----------------------------
# ACTUALIZAR COORDINADOR MX
# -----------------------------
def update_user_coordinador_mx(db: Session, id: int, payload: UserCoordinadorMXUpdate) -> Optional[UserCoordinadorMX]:
    db_user = get_user_coordinador_mx_by_id(db, id)
    if not db_user:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "contrasena" and value is not None:
            value = pwd_context.hash(value)
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

# -----------------------------
# ELIMINAR COORDINADOR MX
# -----------------------------
def delete_user_coordinador_mx(db: Session, id: int) -> bool:
    db_user = get_user_coordinador_mx_by_id(db, id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
