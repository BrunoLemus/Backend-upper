# app/services/caja_service.py
from sqlalchemy.orm import Session
from app.db.models.caja import Caja
from app.schemas.caja import CajaCreate
from typing import List, Optional
from app.db.models.user_coordinador import UserCoordinador
from app.db.models.user_practicante import UserPracticante


def create_caja(db: Session, payload: CajaCreate, current_user) -> Caja:
    """
    Crea una caja y asigna coordinador o practicante según el rol del usuario logueado.
    current_user: objeto UserCoordinador o UserPracticante
    """
    db_caja = Caja(
        paqueteria=payload.paqueteria,
        n_facturas=payload.n_facturas,
        t_embalaje=payload.t_embalaje,
        n_cajas=payload.n_cajas,
        cantidad_piezas=payload.cantidad_piezas,
        clave_producto=payload.clave_producto,
        ancho=payload.ancho or 0,
        alto=payload.alto or 0,
        largo=payload.largo or 0,
        peso=payload.peso or 0,
        peso_volumetrico=payload.peso_volumetrico or None,
        nombre_user_coordinador=current_user.nombre if isinstance(current_user, UserCoordinador) else None,
        nombre_user_practicante=current_user.nombre if isinstance(current_user, UserPracticante) else None,
        coordinador_id=current_user.id if isinstance(current_user, UserCoordinador) else None,
        practicante_id=current_user.id if isinstance(current_user, UserPracticante) else None,
    )
    db.add(db_caja)
    db.commit()
    db.refresh(db_caja)
    return db_caja


def get_cajas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    paqueteria: Optional[str] = None,
    n_facturas: Optional[str] = None,
    current_user=None
) -> List[Caja]:
    """
    Lista cajas, opcionalmente filtradas por paquetería, factura o usuario logueado.
    current_user: objeto UserCoordinador o UserPracticante
    """
    query = db.query(Caja)

    if paqueteria:
        query = query.filter(Caja.paqueteria == paqueteria)
    if n_facturas:
        query = query.filter(Caja.n_facturas == n_facturas)

    # Filtrar por rol si se pasa current_user
    if current_user:
        if isinstance(current_user, UserCoordinador):
            query = query.filter(Caja.coordinador_id == current_user.id)
        elif isinstance(current_user, UserPracticante):
            query = query.filter(Caja.practicante_id == current_user.id)

    return query.offset(skip).limit(limit).all()


def get_caja_by_id(db: Session, caja_id: int) -> Optional[Caja]:
    return db.query(Caja).filter(Caja.id == caja_id).first()


def update_caja(db: Session, caja_id: int, update_data: dict) -> Optional[Caja]:
    db_caja = db.query(Caja).filter(Caja.id == caja_id).first()
    if not db_caja:
        return None

    # Solo permitir actualizar estos campos
    campos_permitidos = ["numero_factura", "paqueteria", "cantidad_piezas", "clave_producto", "tipo_embalaje"]

    for key, value in update_data.items():
        if key in campos_permitidos and hasattr(db_caja, key):
            setattr(db_caja, key, value)

    db.commit()
    db.refresh(db_caja)
    return db_caja



def delete_caja(db: Session, caja_id: int) -> bool:
    db_caja = db.query(Caja).filter(Caja.id == caja_id).first()
    if not db_caja:
        return False
    db.delete(db_caja)
    db.commit()
    return True
