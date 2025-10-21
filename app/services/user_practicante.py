# app/services/user_practicante_service.py
from sqlalchemy.orm import Session
from app.db.models.user_practicante import UserPracticante
from app.schemas.user_practicante import UserPracticanteCreate, UserPracticanteUpdate
from typing import List, Optional
from app.db.models.enums import mesaTrabajoEnum

# 🔹 Crear usuario con contraseña hasheada
def create_user_practicante(db: Session, payload: UserPracticanteCreate) -> UserPracticante:
    if not payload.mesa_trabajo:
        raise ValueError("El campo 'mesa_trabajo' es obligatorio")
    
    db_user = UserPracticante(
        nombre=payload.nombre,
        mesa_trabajo=mesaTrabajoEnum(payload.mesa_trabajo),
    )
    db_user.set_password(payload.contrasena)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# 🔹 Listar todos los practicantes
def get_user_practicantes(db: Session, skip: int = 0, limit: int = 100) -> List[UserPracticante]:
    return db.query(UserPracticante).offset(skip).limit(limit).all()

# 🔹 Obtener practicante por ID
def get_user_practicante_by_id(db: Session, user_id: int) -> Optional[UserPracticante]:
    return db.query(UserPracticante).filter(UserPracticante.user_id == user_id).first()

# 🔹 Actualizar usuario con contraseña opcional
def update_user_practicante(db: Session, user_id: int, payload: UserPracticanteUpdate) -> Optional[UserPracticante]:
    db_user = get_user_practicante_by_id(db, user_id)
    if not db_user:
        return None

    data = payload.dict(exclude_unset=True)  # solo actualizar campos enviados

    # 🔹 Si se actualiza contraseña
    if "contrasena" in data and data["contrasena"]:
        db_user.set_password(data.pop("contrasena"))

    # 🔹 Si se actualiza mesa_trabajo, cast al Enum
    if "mesa_trabajo" in data and data["mesa_trabajo"]:
        data["mesa_trabajo"] = mesaTrabajoEnum(data["mesa_trabajo"])

    # 🔹 Actualizar los demás campos
    for key, value in data.items():
        setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user

# 🔹 Eliminar usuario
def delete_user_practicante(db: Session, user_id: int) -> bool:
    db_user = get_user_practicante_by_id(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
