from sqlalchemy.orm import Session
from app.db.models.user_practicante_mx import UserPracticanteMX
from app.schemas.user_practicante_mx import UserPracticanteMXCreate, UserPracticanteMXUpdate
from typing import List, Optional
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Crear practicante
def create_user_practicante_mx(db: Session, payload: UserPracticanteMXCreate) -> UserPracticanteMX:
    user = UserPracticanteMX(nombre=payload.nombre, mesa_trabajo=payload.mesa_trabajo)
    user.set_password(payload.contrasena)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Obtener todos
def get_user_practicantes_mx(db: Session, skip: int = 0, limit: int = 100) -> List[UserPracticanteMX]:
    return db.query(UserPracticanteMX).offset(skip).limit(limit).all()

# Obtener por ID
def get_user_practicante_mx_by_id(db: Session, id: int) -> Optional[UserPracticanteMX]:
    return db.query(UserPracticanteMX).filter(UserPracticanteMX.id == id).first()

# Actualizar
def update_user_practicante_mx(db: Session, id: int, payload: UserPracticanteMXUpdate) -> Optional[UserPracticanteMX]:
    user = get_user_practicante_mx_by_id(db, id)
    if not user:
        return None
    if payload.nombre:
        user.nombre = payload.nombre
    if payload.contrasena:
        user.set_password(payload.contrasena)
    if payload.mesa_trabajo:
        user.mesa_trabajo = payload.mesa_trabajo
    db.commit()
    db.refresh(user)
    return user

# Eliminar
def delete_user_practicante_mx(db: Session, id: int) -> bool:
    user = get_user_practicante_mx_by_id(db, id)
    if not user:
        return False
    db.delete(user)
    db.commit()
    return True
