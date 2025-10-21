from sqlalchemy.orm import Session
from app.db.models.caja_mx import CajaMX
from app.schemas.caja_mx import CajaMXCreate
from typing import List, Optional
from app.db.models.user_coordinador_mx import UserCoordinadorMX
from app.db.models.user_practicante_mx import UserPracticanteMX


def create_caja_mx(db: Session, payload: CajaMXCreate, current_user) -> CajaMX:
    """
    Crea una caja MX y asigna coordinador o practicante según el rol del usuario logueado.
    current_user: objeto UserCoordinadorMX o UserPracticanteMX
    """
    db_caja = CajaMX(
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
        nombre_user_coordinador=current_user.nombre if isinstance(current_user, UserCoordinadorMX) else None,
        nombre_user_practicante=current_user.nombre if isinstance(current_user, UserPracticanteMX) else None,
        coordinador_id=current_user.id if isinstance(current_user, UserCoordinadorMX) else None,
        practicante_id=current_user.id if isinstance(current_user, UserPracticanteMX) else None,
    )
    db.add(db_caja)
    db.commit()
    db.refresh(db_caja)
    return db_caja


def get_cajas_mx(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    paqueteria: Optional[str] = None,
    n_facturas: Optional[str] = None,
    current_user=None
) -> List[CajaMX]:
    """
    Lista cajas MX, opcionalmente filtradas por paquetería, factura o usuario logueado.
    current_user: objeto UserCoordinadorMX o UserPracticanteMX
    """
    query = db.query(CajaMX)

    if paqueteria:
        query = query.filter(CajaMX.paqueteria == paqueteria)
    if n_facturas:
        query = query.filter(CajaMX.n_facturas == n_facturas)

    # Filtrar por rol si se pasa current_user
    if current_user:
        if isinstance(current_user, UserCoordinadorMX):
            query = query.filter(CajaMX.coordinador_id == current_user.id)
        elif isinstance(current_user, UserPracticanteMX):
            query = query.filter(CajaMX.practicante_id == current_user.id)

    return query.offset(skip).limit(limit).all()


def get_caja_mx_by_id(db: Session, caja_id: int) -> Optional[CajaMX]:
    return db.query(CajaMX).filter(CajaMX.id == caja_id).first()


def update_caja_mx(db: Session, caja_id: int, update_data: dict) -> Optional[CajaMX]:
    db_caja = db.query(CajaMX).filter(CajaMX.id == caja_id).first()
    if not db_caja:
        return None

    # Solo permitir actualizar estos campos
    campos_permitidos = ["n_facturas", "paqueteria", "cantidad_piezas", "clave_producto", "t_embalaje"]

    for key, value in update_data.items():
        if key in campos_permitidos and hasattr(db_caja, key):
            setattr(db_caja, key, value)

    db.commit()
    db.refresh(db_caja)
    return db_caja


def delete_caja_mx(db: Session, caja_id: int) -> bool:
    db_caja = db.query(CajaMX).filter(CajaMX.id == caja_id).first()
    if not db_caja:
        return False
    db.delete(db_caja)
    db.commit()
    return True
