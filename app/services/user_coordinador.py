from sqlalchemy.orm import Session
from app.db.models.user_coordinador import UserCoordinador
from app.schemas.user_coordinador import UserCoordinadorCreate, UserCoordinadorUpdate
from typing import List, Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_CODE = "UPPER"  # Cambia por tu código real

# -----------------------------
# CREAR COORDINADOR
# -----------------------------
def create_user_coordinador(db: Session, payload: UserCoordinadorCreate) -> UserCoordinador:
    if payload.codigo_secreto != SECRET_CODE:
        raise ValueError("Código secreto incorrecto")
    
    hashed_password = pwd_context.hash(payload.contraseña)
    db_user = UserCoordinador(
        
        nombre=payload.nombre,
        contraseña=hashed_password,
        codigo_secreto=payload.codigo_secreto
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# -----------------------------
# OBTENER TODOS LOS COORDINADORES
# -----------------------------
def get_user_coordinadores(db: Session, skip: int = 0, limit: int = 100) -> List[UserCoordinador]:
    return db.query(UserCoordinador).offset(skip).limit(limit).all()

# -----------------------------
# OBTENER COORDINADOR POR ID
# -----------------------------
def get_user_coordinador_by_id(db: Session, id: int) -> Optional[UserCoordinador]:
    return db.query(UserCoordinador).filter(UserCoordinador.id == id).first()

# -----------------------------
# ACTUALIZAR COORDINADOR
# -----------------------------
def update_user_coordinador(db: Session, id: int, payload: UserCoordinadorUpdate) -> Optional[UserCoordinador]:
    db_user = get_user_coordinador_by_id(db, id)
    if not db_user:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "contraseña":
            value = pwd_context.hash(value)
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

# -----------------------------
# ELIMINAR COORDINADOR
# -----------------------------
def delete_user_coordinador(db: Session, id: int) -> bool:
    db_user = get_user_coordinador_by_id(db, id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
