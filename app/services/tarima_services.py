# app/services/tarima_services.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.models.tarima import Tarima
from app.schemas.tarima import TarimaCreate
from app.db.models.user_coordinador import UserCoordinador
from app.db.models.user_practicante import UserPracticante



def create_tarima(db: Session, payload: TarimaCreate, current_user) -> Tarima:
    """
    Crea una tarima y asigna coordinador o practicante según el rol del usuario logueado.
    current_user: objeto UserCoordinador o UserPracticante
    """
    db_tarima = Tarima(
        numero_facturas=payload.numero_facturas,
        numero_tarimas=payload.numero_tarimas,
        tipo_embalaje=payload.tipo_embalaje,
        paqueteria=payload.paqueteria,
        clave_producto=payload.clave_producto,
        cantidad_piezas=payload.cantidad_piezas or 0,
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
    db.add(db_tarima)
    db.commit()
    db.refresh(db_tarima)
    return db_tarima

def get_tarimas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    paqueteria: Optional[str] = None,
    numero_facturas: Optional[str] = None,
    current_user=None
) -> List[Tarima]:
    """
    Lista tarimas, opcionalmente filtradas por paquetería, factura o usuario logueado.
    current_user: objeto UserCoordinador o UserPracticante
    """
    query = db.query(Tarima)

    if paqueteria:
        query = query.filter(Tarima.paqueteria == paqueteria)
    if numero_facturas:
        query = query.filter(Tarima.numero_facturas == numero_facturas)

    # Filtrar por rol si se pasa current_user
    if current_user:
        if isinstance(current_user, UserCoordinador):
            query = query.filter(Tarima.coordinador_id == current_user.id)
        elif isinstance(current_user, UserPracticante):
            query = query.filter(Tarima.practicante_id == current_user.id)

    return query.offset(skip).limit(limit).all()

# Actualizar Tarima
def update_tarima(db: Session, tarima_id: int, payload: dict) -> Optional[Tarima]:
    """
    Actualiza una tarima existente.
    """
    db_tarima = db.query(Tarima).filter(Tarima.id == tarima_id).first()
    if not db_tarima:
        return None

    for key, value in payload.items():
        setattr(db_tarima, key, value)

    db.commit()
    db.refresh(db_tarima)
    return db_tarima


def get_tarima_by_id(db: Session, tarima_id: int) -> Optional[Tarima]:
    """
    Obtiene una tarima por su ID.
    """
    return db.query(Tarima).filter(Tarima.id == tarima_id).first()